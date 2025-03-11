"""
Data management functionality for CreepyAI
"""
import os
import logging
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger(__name__)


class DataManager:
    """Manages data loading, saving, and processing for the application"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the data manager
        
        Args:
            config: Application configuration
        """
        self.config = config
        self.data_config = config.get('data', {})
        self.input_dir = self.data_config.get('input_dir', 'data/input')
        self.output_dir = self.data_config.get('output_dir', 'data/output')
        self.temp_dir = self.data_config.get('temp_dir', 'data/temp')
        
        # Create directories if they don't exist
        os.makedirs(self.input_dir, exist_ok=True)
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir, exist_ok=True)
        
        logger.debug(f"Data manager initialized with directories: input={self.input_dir}, "
                    f"output={self.output_dir}, temp={self.temp_dir}")
    
    def load_data(self, filename: str, data_type: Optional[str] = None) -> Tuple[Any, bool]:
        """
        Load data from a file
        
        Args:
            filename: Name of the file to load
            data_type: Type of data to load (csv, json, xlsx, etc.)
                       If None, will be inferred from the file extension
            
        Returns:
            Tuple of (data, success)
        """
        try:
            filepath = os.path.join(self.input_dir, filename)
            if not os.path.exists(filepath):
                logger.error(f"Data file not found: {filepath}")
                return None, False
            
            # Determine file type from extension if not specified
            if data_type is None:
                _, ext = os.path.splitext(filename)
                data_type = ext[1:].lower() if ext else None
            
            # Load data based on type
            if data_type in ('csv', 'tsv'):
                import pandas as pd
                separator = ',' if data_type == 'csv' else '\t'
                data = pd.read_csv(filepath, sep=separator)
                logger.info(f"Loaded {data.shape[0]} rows and {data.shape[1]} columns from {filename}")
                return data, True
            
            elif data_type == 'json':
                import pandas as pd
                data = pd.read_json(filepath)
                logger.info(f"Loaded {data.shape[0]} rows and {data.shape[1]} columns from {filename}")
                return data, True
            
            elif data_type == 'xlsx':
                import pandas as pd
                data = pd.read_excel(filepath)
                logger.info(f"Loaded {data.shape[0]} rows and {data.shape[1]} columns from {filename}")
                return data, True
            
            elif data_type == 'parquet':
                import pandas as pd
                data = pd.read_parquet(filepath)
                logger.info(f"Loaded {data.shape[0]} rows and {data.shape[1]} columns from {filename}")
                return data, True
            
            elif data_type in ('txt', 'text'):
                with open(filepath, 'r', encoding='utf-8') as f:
                    data = f.read()
                logger.info(f"Loaded {len(data)} characters from {filename}")
                return data, True
            
            else:
                logger.error(f"Unsupported file type: {data_type}")
                return None, False
                
        except Exception as e:
            logger.error(f"Error loading data from {filename}: {str(e)}")
            return None, False
    
    def save_data(self, data: Any, filename: str, data_type: Optional[str] = None) -> bool:
        """
        Save data to a file
        
        Args:
            data: Data to save
            filename: Name of the file to save
            data_type: Type of data to save (csv, json, xlsx, etc.)
                       If None, will be inferred from the file extension
            
        Returns:
            True if successful, False otherwise
        """
        try:
            filepath = os.path.join(self.output_dir, filename)
            os.makedirs(os.path.dirname(filepath), exist_ok=True)
            
            # Determine file type from extension if not specified
            if data_type is None:
                _, ext = os.path.splitext(filename)
                data_type = ext[1:].lower() if ext else None
            
            # Save data based on type
            if data_type == 'csv':
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    data.to_csv(filepath, index=False)
                    logger.info(f"Saved {data.shape[0]} rows and {data.shape[1]} columns to {filename}")
                    return True
                else:
                    logger.error(f"Data must be a pandas DataFrame to save as CSV")
                    return False
            
            elif data_type == 'json':
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    data.to_json(filepath, orient='records', indent=2)
                    logger.info(f"Saved {data.shape[0]} rows and {data.shape[1]} columns to {filename}")
                    return True
                else:
                    import json
                    with open(filepath, 'w', encoding='utf-8') as f:
                        json.dump(data, f, indent=2)
                    logger.info(f"Saved data to {filename}")
                    return True
            
            elif data_type == 'xlsx':
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    data.to_excel(filepath, index=False)
                    logger.info(f"Saved {data.shape[0]} rows and {data.shape[1]} columns to {filename}")
                    return True
                else:
                    logger.error(f"Data must be a pandas DataFrame to save as Excel")
                    return False
            
            elif data_type == 'parquet':
                import pandas as pd
                if isinstance(data, pd.DataFrame):
                    data.to_parquet(filepath, index=False)
                    logger.info(f"Saved {data.shape[0]} rows and {data.shape[1]} columns to {filename}")
                    return True
                else:
                    logger.error(f"Data must be a pandas DataFrame to save as Parquet")
                    return False
            
            elif data_type in ('txt', 'text'):
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(data))
                logger.info(f"Saved {len(str(data))} characters to {filename}")
                return True
            
            else:
                logger.error(f"Unsupported file type: {data_type}")
                return False
                
        except Exception as e:
            logger.error(f"Error saving data to {filename}: {str(e)}")
            return False
    
    def get_input_file_path(self, filename: str) -> str:
        """Get the absolute path to an input file"""
        return os.path.join(self.input_dir, filename)
    
    def get_output_file_path(self, filename: str) -> str:
        """Get the absolute path to an output file"""
        return os.path.join(self.output_dir, filename)
    
    def get_temp_file_path(self, filename: str) -> str:
        """Get the absolute path to a temporary file"""
        return os.path.join(self.temp_dir, filename)
    
    def list_input_files(self, pattern: Optional[str] = None) -> list:
        """List files in the input directory"""
        import glob
        if pattern:
            return glob.glob(os.path.join(self.input_dir, pattern))
        return os.listdir(self.input_dir)
    
    def list_output_files(self, pattern: Optional[str] = None) -> list:
        """List files in the output directory"""
        import glob
        if pattern:
            return glob.glob(os.path.join(self.output_dir, pattern))
        return os.listdir(self.output_dir)
