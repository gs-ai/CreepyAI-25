# CreepyAI‑25

CreepyAI is an open‑source OSINT assistant that helps analysts collect and
visualise geolocation information from a variety of data sources. This
repository contains a refactored core engine, a plugin framework, a
PyQt‑based GUI, and a growing library of plugins for processing
archives from social media platforms and other sources.

## Getting started

Install the project dependencies using pip:

```bash
pip install -r requirements.txt
```

To run the application you need Python 3.9 or later. Launch the GUI
with:

```bash
python -m app.gui.launcher
```

## Development

This codebase follows common Python conventions (PEP 8 and type hints)
and uses `pytest` and `unittest` for testing. Run the test suite via:

```bash
pytest creepAI/tests
```

## Contribution guidelines

* Add new functionality as plugins by subclassing `BasePlugin` and
  implementing the `collect_locations` and `search_for_targets` methods.
* Ensure new code is fully type annotated and accompanied by unit
  tests.
* Update documentation under the `docs/` directory when adding
  significant features.
