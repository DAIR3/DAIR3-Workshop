"""
cls_provider_catalog.py
Loader and query layer for providers.json.

providers.json is the authoritative catalog of available providers and models.
config.json holds only per-agent *selections* (cd_provider + cd_model). This
module joins the two: given a desired model code it returns the catalog entry,
and given a category filter it returns the dropdown population.

Schema (providers.json):

    {
      "models":   [ { cd_provider, cd_model, nm_display, ds_description,
                      cd_model_category, in_active, ...}, ... ],
      "providers": [ { cd_provider, ds_display_name, ds_base_url,
                       ds_api_key_env, in_active, ...}, ... ]
    }

Filters applied by ``available_providers_for_chat()``:
  - provider.in_active == True
  - api key env var is set (or provider is 'ollama' which needs no key)
  - at least one model under that provider passes the chat filter

Filters applied by ``models_for_provider()``:
  - model.in_active == True
  - model.cd_provider == requested provider
  - model.cd_model_category in {'chat', 'reasoning', 'coding'} (chat use)
    or whatever the caller asks via category_whitelist.

Backward compatibility: ``resolve_legacy_model(model_code)`` maps an old
``MODELS[*].model_code`` value (e.g. ``"claude-opus-4-7"``) to a (provider,
model) pair using the catalog. This lets old config.json files continue to
work without migration.

By Juan B. Gutiérrez, Professor of Mathematics
University of Texas at San Antonio.

License: Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0)
"""
import os
import json


CHAT_CATEGORIES = ("chat", "reasoning", "coding")
EMBEDDING_CATEGORIES = ("embedding",)

# Providers FOO currently has an engine class for. The catalog may list more
# (e.g. openrouter); they are filtered out of the GUI dropdowns until a class
# is added so the user never picks one and immediately hits a ValueError.
SUPPORTED_PROVIDERS = {"anthropic", "openai", "gemini", "ollama"}


def _here():
    return os.path.dirname(os.path.abspath(__file__))


def _project_root():
    # This module lives in <root>/classes/, so the project root is one up.
    return os.path.dirname(_here())


def load_catalog(path=None):
    """Load and return providers.json as a dict. Resolves to <root>/providers.json by default."""
    path = path or os.path.join(_project_root(), "providers.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def _index(catalog):
    """Return (providers_by_code, models_by_code) for fast lookup."""
    providers = {p["cd_provider"]: p for p in catalog.get("providers", [])}
    models = {}
    for m in catalog.get("models", []):
        models.setdefault(m["cd_provider"], []).append(m)
    return providers, models


def provider_has_key(provider_entry):
    """True if the provider needs no key, or its key env var is set."""
    env = provider_entry.get("ds_api_key_env")
    if not env:
        return True  # e.g. Ollama
    return bool(os.environ.get(env))


def available_providers_for_chat(catalog=None, category_whitelist=CHAT_CATEGORIES):
    """Providers that (a) are active, (b) have an API key (or need none),
    (c) have at least one active model in the requested categories.

    Returns a list of provider dicts, sorted by ds_display_name.
    """
    catalog = catalog or load_catalog()
    providers, models = _index(catalog)
    out = []
    for code, prov in providers.items():
        if code not in SUPPORTED_PROVIDERS:
            continue
        if not prov.get("in_active", True):
            continue
        if not provider_has_key(prov):
            continue
        usable = [
            m for m in models.get(code, [])
            if m.get("in_active", True)
            and m.get("cd_model_category") in category_whitelist
        ]
        if not usable:
            continue
        out.append(prov)
    return sorted(out, key=lambda p: p.get("ds_display_name", p["cd_provider"]))


def models_for_provider(provider_code, catalog=None, category_whitelist=CHAT_CATEGORIES):
    """All active models for one provider, filtered by category. Sorted by n_ordo then name."""
    catalog = catalog or load_catalog()
    _, models = _index(catalog)
    out = [
        m for m in models.get(provider_code, [])
        if m.get("in_active", True)
        and m.get("cd_model_category") in category_whitelist
    ]
    return sorted(out, key=lambda m: (m.get("n_ordo", 9999), m.get("nm_display", "")))


def embedding_models(catalog=None):
    """All active embedding models across providers."""
    catalog = catalog or load_catalog()
    out = [
        m for m in catalog.get("models", [])
        if m.get("in_active", True)
        and m.get("cd_model_category") in EMBEDDING_CATEGORIES
    ]
    return sorted(out, key=lambda m: (m.get("cd_provider", ""), m.get("n_ordo", 9999)))


def find_model(model_code, catalog=None):
    """Return the catalog entry for a model code, or None."""
    catalog = catalog or load_catalog()
    for m in catalog.get("models", []):
        if m.get("cd_model") == model_code:
            return m
    return None


def find_provider(provider_code, catalog=None):
    """Return the catalog entry for a provider code, or None."""
    catalog = catalog or load_catalog()
    for p in catalog.get("providers", []):
        if p.get("cd_provider") == provider_code:
            return p
    return None


def resolve_legacy_model(model_code, catalog=None):
    """Given a bare model id (the old config.json `model_code` field),
    return (provider_code, model_entry). Falls back to prefix-based
    detection if the model isn't in the catalog. Used by the migration
    shim so old configs keep working.
    """
    catalog = catalog or load_catalog()
    entry = find_model(model_code, catalog)
    if entry:
        return entry["cd_provider"], entry
    # Fall back to the legacy auto-detect rules.
    if model_code.startswith("claude"):
        return "anthropic", None
    if model_code.startswith("gemini"):
        return "gemini", None
    if model_code.startswith(("gpt-", "o3", "o1", "ft:")):
        return "openai", None
    if model_code.startswith(("llama", "mistral", "qwen", "phi", "gemma", "nomic")):
        return "ollama", None
    # Last resort.
    return "openai", None


def engine_class_for(provider_code):
    """Return the AgentClass for a provider code. Imports are deferred so a
    missing optional dependency only breaks that one provider.

    Raises ValueError on an unknown provider code.
    """
    if provider_code == "anthropic":
        from cls_anthropic import AnthropicAgent
        return AnthropicAgent
    if provider_code == "openai":
        from cls_openai import OpenAIAgent
        return OpenAIAgent
    if provider_code == "gemini":
        from cls_google import GoogleAgent
        return GoogleAgent
    if provider_code == "ollama":
        from cls_ollama import OllamaAgent
        return OllamaAgent
    raise ValueError(f"Unknown provider: {provider_code!r}")
