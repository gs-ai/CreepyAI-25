"""
Model management functionality for CreepyAI
"""
import os
import pickle
import json
import logging
from typing import Dict, Any, Optional, Tuple, List

logger = logging.getLogger(__name__)


class ModelManager:
    """Manages machine learning models for the application"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the model manager
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.model_config = config.get('models', {})
        self.model_dir = self.model_config.get('model_dir', 'models')
        self.default_model = self.model_config.get('default_model', 'base_model')
        
        # Create model directory if it doesn't exist
        os.makedirs(self.model_dir, exist_ok=True)
        
        logger.debug(f"Model manager initialized with model_dir={self.model_dir}, "
                    f"default_model={self.default_model}")
    
    def save_model(self, model: Any, model_name: str, metadata: Dict[str, Any] = None) -> bool:
        """
        Save a model to disk
        
        Args:
            model: Model to save
            model_name: Name of the model
            metadata: Additional model metadata
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
            
            # Create model directory if it doesn't exist
            os.makedirs(os.path.dirname(model_path), exist_ok=True)
            
            # Prepare metadata
            if metadata is None:
                metadata = {}
                
            # Add basic metadata if not present
            if 'name' not in metadata:
                metadata['name'] = model_name
            
            # Create model package with model and metadata
            model_package = {
                'model': model,
                'metadata': metadata
            }
            
            # Save model
            with open(model_path, 'wb') as f:
                pickle.dump(model_package, f)
            
            # Save metadata separately for easy inspection
            metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Saved model {model_name} to {model_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving model {model_name}: {str(e)}")
            return False
    
    def load_model(self, model_name: Optional[str] = None) -> Tuple[Any, Dict[str, Any], bool]:
        """
        Load a model from disk
        
        Args:
            model_name: Name of the model to load. If None, loads the default model.
            
        Returns:
            Tuple of (model, metadata, success)
        """
        try:
            if model_name is None:
                model_name = self.default_model
                
            model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
            
            if not os.path.exists(model_path):
                logger.error(f"Model file not found: {model_path}")
                return None, {}, False
            
            # Load model
            with open(model_path, 'rb') as f:
                model_package = pickle.load(f)
            
            # Extract model and metadata
            if isinstance(model_package, dict) and 'model' in model_package:
                model = model_package['model']
                metadata = model_package.get('metadata', {})
            else:
                # Handle legacy format (just the model)
                model = model_package
                metadata = {'name': model_name}
            
            logger.info(f"Loaded model {model_name} from {model_path}")
            return model, metadata, True
            
        except Exception as e:
            logger.error(f"Error loading model {model_name}: {str(e)}")
            return None, {}, False
    
    def list_models(self) -> List[str]:
        """
        List available models
        
        Returns:
            List of model names
        """
        try:
            model_files = [f for f in os.listdir(self.model_dir) 
                          if f.endswith('.pkl') and not f.endswith('_metadata.pkl')]
            return [os.path.splitext(f)[0] for f in model_files]
        except Exception as e:
            logger.error(f"Error listing models: {str(e)}")
            return []
    
    def delete_model(self, model_name: str) -> bool:
        """
        Delete a model
        
        Args:
            model_name: Name of the model to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            model_path = os.path.join(self.model_dir, f"{model_name}.pkl")
            metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
            
            # Delete model file
            if os.path.exists(model_path):
                os.remove(model_path)
                logger.info(f"Deleted model file: {model_path}")
            
            # Delete metadata file
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
                logger.info(f"Deleted metadata file: {metadata_path}")
            
            return True
            
        except Exception as e:
            logger.error(f"Error deleting model {model_name}: {str(e)}")
            return False
    
    def get_model_metadata(self, model_name: str) -> Dict[str, Any]:
        """
        Get metadata for a model
        
        Args:
            model_name: Name of the model
            
        Returns:
            Model metadata dictionary
        """
        try:
            metadata_path = os.path.join(self.model_dir, f"{model_name}_metadata.json")
            
            if not os.path.exists(metadata_path):
                logger.warning(f"Metadata file not found: {metadata_path}")
                # Try extracting from model file
                _, metadata, success = self.load_model(model_name)
                if success:
                    return metadata
                return {}
            
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error loading metadata for model {model_name}: {str(e)}")
            return {}
