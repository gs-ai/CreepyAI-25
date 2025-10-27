# CreepyAI-25 – OSINT Intelligence Platform

![CreepyAI-25 Emblem](./image.png)

CreepyAI-25 is an open-source geolocation intelligence assistant that
ingests, normalises, correlates, and visualises offline-first datasets
to help investigators surface actionable insights without relying on API
keys or account credentials. The project emphasises reproducible
workflow automation, modular plugins, and on-device analytics so
practitioners can operate within strict legal and ethical boundaries.

---

## Feature Highlights

- **Managed ingest directories** – every plugin exposes a dedicated drop
  folder so you can preload exports and archives without browsing for
  paths at run time.
- **Automated social media collectors** – refresh OSINT datasets for
  supported platforms with a single command that dedupes records and
  preserves the latest evidence inside each plugin directory.
- **Local LLM analysis** – run privacy-preserving intelligence synthesis
  against collected data using locally installed Ollama models tuned for
  Apple Silicon laptops.
- **Credential-free operation** – work exclusively with offline exports
  and open datasets while keeping audit logs and chain-of-custody
  metadata intact.
- **Modular plugin ecosystem** – expand coverage with dedicated parsers,
  normalisers, and correlation engines for social media, email, location
  history, and OSINT archives.
- **Rich visualisation** – map locations, explore relationships, and
  generate reports directly from the CreepyAI-25 desktop interface.
- **Structured logging & metrics** – centralised logging across the core
  engine and plugins with optional JSON output for SIEM ingestion.

---

## Architecture Overview

The codebase is divided into a handful of cohesive packages:

| Module | Purpose |
| --- | --- |
| `app/core` | Event-driven engine orchestrating plugin execution, jobs, and resilience controls. |
| `app/plugins` | Base plugin definitions plus domain-specific collectors, parsers, and analysts. |
| `app/gui` | PyQt-based desktop interface for managing datasets, launching jobs, and reviewing outputs. |
| `resources/` | Icons, imagery, and static assets rendered by the GUI and report generator. |
| `tests/` | Unit, integration, and regression suites ensuring stable behaviour across releases. |

The `PluginManager` coordinates plugin discovery, lifecycle hooks, and
fault isolation. Plugins communicate results to the engine through
well-defined dataclasses so downstream analysis layers can reason about
them consistently.

---

## Quick Start

### 1. Create a Python Environment

```bash
conda env create -f environments/conda-env.yaml
conda activate creepyai
```

The bundled `conda-env.yaml` provisions Python 3.11, Node.js, and the
project dependencies in a managed Conda environment named `creepyai`.
If the environment already exists, run `conda activate creepyai &&
conda env update -f environments/conda-env.yaml` to refresh it.

### 2. Launch the Desktop App

```bash
python app/main.py
```

The GUI surfaces plugin status, allows dataset ingestion, and exposes
analysis workflows that can also be scripted via CLI helpers.

### 3. Run the CLI Collectors (Optional)

Use the social media collector scripts to refresh public datasets:

```bash
python scripts/collect_social_media_data.py
```

Each run deduplicates records and writes a `collected_locations.json`
file to the appropriate plugin ingest directory.

---

## Preparing Offline Datasets

1. Place exported archives for each plugin inside its managed ingest
   directory. By default the application prefers a repository-local drop
   folder so you can keep imports with the project during development:

   - **Repository (preferred)**: `./INPUT-DATA/<plugin_source>`

2. The legacy per-user application data locations remain supported if
   you prefer a global drop location:

   - **Linux**: `~/.local/share/CreepyAI/imports/<plugin_source>`
   - **macOS**: `~/Library/Application Support/CreepyAI/imports/<plugin_source>`
   - **Windows**: `%APPDATA%\CreepyAI\imports\<plugin_source>`

3. (Optional) Kick off the automated collectors to seed the ingest
   directories with curated OSINT payloads.

---

## Local LLM Correlation Workflows

Use the analysis CLI to correlate records and surface investigative
leads with locally installed Ollama models:

```bash
python scripts/analyze_intelligence.py "Subject Name" --focus "recent activity"
```

The command prints a structured summary, hotspot locations, and raw
model outputs. Pass `--output json` to emit machine-readable results or
`--models` to specify a custom subset of installed models.

#### Recommended Ollama Models for MacBook Air M2 (16 GB RAM)

| Model Tag | Approx. Size | Why it works well |
| --- | --- | --- |
| `llama3.2:latest` | ~2.0 GB | Efficient distilled Llama 3.2 variant delivering balanced reasoning speed on Apple Silicon. |
| `phi4-mini:latest` | ~2.5 GB | Lightweight Phi-4 Mini tuned for investigative assistance with minimal memory footprint. |
| `wizardlm2:7b` | ~4.1 GB | Instruction-tuned WizardLM 2 model that excels at synthesising cross-source findings locally. |

All models are available through Ollama and operate entirely on-device.

---

## Development Workflow

1. **Install tooling** – ensure `pre-commit`, `ruff`, and `mypy` are
   available in your environment.
2. **Activate hooks** – run `pre-commit install` to apply formatting and
   linting automatically.
3. **Add type hints** – maintain full typing coverage, especially inside
   plugins where dynamic data structures are common.
4. **Document behaviour** – include docstrings and inline comments for
   complex logic paths so auditing is straightforward.

### Testing & QA

```bash
pytest
```

Integration suites live under `tests/integration/` and leverage mocked
data sources for deterministic runs. Regression tests protect the
`Engine`, `PluginManager`, `BasePlugin` subclasses, and GUI event loops
from behavioural drift across releases.

### Structured Logging & Error Handling

- Core engine exceptions bubble through a unified handler that records
  context-rich log events and ensures plugin failures are isolated from
  unrelated jobs.
- Configure JSON logs via environment variables for ingestion into SIEM
  platforms.
- Use `utilities/logging.py` helpers to standardise log formats across
  first- and third-party plugins.

---

## Security and Compliance Expectations

- All user input and file paths must be sanitised before execution.
- Validate file types and external data before parsing to avoid
  injection attacks.
- Follow OSINT legal/ethical guidelines; consult `SECURITY.md` for
  deeper policy notes and check jurisdictional requirements prior to
  deployment.

---

## Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m "Add some amazing feature"`).
4. Run formatting and tests (`pre-commit run --all-files && pytest`).
5. Push to the branch (`git push origin feature/amazing-feature`).
6. Open a Pull Request describing the change set and any follow-up work.

Please review the `docs/` directory for API references, plugin authoring
guides, and the project roadmap.

---

## License

CreepyAI-25 is released under the MIT License – see `LICENSE` for
details.

---

## Disclaimer

CreepyAI-25 is intended for lawful OSINT research by authorised
practitioners. Ensure compliance with applicable legislation,
organisational policy, and terms of service for any datasets you ingest.
The authors are not responsible for misuse of this software.
