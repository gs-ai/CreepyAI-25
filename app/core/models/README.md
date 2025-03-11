# CreepyAI Models

This directory contains models used by CreepyAI for data analysis and prediction.

## Models Structure

```
models/
├── clustering/       # Clustering models
├── classification/   # Classification models
├── embeddings/       # Embedding models
└── config/           # Model configuration files
```

## Model Types

### Clustering Models

Used to identify patterns and group similar data points together.

### Classification Models

Used to categorize data into predefined classes.

### Embedding Models

Used to convert data into vector representations for further analysis.

## Adding New Models

1. Create a new directory for your model type if it doesn't exist
2. Add your model files
3. Create a configuration file in the `config/` directory
4. Register the model in the application configuration

## Using Models in CreepyAI

Models can be used by both the core application and plugins. Reference a model using its name as defined in its configuration file.
