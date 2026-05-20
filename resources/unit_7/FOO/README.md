# Flaws of Others (FOO) — Multi-Agent Chat Workshop

A teaching suite of Qt-based chat interfaces that let you converse with a single LLM or watch several LLMs critique and refine each other's work. Built for the NIH R25 *DAIR3* workshop on AI-assisted grant writing and review.

There are two ways to use this folder:

- **Single-agent GUIs** (`agentClaude.py`, `agentGPTGUI.py`, `agentGoogleGUI.py`): one chat window, one model, one persona.
- **Multi-agent FOO GUI** (`foo_gui.py`): one tabbed window with several agents at once, plus the FOO workflow (Vulnerability → Judgment → Reflection) for collaborative critique.

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
| OpenAI | `OPENAI_API_KEY` | `agentGPTGUI.py`, `foo_gui.py` (any `gpt-*` / `o*` model) |
| Anthropic | `ANTHROPIC_API_KEY` | `agentClaude.py`, `foo_gui.py` (any `claude-*` model) |
| Google | `GEMINI_API_KEY` or `GOOGLE_API_KEY` | `agentGoogleGUI.py`, `foo_gui.py` (any `gemini-*` model) |

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

- `common_md` — markdown file with shared persona conventions ([common.md](common.md)) prepended to every agent's role.
- `model` — default OpenAI model used by `agentGPTGUI.py`.
- `claude_model` — default Anthropic model used by `agentClaude.py`.
- `google_model` (optional) — default Google model used by `agentGoogleGUI.py`.
- `name`, `user` — substituted into `{name}` and `{user}` placeholders inside all `.md` files.
- `fontsize` — starting font size for every widget; the `[-]` / `[+]` buttons adjust at runtime.

Each entry in `MODELS` (used by [foo_gui.py](foo_gui.py)) has:

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

Each `.md` file in this folder is a *role*. The dropdown in every GUI lists them all (except `common.md`, which is the shared header).

| File | Persona |
|---|---|
| [general.md](general.md) | Generic critical-thinking assistant |
| [researcher.md](researcher.md) | Scientific researcher; rigor, evidence, FAIR data |
| [grant_reviewer_NIH.md](grant_reviewer_NIH.md) | NIH study-section reviewer (5 criteria, 9-point scoring) |
| [grant_reviewer_NSF.md](grant_reviewer_NSF.md) | NSF panel reviewer (Intellectual Merit / Broader Impacts) |
| [grant_writer_NIH.md](grant_writer_NIH.md) | NIH grant writer (Specific Aims, rigor & reproducibility, SABV) |
| [grant_writer_NSF.md](grant_writer_NSF.md) | NSF proposal writer (DMP, Mentoring Plan, IM/BI articulation) |
| [article_writer.md](article_writer.md) | Scientific manuscript writer (IMRaD, EQUATOR guidelines) |
| [article_reviewer.md](article_reviewer.md) | Peer reviewer (review structure, ethics, methodological red flags) |
| [harmonizer.md](harmonizer.md) | Judgment-phase directive for the FOO workflow |

To create a new persona, copy any existing role file, edit it, and save with a new name — it will appear in the dropdown next time you start a GUI. Variables you can use anywhere in the file: `{user}`, `{name}`, and (for harmonizer directives only) `{source_agent_name}`.

---

## 4. Running the apps

### Single-agent GUIs

Each takes an optional positional argument: the role markdown to load. The default is `general.md`.

```bash
python agentClaude.py                       # default: general.md
python agentClaude.py researcher.md
python agentClaude.py grant_writer_NIH.md

python agentGPTGUI.py article_reviewer.md
python agentGoogleGUI.py grant_reviewer_NSF.md
```

Once running, you can switch roles live via the dropdown in the top-left of the window — the conversation is reset when the role changes.

### Multi-agent FOO GUI

```bash
python foo_gui.py
python foo_gui.py --reset      # or -r: wipe agent history before starting
```

Creates one tab per agent listed in `MODELS`. Type into the **broadcast** box at the bottom to send a message to every active agent. Each tab's `Vulnerability` / `Judgment` / `Reflection` buttons drive the three FOO phases.

**`--reset` / `-r` flag.** On startup, each agent normally loads its saved history from `chats/<AgentName>.json` and replays the full transcript to the model as a single priming turn so the conversation resumes with prior context. For long conversations this can take many seconds per agent on the main thread and the GUI will appear stuck while the API call is in flight. Passing `--reset` deletes those JSON files *before* the orchestrator initializes, so each agent starts fresh and the GUI comes up immediately. Equivalent to the in-app **Reset** button, but without the confirmation dialog and without needing the GUI to be responsive first.

---

## 5. Features available in every GUI

| Feature | How |
|---|---|
| **Markdown rendering** | Every response is rendered via `QTextEdit.setMarkdown()` (headings, bold, lists, code blocks). Source: [md_widget.py](md_widget.py). |
| **Role dropdown** | Top-left of each chat window / tab. Pick any `.md` file in this folder to swap personas; conversation resets. |
| **Font controls** | `[-]` and `[+]` buttons in the top-right scale every widget. Initial size from `fontsize` in `config.json`. |
| **Drag-and-drop files** | Drop a file onto any chat window. Text files are inlined; images and PDFs go via each engine's *native* upload (base64 content block for OpenAI / Anthropic, Files API for Gemini) so layout and embedded images are preserved. In `foo_gui.py`, a drop broadcasts to every active tab. See [file_loader.py](file_loader.py). |
| **Upload progress** | An indeterminate progress bar + live status label (`Reading…`, `Base64-encoding…`, `Sending to <provider>…`) shows during uploads. Token counts (`in: 1234 / out: 256`) are reported when the API returns them. Source: [file_upload_worker.py](file_upload_worker.py). |
| **Session header** | Each window prints model name, model code, provider, load timestamp, agent name, and role at startup (and again whenever the role changes). |

