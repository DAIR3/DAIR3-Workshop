# Flaws of Others (FOO) — Multi-Agent Chat Workshop

A teaching suite of Qt-based chat interfaces that let you converse with a single LLM or watch several LLMs critique and refine each other's work. Built for the NIH R25 *DAIR3* workshop on AI-assisted grant writing and review.

There are two ways to use this folder:

- **Single-agent GUIs** ([apps/agentClaude.py](apps/agentClaude.py), [apps/agentGPTGUI.py](apps/agentGPTGUI.py), [apps/agentGoogleGUI.py](apps/agentGoogleGUI.py)): one chat window, one model, one persona.
- **Multi-agent FOO GUI** ([apps/foo_gui.py](apps/foo_gui.py)): one tabbed window with several agents at once, plus the FOO workflow (Vulnerability → Judgment → Reflection) for collaborative critique.

### Folder layout

```
FOO/
├── README.md, requirements.txt
├── config.json, providers.json         data files, loaded at startup
├── dual_agent_dependencies.sh          installer for grant_review_v2.py extras (section 4)
│
├── apps/                               user-facing entry points (run from FOO root)
│   ├── foo_gui.py                      multi-agent GUI
│   ├── agentClaude.py / agentGPTGUI.py / agentGoogleGUI.py
│   ├── single_agent_gui.py             shared implementation for the three above
│   ├── widgets_common.py               shared Qt widgets
│   ├── editJSON.py                     standalone JSON tree editor
│   └── _bootstrap.py                   sys.path shim, imported by every entry script
│
├── classes/                            non-GUI engine + support modules
│   ├── cls_anthropic.py, cls_openai.py, cls_google.py, cls_ollama.py
│   ├── cls_blockchain.py, cls_foo.py
│   ├── cls_provider_catalog.py, cls_rag.py, cls_file_router.py
│   ├── md_loader.py, md_widget.py
│   └── file_loader.py, file_upload_worker.py
│
├── agents/                             persona markdown (common.md + 9 roles)
├── chats/                              per-agent conversation history (created at runtime)
├── knowledge/                          per-agent RAG sources and index
├── prototypes/                         older / one-off scripts kept for reference
└── fine_tune_demos/                    self-contained fine-tuning demos
```

All apps are launched from this folder so that `config.json` / `providers.json` resolve. See section 4.

---

## 1. Prerequisites

- **Python 3.10+** (tested with 3.11).
- **PyQt5** (5.15.x).
- The vendor SDKs you intend to use (one or more):
  - `openai` 2.5+
  - `anthropic` 0.71+
  - `google-genai` 2.1+

Everything is captured in `requirements.txt`. From the folder containing this file:

```bash
pip install -r requirements.txt
```

