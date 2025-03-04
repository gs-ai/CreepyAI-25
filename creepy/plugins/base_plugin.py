import abc
from typing import List, Dict, Any, Optional
from datetime import datetime
import os
import json

class LocationPoint:
    def __init__(self, latitude: float, longitude: float, timestamp: datetime, 
                 source: str, context: str = "", accuracy: float = 0):
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp
        self.source = source
        self.context = context
        self.accuracy = accuracy
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat(),
            "source": self.source,
            "context": self.context,
            "accuracy": self.accuracy
        }

class BasePlugin:
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.enabled = True
        self.config = {}
        self.data_dir = os.path.join(os.path.expanduser("~"), ".creepyai", "data")
        os.makedirs(self.data_dir, exist_ok=True)
    
    def collect_locations(self, target: str, date_from: Optional[datetime] = None, 
                         date_to: Optional[datetime] = None) -> List[LocationPoint]:
        raise NotImplementedError
    
    def get_configuration_options(self) -> List[Dict[str, Any]]:
        raise NotImplementedError
    
    def set_configuration(self, config: Dict[str, Any]) -> None:
        self.config = config
    
    def save_data(self, target: str, locations: List[LocationPoint]) -> None:
        target_dir = os.path.join(self.data_dir, self.name)
        os.makedirs(target_dir, exist_ok=True)
        
        filename = os.path.join(target_dir, f"{target.replace('@', '')}.json")
        with open(filename, 'w') as f:
            json.dump([loc.to_dict() for loc in locations], f, indent=2)
