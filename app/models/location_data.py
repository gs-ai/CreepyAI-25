"""
Location Data Model for CreepyAI
Defines the data structures for location information
"""

import uuid
import json
import logging
from typing import Dict, List, Optional, Any, Union, Set
from datetime import datetime
from dataclasses import dataclass, field, asdict

from PyQt5.QtCore import QObject, pyqtSignal

from app.plugins.base_plugin import LocationPoint

logger = logging.getLogger(__name__)

@dataclass
class GeocodedInfo:
    """Geocoded information about a location"""
    formatted_address: str = ""
    country: str = ""
    administrative_area: str = ""
    locality: str = ""
    postal_code: str = ""
    thoroughfare: str = ""
    provider: str = ""
    confidence: float = 0.0  # 0-100 scale
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GeocodedInfo':
        """Create from dictionary"""
        return cls(**data)

@dataclass
class LocationMetadata:
    """Additional metadata for a location"""
    source_id: str = ""  # Original ID from the source
    url: str = ""  # URL related to the location, if any
    description: str = ""  # Additional description
    accuracy: float = 0.0  # Accuracy in meters
    altitude: Optional[float] = None  # Altitude in meters
    speed: Optional[float] = None  # Speed in m/s
    heading: Optional[float] = None  # Heading in degrees
    floor_level: Optional[int] = None  # Floor level for indoor locations
    confidence: float = 100.0  # Confidence score (0-100)
    tags: List[str] = field(default_factory=list)  # Tags for categorization
    properties: Dict[str, Any] = field(default_factory=dict)  # Any additional properties
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LocationMetadata':
        """Create from dictionary"""
        return cls(**data)

