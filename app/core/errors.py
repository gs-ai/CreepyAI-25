"""
Custom exceptions for the CreepyAI application
"""


class CreepyAIError(Exception):
    """Base class for all CreepyAI exceptions"""
    pass


class ConfigurationError(CreepyAIError):
    """Exception raised for configuration errors"""
    pass


class PluginError(CreepyAIError):
    """Base class for plugin-related exceptions"""
    pass


class PluginLoadError(PluginError):
    """Exception raised when a plugin cannot be loaded"""
    pass


class PluginExecutionError(PluginError):
    """Exception raised when a plugin execution fails"""
    pass


class DataError(CreepyAIError):
    """Base class for data-related exceptions"""
    pass


class DataLoadError(DataError):
    """Exception raised when data cannot be loaded"""
    pass


class DataSaveError(DataError):
    """Exception raised when data cannot be saved"""
    pass


class ModelError(CreepyAIError):
    """Base class for model-related exceptions"""
    pass


class ModelLoadError(ModelError):
    """Exception raised when a model cannot be loaded"""
    pass


class ModelSaveError(ModelError):
    """Exception raised when a model cannot be saved"""
    pass


class ModelNotFoundError(ModelError):
    """Exception raised when a requested model is not found"""
    pass


class ValidationError(CreepyAIError):
    """Exception raised for validation errors"""
    pass
