# CreepyAI-25 – OSINT Intelligence Platform

![CreepyAI Logo](./creepyai25-logo1.1.png)

CreepyAI-25 is an open-source geolocation intelligence assistant that ingests, normalises, and correlates
offline-first datasets to help investigators surface actionable insights without relying on API keys or
account credentials.

## Feature Highlights

- **Managed ingest directories** – every plugin exposes a dedicated drop folder so you can preload exports
  and archives without browsing for paths at run time.
- **Automated social media collectors** – refresh OSINT datasets for supported platforms with a single
  command that dedupes records and preserves the latest evidence inside each plugin directory.
- **Local LLM analysis** – run privacy-preserving intelligence synthesis against collected data using locally
  installed Ollama models tuned for Apple Silicon laptops.
- **Credential-free operation** – work exclusively with offline exports and open datasets while keeping audit
  logs and chain-of-custody metadata intact.
- **Modular plugin ecosystem** – expand coverage with dedicated parsers, normalisers, and correlation
  engines for social media, email, location history, and OSINT archives.
- **Rich visualisation** – map locations, explore relationships, and generate reports directly from the
  CreepyAI-25 desktop interface.

## Quick Start

### Installation

1. **Create an environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Launch the desktop app**
   ```bash
   python app/main.py
   ```

### Prepare Offline Datasets

1. Place exported archives for each plugin inside its managed ingest directory. CreepyAI-25 provisions the
   folders automatically on first launch:
   - **Linux**: `~/.local/share/CreepyAI/imports/<plugin_source>`
   - **macOS**: `~/Library/Application Support/CreepyAI/imports/<plugin_source>`
   - **Windows**: `%APPDATA%\CreepyAI\imports\<plugin_source>`

2. (Optional) Refresh the curated social media datasets without credentials:
   ```bash
   python scripts/collect_social_media_data.py
   ```
   The collector downloads public location intelligence, deduplicates the payload, and stores a
   `collected_locations.json` file in each plugin directory.

### Run Local LLM Analysis

Use the new analysis CLI to correlate records and surface investigative leads with locally installed
Ollama models:

```bash
python scripts/analyze_intelligence.py "Subject Name" --focus "recent activity"
```

The command prints a structured summary, hotspot locations, and raw model outputs. Pass `--output json` to
emit machine-readable results or `--models` to specify a custom subset of installed models.

#### Recommended Ollama Models for MacBook Air M2 (16 GB RAM)

| Model Tag           | Approx. Size | Why it works well |
|---------------------|--------------|-------------------|
| `llama3.2:latest`   | ~2.0 GB      | Efficient distilled Llama 3.2 variant delivering balanced reasoning speed on Apple Silicon. |
| `phi4-mini:latest`  | ~2.5 GB      | Lightweight Phi-4 Mini tuned for investigative assistance with minimal memory footprint. |
| `wizardlm2:7b`      | ~4.1 GB      | Instruction-tuned WizardLM 2 model that excels at synthesising cross-source findings locally. |

All models are available through Ollama and operate entirely on-device.

## Additional Tooling

- `scripts/analyze_intelligence.py` – run local LLM-driven analysis across collected datasets.
- `scripts/collect_social_media_data.py` – maintain curated, deduplicated location payloads per plugin.
- `scripts/download_icons.py` – regenerate UI icons using canonical naming.

## Development Notes

- The plugin framework lives under `app/plugins/` with shared ingestion utilities in `app/plugins/base_plugin.py`.
- Social media plugins share infrastructure in `app/plugins/social_media/` and rely on the managed ingest
  directories created at runtime.
- New analysis helpers (data loading, local LLM orchestration, relationship graphing) are provided in
  `app/analysis/`.

### Testing

```bash
pytest
```

### Contributing

1. Fork the repository.
2. Create a feature branch (`git checkout -b feature/amazing-feature`).
3. Commit your changes (`git commit -m "Add some amazing feature"`).
4. Push to the branch (`git push origin feature/amazing-feature`).
5. Open a Pull Request.

## License

CreepyAI-25 is released under the MIT License – see `LICENSE` for details.

## Disclaimer

CreepyAI-25 is intended for lawful OSINT research by authorised practitioners. Ensure compliance with
applicable legislation, organisational policy, and terms of service for any datasets you ingest. The authors
are not responsible for misuse of this software.