class Location:
    """Represents a geographic location with metadata"""
    
    def __init__(self, 
                latitude: float, 
                longitude: float,
                timestamp: Optional[datetime] = None,
                source: str = "",
                context: str = "",
                location_id: Optional[str] = None):
        """
        Initialize a location
        
        Args:
            latitude: Location latitude
            longitude: Location longitude
            timestamp: When the location was recorded
            source: Source of the location data
            context: Context information about this location
            location_id: Optional unique ID (generated if not provided)
        """
        self.id = location_id or str(uuid.uuid4())
        self.latitude = latitude
        self.longitude = longitude
        self.timestamp = timestamp or datetime.now()
        self.source = source
        self.context = context
        self.geocoded: Optional[GeocodedInfo] = None
        self.metadata = LocationMetadata()
        self.address = ""  # Cached address string
        self.photos: List[str] = []  # Paths to related photos
        self.notes: str = ""  # User notes about this location
        self.verified: bool = False  # Whether this location has been verified
        self._nearby_locations: List['Location'] = []  # Cached nearby locations
        
    def __eq__(self, other):
        """Check if locations are equal"""
        if not isinstance(other, Location):
            return False
        
        return (self.id == other.id or 
                (abs(self.latitude - other.latitude) < 0.00001 and 
                 abs(self.longitude - other.longitude) < 0.00001 and
                 abs((self.timestamp - other.timestamp).total_seconds()) < 60))
    
    def __hash__(self):
        """Hash the location"""
        return hash((self.id, self.latitude, self.longitude, self.timestamp))
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary
        
        Returns:
            Dictionary representation of the location
        """
        result = {
            'id': self.id,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source,
            'context': self.context,
            'address': self.address,
            'verified': self.verified,
            'notes': self.notes,
            'photos': self.photos,
            'metadata': self.metadata.to_dict()
        }
        
        # Add geocoded info if available
        if self.geocoded:
            result['geocoded'] = self.geocoded.to_dict()
            
        return result
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Location':
        """
        Create a Location object from a dictionary
        
        Args:
            data: Dictionary with location data
            
        Returns:
            New Location object
        """
        # Handle timestamp
        timestamp = None
        if data.get('timestamp'):
            try:
                if isinstance(data['timestamp'], str):
                    timestamp = datetime.fromisoformat(data['timestamp'].replace('Z', '+00:00'))
                else:
                    timestamp = datetime.fromtimestamp(data['timestamp'])
            except (ValueError, TypeError):
                logger.warning(f"Invalid timestamp format: {data.get('timestamp')}")
                timestamp = datetime.now()
        
        # Create the location
        location = cls(
            latitude=float(data['latitude']),
            longitude=float(data['longitude']),
            timestamp=timestamp,
            source=data.get('source', ''),
            context=data.get('context', ''),
            location_id=data.get('id')
        )
        
        # Set optional attributes
        location.address = data.get('address', '')
        location.notes = data.get('notes', '')
        location.verified = data.get('verified', False)
        location.photos = data.get('photos', [])
        
        # Set metadata
        if 'metadata' in data:
            location.metadata = LocationMetadata.from_dict(data['metadata'])
            
        # Set geocoded info
        if 'geocoded' in data:
            location.geocoded = GeocodedInfo.from_dict(data['geocoded'])
            
        return location
    
    @classmethod
    def from_location_point(cls, point: LocationPoint) -> 'Location':
        """
        Create a Location from a LocationPoint
        
        Args:
            point: LocationPoint object
            
        Returns:
            New Location object
        """
        return cls(
            latitude=point.latitude,
            longitude=point.longitude,
            timestamp=point.timestamp,
            source=point.source,
            context=point.context
        )
    
    def to_geojson(self) -> Dict[str, Any]:
        """
        Convert to GeoJSON feature
        
        Returns:
            GeoJSON feature dictionary
        """
        properties = {
            'id': self.id,
            'timestamp': self.timestamp.isoformat() if self.timestamp else None,
            'source': self.source,
            'context': self.context,
            'address': self.address
        }
        
        # Add metadata properties
        if self.metadata:
            for k, v in self.metadata.to_dict().items():
                if v is not None and k not in properties:
                    properties[k] = v
        
        return {
            'type': 'Feature',
            'geometry': {
                'type': 'Point',
                'coordinates': [self.longitude, self.latitude]  # GeoJSON uses [lng, lat]
            },
            'properties': properties
        }
    
    def distance_to(self, other: 'Location') -> float:
        """
        Calculate the distance to another location in kilometers
        
        Args:
            other: Other location
            
        Returns:
            Distance in kilometers
        """
        from geopy.distance import geodesic
        
        return geodesic(
            (self.latitude, self.longitude),
            (other.latitude, other.longitude)
        ).kilometers
    
    def set_nearby_locations(self, locations: List['Location']) -> None:
        """
        Set the list of nearby locations
        
        Args:
            locations: List of nearby locations
        """
        self._nearby_locations = locations
        
    def get_nearby_locations(self) -> List['Location']:
        """
        Get nearby locations
        
        Returns:
            List of nearby locations
        """
        return self._nearby_locations


class LocationDataModel(QObject):
    """
    Model for managing location data
    
    Emits signals when the data changes to update the UI
    """
    
    # Signals for data changes
    locationAdded = pyqtSignal(Location)
    locationRemoved = pyqtSignal(str)  # Location ID
    locationUpdated = pyqtSignal(Location)
    locationsCleared = pyqtSignal()
    dataChanged = pyqtSignal()
    
    def __init__(self):
        """Initialize the location data model"""
        super().__init__()
        self._locations: Dict[str, Location] = {}  # ID -> Location
        self._tags: Set[str] = set()  # All tags used
        self._sources: Set[str] = set()  # All sources used
        
    def add_location(self, location: Location) -> str:
        """
        Add a location to the model
        
        Args:
            location: Location to add
            
        Returns:
            ID of the added location
        """
        self._locations[location.id] = location
        
        # Update tags and sources
        if location.metadata and location.metadata.tags:
            self._tags.update(location.metadata.tags)
        
        if location.source:
            self._sources.add(location.source)
            
        # Emit signal
        self.locationAdded.emit(location)
        self.dataChanged.emit()
        
        return location.id
    
    def add_locations(self, locations: List[Location]) -> List[str]:
        """
        Add multiple locations to the model
        
        Args:
            locations: Locations to add
            
        Returns:
            List of added location IDs
        """
        added_ids = []
        
        for location in locations:
            loc_id = self.add_location(location)
            added_ids.append(loc_id)
            
        return added_ids
    
    def get_location(self, location_id: str) -> Optional[Location]:
        """
        Get a location by ID
        
        Args:
            location_id: Location ID
            
        Returns:
            Location object or None if not found
        """
        return self._locations.get(location_id)
    
    def update_location(self, location: Location) -> bool:
        """
        Update a location
        
        Args:
            location: Updated location
            
        Returns:
            True if location was updated, False if not found
        """
        if location.id in self._locations:
            self._locations[location.id] = location
            
            # Update tags and sources
            self._refresh_tags_and_sources()
            
            # Emit signal
            self.locationUpdated.emit(location)
            self.dataChanged.emit()
            
            return True
            
        return False
    
    def remove_location(self, location_id: str) -> bool:
        """
        Remove a location
        
        Args:
            location_id: ID of location to remove
            
        Returns:
            True if location was removed, False if not found
        """
        if location_id in self._locations:
            location = self._locations.pop(location_id)
            
            # Update tags and sources
            self._refresh_tags_and_sources()
            
            # Emit signal
            self.locationRemoved.emit(location_id)
            self.dataChanged.emit()
            
            return True
            
        return False
    
    def clear_locations(self) -> None:
        """Clear all locations"""
        self._locations.clear()
        self._tags.clear()
        self._sources.clear()
        
        # Emit signal
        self.locationsCleared.emit()
        self.dataChanged.emit()
    
    def get_all_locations(self) -> List[Location]:
        """
        Get all locations
        
        Returns:
            List of all locations
        """
        return list(self._locations.values())
    
    def get_location_count(self) -> int:
        """
        Get the number of locations
        
        Returns:
            Number of locations
        """
        return len(self._locations)
    
    def get_all_tags(self) -> List[str]:
        """
        Get all tags used in locations
        
        Returns:
            List of all tags
        """
        return sorted(list(self._tags))
    
    def get_all_sources(self) -> List[str]:
        """
        Get all sources used in locations
        
        Returns:
            List of all sources
        """
        return sorted(list(self._sources))
    
    def find_locations_by_source(self, source: str) -> List[Location]:
        """
        Find locations by source
        
        Args:
            source: Source to filter by
            
        Returns:
            List of matching locations
        """
        return [loc for loc in self._locations.values() if loc.source == source]
    
    def find_locations_by_tag(self, tag: str) -> List[Location]:
        """
        Find locations by tag
        
        Args:
            tag: Tag to filter by
            
        Returns:
            List of matching locations
        """
        return [
            loc for loc in self._locations.values() 
            if loc.metadata and loc.metadata.tags and tag in loc.metadata.tags
        ]
    
    def find_locations_by_date_range(self, 
                                    start_date: Optional[datetime] = None, 
                                    end_date: Optional[datetime] = None) -> List[Location]:
        """
        Find locations within a date range
        
        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            
        Returns:
            List of matching locations
        """
        result = []
        
        for loc in self._locations.values():
            if not loc.timestamp:
                continue
                
            if start_date and loc.timestamp < start_date:
                continue
                
            if end_date and loc.timestamp > end_date:
                continue
                
            result.append(loc)
            
        return result
    
    def find_locations_by_bounding_box(self, 
                                      min_lat: float, 
                                      min_lon: float, 
                                      max_lat: float, 
                                      max_lon: float) -> List[Location]:
        """
        Find locations within a bounding box
        
        Args:
            min_lat: Minimum latitude
            min_lon: Minimum longitude
            max_lat: Maximum latitude
            max_lon: Maximum longitude
            
        Returns:
            List of matching locations
        """
        return [
            loc for loc in self._locations.values()
            if min_lat <= loc.latitude <= max_lat and min_lon <= loc.longitude <= max_lon
        ]
    
    def find_nearest_locations(self, 
                             lat: float, 
                             lon: float, 
                             max_count: int = 10,
                             max_distance: Optional[float] = None) -> List[Location]:
        """
        Find locations nearest to a point
        
        Args:
            lat: Latitude
            lon: Longitude
            max_count: Maximum number of locations to return
            max_distance: Maximum distance in kilometers (None for no limit)
            
        Returns:
            List of nearest locations
        """
        # Create a reference point
        from geopy.distance import geodesic
        
        # Calculate distances
        locations_with_distance = []
        for loc in self._locations.values():
            dist = geodesic((lat, lon), (loc.latitude, loc.longitude)).kilometers
            
            if max_distance is not None and dist > max_distance:
                continue
                
            locations_with_distance.append((loc, dist))
        
        # Sort by distance
        locations_with_distance.sort(key=lambda x: x[1])
        
        # Return the nearest locations
        return [loc for loc, _ in locations_with_distance[:max_count]]
    
    def to_geojson(self) -> Dict[str, Any]:
        """
        Convert all locations to a GeoJSON FeatureCollection
        
        Returns:
            GeoJSON FeatureCollection dictionary
        """
        features = [loc.to_geojson() for loc in self._locations.values()]
        
        return {
            'type': 'FeatureCollection',
            'features': features
        }
    
    def save_to_file(self, file_path: str) -> bool:
        """
        Save locations to a file
        
        Args:
            file_path: Path to save to
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Convert locations to dictionaries
            locations_data = [loc.to_dict() for loc in self._locations.values()]
            
            # Save to file
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(locations_data, f, indent=2)
                
            return True
        except Exception as e:
            logger.error(f"Error saving locations to {file_path}: {e}")
            return False
    
    @classmethod
    def load_from_file(cls, file_path: str) -> 'LocationDataModel':
        """
        Load locations from a file
        
        Args:
            file_path: Path to load from
            
        Returns:
            New LocationDataModel
        """
        model = cls()
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                locations_data = json.load(f)
            
            # Convert dictionaries to Location objects
            for loc_data in locations_data:
                location = Location.from_dict(loc_data)
                model.add_location(location)
                
            return model
        except Exception as e:
            logger.error(f"Error loading locations from {file_path}: {e}")
            return model
    
    def _refresh_tags_and_sources(self) -> None:
        """Refresh the sets of tags and sources"""
        self._tags.clear()
        self._sources.clear()
        
        for loc in self._locations.values():
            if loc.metadata and loc.metadata.tags:
                self._tags.update(loc.metadata.tags)
            
            if loc.source:
                self._sources.add(loc.source)