### Supported file types on drop

- **Text** (inlined as user message): `.txt`, `.md`, `.csv`, `.tsv`, `.json`, `.yaml`/`.yml`, `.log`, `.tex`, `.bib`, source code (`.py`, `.r`, `.js`, etc.), HTML/XML, SQL, …
- **Images** (native): `.jpg`/`.jpeg`, `.png`, `.gif`, `.webp`.
- **PDFs** (native): `.pdf`.

Anything else returns an "Unsupported file type" message.

---

## 6. Files reference (short)

### Applications

| File | What it is |
|---|---|
| [foo_gui.py](foo_gui.py) | Multi-agent FOO GUI (tabs, broadcast, FOO workflow). |
| [agentClaude.py](agentClaude.py) | Single-Anthropic GUI. CLI: `python agentClaude.py [role.md]`. |
| [agentGPTGUI.py](agentGPTGUI.py) | Single-OpenAI GUI. CLI: `python agentGPTGUI.py [role.md]`. |
| [agentGoogleGUI.py](agentGoogleGUI.py) | Single-Gemini GUI. CLI: `python agentGoogleGUI.py [role.md]`. |

### Support modules

| File | What it is |
|---|---|
| [cls_foo.py](cls_foo.py) | `MultiAgentOrchestrator` — loads agents, runs Vulnerability/Judgment/Reflection. |
| [cls_openai.py](cls_openai.py), [cls_anthropic.py](cls_anthropic.py), [cls_google.py](cls_google.py) | Engine-specific agent classes (chat, history, file upload). |
| [cls_blockchain.py](cls_blockchain.py) | No-op `IntegrityManager` stub. (The real blockchain-integrity module is not bundled.) |
| [md_widget.py](md_widget.py) | `MarkdownTextEdit` — `QTextEdit` subclass that re-renders via `setMarkdown()` on each append. |
| [md_loader.py](md_loader.py) | `load_persona()` + `read_md_file()` — compose `common.md` + role file, substitute variables. |
| [file_loader.py](file_loader.py) | `classify_file()` + `read_text()` + `read_base64()` — drag-and-drop helpers. |
| [file_upload_worker.py](file_upload_worker.py) | `FileUploadWorker(QThread)` + `format_usage()` — keeps uploads off the GUI thread, formats token counts. |

### Configuration & content

| File | What it is |
|---|---|
| [config.json](config.json) | Models, roles, and runtime settings. |
| `*.md` (10 files) | Persona definitions — see table in section 3. |

### Other / not actively used

`agentGPT.py`, `agentGoogle.py` are CLI-only versions; `Agent.py`, `ClaudeChatUL.py`, `ClaudeGUI.py`, `ClaudeQA.py`, `ClaudeUUID.py`, `editJSON.py`, `generateSummaries.py`, `grant_review.py`, `multillm.py`, `agentGroq.py` are earlier prototypes kept for reference.

---

## 7. Troubleshooting

**`'ascii' codec can't encode character '’' …` on OpenAI calls.**
Means a string with a non-ASCII character (smart quote, em dash) is reaching an HTTP header. Most often a stray smart quote in an environment variable. Check `OPENAI_API_KEY`, `OPENAI_ORGANIZATION`, `OPENAI_PROJECT`, `OPENAI_BASE_URL` for any pasted-from-document characters.

**`temperature is deprecated for this model` (Anthropic).**
Already handled — `_temperature_kwarg()` in [cls_anthropic.py](cls_anthropic.py) and [agentClaude.py](agentClaude.py) omits the parameter for models in `_TEMPERATURE_DEPRECATED_PREFIXES`. If a new model deprecates it, add its prefix to that tuple.

**"Pylance can't resolve `openai` / `anthropic` …" in VS Code, but `pip show` confirms they're installed.**
Wrong interpreter selected in VS Code. `Cmd/Ctrl+Shift+P` → `Python: Select Interpreter`, pick the one matching `which python` in your activated venv, then `Developer: Reload Window`.

**`No config.json found in CWD: …` warning at startup.**
Old foo_gui.py message; the `CWD` mechanism still falls back to the local folder. To silence, ensure the `CWD` key is *not* in `config.json` (it is removed in the current build).

**The window appears to freeze during file uploads.**
Fixed — uploads now run on `FileUploadWorker` with a live progress bar. If you still see this, you're probably running an older copy of `foo_gui.py`; re-pull.

**`foo_gui.py` looks stuck after `Updated thread ID for <Agent>: …`.**
Not stuck — replaying a long saved conversation back to the model on startup. The replay runs synchronously per agent before the GUI is shown; with a multi-thousand-line history this can take 30–90 s per agent. Either wait it out, or relaunch with `python foo_gui.py --reset` to discard the prior history and start fresh.

**`model_not_found` from OpenAI/Anthropic.**
The model ID in `config.json` doesn't exist on your account. Edit the `model_code` value (e.g. `gpt-5.5` → `gpt-5.1`, or pick whatever your dashboard lists).

---

## 8. License

Creative Commons Attribution-ShareAlike 4.0 International (CC BY-SA 4.0).
By Juan B. Gutiérrez, Professor of Mathematics, University of Texas at San Antonio.