If you want a clean install (recommended on a fresh machine), create a virtual environment first:

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS / Linux:
source .venv/bin/activate
pip install -r requirements.txt
```

---

## 2. API keys

Set the keys for the providers you plan to use. Unset keys just disable that provider — the other apps still work.

| Provider | Environment variable | Used by |
|---|---|---|
| OpenAI | `OPENAI_API_KEY` | `apps/agentGPTGUI.py`, `apps/foo_gui.py` (any `gpt-*` / `o*` model) |
| Anthropic | `ANTHROPIC_API_KEY` | `apps/agentClaude.py`, `apps/foo_gui.py` (any `claude-*` model) |
| Google | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `apps/agentGoogleGUI.py`, `apps/foo_gui.py` (any `gemini-*` model) |

**Windows (cmd):**
```
setx OPENAI_API_KEY "sk-..."
setx ANTHROPIC_API_KEY "sk-ant-..."
setx GEMINI_API_KEY "AIza..."
```
(Open a new terminal after `setx` for the variable to take effect.)

**macOS / Linux:**
```bash
export OPENAI_API_KEY="sk-..."
export ANTHROPIC_API_KEY="sk-ant-..."
export GEMINI_API_KEY="AIza..."
```
Add the `export` lines to `~/.bashrc` / `~/.zshrc` to make them permanent.

---

## 3. Configuration

### `config.json`

Top-level shape:

```json
{
  "CONFIG": {
    "common_md": "common.md",
    "model": "gpt-5.5",
    "claude_model": "claude-opus-4-7",
    "name": "Tobby",
    "user": "Dr. G",
    "fontsize": 12,
    "blockchain_salt": "..."
  },
  "MODELS": [ /* one entry per agent in the multi-agent GUI */ ]
}
```

- `common_md` — markdown file with shared persona conventions ([agents/common.md](agents/common.md)) prepended to every agent's role. Bare filenames like `"common.md"` are resolved against `agents/` automatically.
- `model` — default OpenAI model used by `apps/agentGPTGUI.py`.
- `claude_model` — default Anthropic model used by `apps/agentClaude.py`.
- `google_model` (optional) — default Google model used by `apps/agentGoogleGUI.py`.
- `name`, `user` — substituted into `{name}` and `{user}` placeholders inside all `.md` files.
- `fontsize` — starting font size for every widget; the `[-]` / `[+]` buttons adjust at runtime.

Each entry in `MODELS` (used by [apps/foo_gui.py](apps/foo_gui.py)) has:

```json
{
  "model_code": "claude-opus-4-7",
  "model_name": "Anthropic Claude Opus 4.7",
  "agent_name": "Claudius",
  "instructions_file": "researcher.md",
  "harmonizer": "false",
  "harmonizer_directive_file": "",
  "temperature": 0.1
}
```

- `model_code` — the exact ID sent to the API. Engine is auto-detected: starts with `claude` → Anthropic, `gemini` → Google, anything else → OpenAI.
- `instructions_file` — role markdown for this agent. Combined with `common_md`, with `{user}`/`{name}` substituted in.
- `harmonizer: "true"` — marks this agent as a harmonizer (used in the Judgment phase of the FOO workflow).
- `harmonizer_directive_file` — markdown read at Judgment time. `{source_agent_name}` is substituted in then.

### Persona markdown files

Each `.md` file in [agents/](agents/) is a *role*. The dropdown in every GUI lists them all (except `common.md`, which is the shared header).

| File | Persona |
|---|---|
| [agents/general.md](agents/general.md) | Generic critical-thinking assistant |
| [agents/researcher.md](agents/researcher.md) | Scientific researcher; rigor, evidence, FAIR data |
| [agents/grant_reviewer_NIH.md](agents/grant_reviewer_NIH.md) | NIH study-section reviewer (5 criteria, 9-point scoring) |
| [agents/grant_reviewer_NSF.md](agents/grant_reviewer_NSF.md) | NSF panel reviewer (Intellectual Merit / Broader Impacts) |
| [agents/grant_writer_NIH.md](agents/grant_writer_NIH.md) | NIH grant writer (Specific Aims, rigor & reproducibility, SABV) |
| [agents/grant_writer_NSF.md](agents/grant_writer_NSF.md) | NSF proposal writer (DMP, Mentoring Plan, IM/BI articulation) |
| [agents/article_writer.md](agents/article_writer.md) | Scientific manuscript writer (IMRaD, EQUATOR guidelines) |
| [agents/article_reviewer.md](agents/article_reviewer.md) | Peer reviewer (review structure, ethics, methodological red flags) |
| [agents/harmonizer.md](agents/harmonizer.md) | Judgment-phase directive for the FOO workflow |

To create a new persona, copy any existing role file in `agents/`, edit it, and save with a new name — it will appear in the dropdown next time you start a GUI. Variables you can use anywhere in the file: `{user}`, `{name}`, and (for harmonizer directives only) `{source_agent_name}`.

---

## 4. Running the apps

You can launch from anywhere — either `python apps/foo_gui.py` from the FOO root, or `cd apps && python foo_gui.py`. The first project import in every entry script is [apps/_bootstrap.py](apps/_bootstrap.py), which (1) inserts `classes/` and `apps/` into `sys.path`, and (2) `chdir`'s into the FOO root so that relative-path file loads (`config.json`, `providers.json`, the `chats/` folder named by `CONFIG.CWD`) all resolve.

### Single-agent GUIs

Each takes an optional positional argument: the role markdown to load. The default is `general.md` (resolved against `agents/`).

```bash
python apps/agentClaude.py                       # default: general.md
python apps/agentClaude.py researcher.md
python apps/agentClaude.py grant_writer_NIH.md

