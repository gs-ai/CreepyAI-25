
# CreepyAI - OSINT Assistant

CreepyAI is an open-source OSINT (Open Source Intelligence) assistant designed to help researchers, analysts, and cybersecurity professionals gather and analyze public information effectively.

## Features

- **Multi-platform Search**: Query multiple sources simultaneously
- **Credential-free Operation**: Work entirely with offline data exports and open data sources—no API keys or logins required
- **Data Visualization**: Visualize relationships between data points
- **Project Management**: Save and organize your research
- **Plugin System**: Extend functionality with custom plugins
- **Reporting**: Generate comprehensive reports

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

CreepyAI supports plugins to extend its functionality. Plugins are stored in `~/.config/creepyai/plugins/` by default.

### Offline Data Imports

Each plugin now watches a dedicated ingest directory so you no longer need to browse for exports manually. Drop your ZIP archives or extracted folders into the matching subdirectory and enable the plugin's checkbox.

- **Linux**: `~/.local/share/creepyai/imports/<plugin_slug>`
- **macOS**: `~/Library/Application Support/CreepyAI/imports/<plugin_slug>`
- **Windows**: `%APPDATA%\CreepyAI\imports\<plugin_slug>`

The slug corresponds to the plugin name in lowercase with spaces replaced by underscores (for example, `Instagram` → `instagram`, `Email Analysis` → `email_analysis`). The configuration dialog displays the resolved path for each plugin as a reminder.

### Creating Plugins

To create a plugin:

1. Create a new Python file in the plugins directory
2. Inherit from the `BasePlugin` class
3. Implement the required methods
4. See `plugin_base.py` for more details

## Troubleshooting

### PyQt5 Issues

If you encounter Qt/PyQt5 errors:

1. **Run the diagnostic tool**:
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
