# CreepyAI Configuration Guide

This guide explains the configuration options for CreepyAI applications.

## Configuration File

The main configuration file is located at `config/settings.yaml`. The following sections describe the available configuration options.

## Application Settings

```yaml
application:
  name: "My CreepyAI Project"
  version: "0.1.0"
  debug_mode: false
```

- `name`: The display name of your application
- `version`: Your application version
- `debug_mode`: Enable detailed debug logging and features

## Data Settings

```yaml
data:
  input_dir: "data/input"
  output_dir: "data/output"
  temp_dir: "data/temp"
```

- `input_dir`: Directory for input data files
- `output_dir`: Directory for output data files
- `temp_dir`: Directory for temporary files

## Model Settings

```yaml
models:
  model_dir: "models"
  default_model: "base_model"
  model_parameters:
    learning_rate: 0.01
    batch_size: 64
    epochs: 10
```

- `model_dir`: Directory containing model files
- `default_model`: The model to use by default
- `model_parameters`: Parameters for model training and inference

## Plugin System

```yaml
plugins:
  enabled: true
  directory: "plugins"
  auto_load: true
  allowed_plugins:
    - "plugin_name_1"
    - "plugin_name_2"
```

- `enabled`: Enable or disable the plugin system
- `directory`: Directory containing plugins
- `auto_load`: Automatically load plugins at startup
- `allowed_plugins`: Optional list to restrict which plugins can be loaded

## Logging

```yaml
logging:
  level: "INFO"
  log_dir: "logs"
  log_rotation: true
  max_log_size: 10485760  # 10 MB
```

- `level`: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- `log_dir`: Directory for log files
- `log_rotation`: Enable or disable log rotation
- `max_log_size`: Maximum size for log files before rotation (in bytes)