python apps/agentGPTGUI.py article_reviewer.md
python apps/agentGoogleGUI.py grant_reviewer_NSF.md
```

Once running, you can switch roles live via the dropdown in the top-left of the window — the conversation is reset when the role changes.

### Multi-agent FOO GUI

```bash
python apps/foo_gui.py
python apps/foo_gui.py --reset      # or -r: wipe agent history before starting
```

Creates one tab per agent listed in `MODELS`. Type into the **broadcast** box at the bottom to send a message to every active agent. Each tab's `Vulnerability` / `Judgment` / `Reflection` buttons drive the three FOO phases.

**`--reset` / `-r` flag.** On startup, each agent normally loads its saved history from `chats/<AgentName>.json` and replays the full transcript to the model as a single priming turn so the conversation resumes with prior context. For long conversations this can take many seconds per agent on the main thread and the GUI will appear stuck while the API call is in flight. Passing `--reset` deletes those JSON files *before* the orchestrator initializes, so each agent starts fresh and the GUI comes up immediately. Equivalent to the in-app **Reset** button, but without the confirmation dialog and without needing the GUI to be responsive first.

### Standalone JSON editor

```bash
python apps/editJSON.py
```

Opens a tree-view JSON editor (file is chosen via the open dialog). Useful for hand-editing `chats/<Agent>.json` history files when something goes wrong without having to re-run an agent.

### `dual_agent_dependencies.sh`

A bash installer that adds the third-party packages required by `prototypes/grant_review_v2.py` (a multi-modal dual-agent demo not bundled with the surviving FOO apps). Run it only if you intend to bring that prototype back into use. Has no effect on `apps/foo_gui.py` or the single-agent GUIs — their requirements live in [requirements.txt](requirements.txt).

---

## 5. Features available in every GUI

| Feature | How |
|---|---|
| **Markdown rendering** | Every response is rendered via `QTextEdit.setMarkdown()` (headings, bold, lists, code blocks). Source: [classes/md_widget.py](classes/md_widget.py). |
| **Role dropdown** | Top-left of each chat window / tab. Pick any `.md` file in [agents/](agents/) to swap personas; conversation resets. |
| **Font controls** | `[-]` and `[+]` buttons in the top-right scale every widget. Initial size from `fontsize` in `config.json`. |
| **Drag-and-drop files** | Drop a file onto any chat window. Text files (including `.ipynb` — outputs are stripped so only cell sources are sent) are inlined; images and PDFs go via each engine's *native* upload (base64 content block for OpenAI / Anthropic, Files API for Gemini) so layout and embedded images are preserved. In `apps/foo_gui.py`, a drop broadcasts to every active tab. See [classes/file_loader.py](classes/file_loader.py). |
| **Upload progress** | An indeterminate progress bar + live status label (`Reading…`, `Base64-encoding…`, `Sending to <provider>…`) shows during uploads. Token counts (`in: 1234 / out: 256`) are reported when the API returns them. Source: [classes/file_upload_worker.py](classes/file_upload_worker.py). |
| **Session header** | Each window prints model name, model code, provider, load timestamp, agent name, and role at startup (and again whenever the role changes). |

### Supported file types on drop

- **Text** (inlined as user message): `.txt`, `.md`, `.csv`, `.tsv`, `.json`, `.yaml`/`.yml`, `.log`, `.tex`, `.bib`, source code (`.py`, `.r`, `.js`, etc.), HTML/XML, SQL, …
- **Images** (native): `.jpg`/`.jpeg`, `.png`, `.gif`, `.webp`.
- **PDFs** (native): `.pdf`.

Anything else returns an "Unsupported file type" message.

---

## 6. Files reference (short)

### `apps/` — user-facing entry points

| File | What it is |
|---|---|
| [apps/foo_gui.py](apps/foo_gui.py) | Multi-agent FOO GUI (tabs, broadcast, FOO workflow). `--reset` wipes history at startup. |
| [apps/agentClaude.py](apps/agentClaude.py) | Single-Anthropic GUI. CLI: `python apps/agentClaude.py [role.md]`. |
| [apps/agentGPTGUI.py](apps/agentGPTGUI.py) | Single-OpenAI GUI. CLI: `python apps/agentGPTGUI.py [role.md]`. |
| [apps/agentGoogleGUI.py](apps/agentGoogleGUI.py) | Single-Gemini GUI. CLI: `python apps/agentGoogleGUI.py [role.md]`. |
| [apps/single_agent_gui.py](apps/single_agent_gui.py) | Shared implementation behind the three single-agent entry scripts above. |
| [apps/widgets_common.py](apps/widgets_common.py) | Shared Qt widgets (`ProviderModelSelector`, `RAGSettingsDialog`). |
| [apps/editJSON.py](apps/editJSON.py) | Standalone tree-view JSON editor — open any JSON file (e.g. a `chats/<Agent>.json` history) and edit values inline. |
| [apps/_bootstrap.py](apps/_bootstrap.py) | Path shim imported by every entry script; inserts `classes/` and `apps/` into `sys.path`. |

### `classes/` — engine adapters and support modules

| File | What it is |
|---|---|
| [classes/cls_foo.py](classes/cls_foo.py) | `MultiAgentOrchestrator` — loads agents, runs Vulnerability/Judgment/Reflection. |
| [classes/cls_openai.py](classes/cls_openai.py), [classes/cls_anthropic.py](classes/cls_anthropic.py), [classes/cls_google.py](classes/cls_google.py), [classes/cls_ollama.py](classes/cls_ollama.py) | Engine-specific agent classes (chat, history, file upload). |
| [classes/cls_provider_catalog.py](classes/cls_provider_catalog.py) | Reads `providers.json` and resolves model codes → engine class. |
| [classes/cls_rag.py](classes/cls_rag.py) | Per-agent `KnowledgeBase`, retrieval, citation rendering. Stores under `knowledge/<agent>/`. |
| [classes/cls_file_router.py](classes/cls_file_router.py) | Decides whether a dropped file goes to chat context or into the RAG index. |
| [classes/cls_blockchain.py](classes/cls_blockchain.py) | No-op `IntegrityManager` stub. (The real blockchain-integrity module is not bundled.) |
| [classes/md_widget.py](classes/md_widget.py) | `MarkdownTextEdit` — `QTextEdit` subclass that re-renders via `setMarkdown()` on each append. |
| [classes/md_loader.py](classes/md_loader.py) | `load_persona()` + `read_md_file()` — compose `common.md` + role file, substitute variables. Bare filenames fall back to `agents/`. |
| [classes/file_loader.py](classes/file_loader.py) | `classify_file()` + `read_text()` (Jupyter-aware) + `read_base64()` — drag-and-drop helpers. |
| [classes/file_upload_worker.py](classes/file_upload_worker.py) | `FileUploadWorker(QThread)` + `format_usage()` — keeps uploads off the GUI thread, formats token counts. |

### Configuration & content

| File | What it is |
|---|---|
| [config.json](config.json) | Models, roles, and runtime settings. Loaded by literal `"config.json"` from the FOO root. |
| [providers.json](providers.json) | Provider/model catalog read by `cls_provider_catalog.py`. |
| [requirements.txt](requirements.txt) | Pip dependencies for `apps/` + `classes/`. |
| [agents/](agents/) | 10 persona definition files — see table in section 3. |
| [chats/](chats/) | Per-agent conversation history (`<AgentName>.json`), created at runtime. |
| [knowledge/](knowledge/) | Per-agent RAG sources + index. |

### Other folders

| Folder | What it is |
|---|---|
| [prototypes/](prototypes/) | Earlier / one-off scripts kept for reference (`Agent.py`, `ClaudeChatUL.py`, `ClaudeGUI.py`, `ClaudeQA.py`, `ClaudeUUID.py`, `editJSON.py` *(older twin)*, `generateSummaries.py`, `grant_review.py`, `multillm.py`, `agentGroq.py`, CLI-only `agentGPT.py` / `agentGoogle.py`). Not imported by anything in `apps/` or `classes/`. |
| [fine_tune_demos/](fine_tune_demos/) | Self-contained fine-tuning demos (NIH voice transfer, bibliography reformatter). |

---

## 7. Troubleshooting

**`'ascii' codec can't encode character '’' …` on OpenAI calls.**
Means a string with a non-ASCII character (smart quote, em dash) is reaching an HTTP header. Most often a stray smart quote in an environment variable. Check `OPENAI_API_KEY`, `OPENAI_ORGANIZATION`, `OPENAI_PROJECT`, `OPENAI_BASE_URL` for any pasted-from-document characters.

**`temperature is deprecated for this model` (Anthropic).**
Already handled — `_temperature_kwarg()` in [classes/cls_anthropic.py](classes/cls_anthropic.py) omits the parameter for models in `_TEMPERATURE_DEPRECATED_PREFIXES`. If a new model deprecates it, add its prefix to that tuple.

**"Pylance can't resolve `openai` / `anthropic` …" in VS Code, but `pip show` confirms they're installed.**
Wrong interpreter selected in VS Code. `Cmd/Ctrl+Shift+P` → `Python: Select Interpreter`, pick the one matching `which python` in your activated venv, then `Developer: Reload Window`.

**`No config.json found in CWD: …` warning at startup.**
Old foo_gui.py message; the `CWD` mechanism still falls back to the local folder. To silence, ensure the `CWD` key is *not* in `config.json` (it is removed in the current build).

**The window appears to freeze during file uploads.**
Fixed — uploads now run on `FileUploadWorker` with a live progress bar. If you still see this, you're probably running an older copy of `apps/foo_gui.py`; re-pull.

**`apps/foo_gui.py` looks stuck after `Updated thread ID for <Agent>: …`.**
Not stuck — replaying a long saved conversation back to the model on startup. The replay runs synchronously per agent before the GUI is shown; with a multi-thousand-line history this can take 30–90 s per agent. Either wait it out, or relaunch with `python apps/foo_gui.py --reset` to discard the prior history and start fresh.

**`model_not_found` from OpenAI/Anthropic.**
The model ID in `config.json` doesn't exist on your account. Edit the `model_code` value (e.g. `gpt-5.5` → `gpt-5.1`, or pick whatever your dashboard lists).

**`Master config file not found: config.json` or a `FileNotFoundError` on startup.**
[apps/_bootstrap.py](apps/_bootstrap.py) normally `chdir`'s into the FOO root before any module touches the filesystem, so this should not happen. If it does, you likely imported a project module before `_bootstrap`. Always put `import _bootstrap` as the first project import in any new entry script.

---

## 8. License

Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
By Juan B. Gutiérrez, Professor of Mathematics, University of Texas at San Antonio.
