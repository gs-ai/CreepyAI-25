import sqlite3
import json
import os
import logging
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    """Handles database operations for CreepyAI."""
    
    def __init__(self, db_path=None):
        """Initialize the database."""
        self.db_path = db_path or os.path.join(os.path.expanduser("~"), ".creepyai", "creepyai.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._conn = None
        self._lock = threading.RLock()  # Thread-safe database access
        self._connect()
        self._setup_tables()
    
    @contextmanager
    def _get_connection(self):
        """Get a thread-safe database connection."""
        with self._lock:
            try:
                if self._conn is None:
                    self._connect()
                    
                # Create a cursor for this specific operation
                cursor = self._conn.cursor()
                yield cursor
                self._conn.commit()
            except sqlite3.Error as e:
                if self._conn:
                    self._conn.rollback()
                logger.error(f"Database error: {str(e)}")
                raise
            finally:
                if cursor:
                    cursor.close()
                    
    def _connect(self):
        """Connect to the SQLite database."""
        try:
            # Enable URI mode to allow options for connection
            self._conn = sqlite3.connect(f"file:{self.db_path}?mode=rwc", 
                                        uri=True,
                                        check_same_thread=False,  # Will handle thread safety with our own lock
                                        detect_types=sqlite3.PARSE_DECLTYPES)
            self._conn.row_factory = sqlite3.Row
            
            # Enable foreign keys
            with self._get_connection() as cursor:
                cursor.execute("PRAGMA foreign_keys = ON")
                
                # Performance optimizations
                cursor.execute("PRAGMA journal_mode = WAL")  # Write-Ahead Logging
                cursor.execute("PRAGMA synchronous = NORMAL")  # Balance safety and performance
                cursor.execute("PRAGMA cache_size = 10000")  # Increase cache size (in pages)
                
            logger.info("Database connection established")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
            
    def _setup_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            with self._get_connection() as cursor:
                # Projects table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    settings TEXT
                )
                ''')
                
                # Targets table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS targets (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    project_id INTEGER,
                    name TEXT NOT NULL,
                    username TEXT,
                    data TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL,
                    FOREIGN KEY (project_id) REFERENCES projects (id) ON DELETE CASCADE
                )
                ''')
                
                # Locations table
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS locations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER,
                    latitude REAL NOT NULL,
                    longitude REAL NOT NULL,
                    date TEXT,
                    source TEXT,
                    source_type TEXT,
                    confidence REAL,
                    context TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (target_id) REFERENCES targets (id) ON DELETE CASCADE
                )
                ''')
                
                # Sources table (for tracking non-API sources)
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS sources (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    target_id INTEGER,
                    source_url TEXT,
                    source_type TEXT,
                    source_date TEXT,
                    content_hash TEXT,
                    data TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (target_id) REFERENCES targets (id) ON DELETE CASCADE
                )
                ''')
                
                # Cache table for scraped content
                cursor.execute('''
                CREATE TABLE IF NOT EXISTS cache (
                    url TEXT PRIMARY KEY,
                    content TEXT,
                    headers TEXT,
                    timestamp TEXT NOT NULL,
                    expiry TEXT
                )
                ''')
                
                # Create indices for better performance
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_targets_project_id ON targets(project_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_target_id ON locations(target_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_sources_target_id ON sources(target_id)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_coordinates ON locations(latitude, longitude)')
                cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_date ON locations(date)')
                
                logger.info("Database tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Database setup error: {str(e)}")
            raise
    
    def create_project(self, name: str, description: str = "", settings: Optional[Dict] = None) -> Optional[int]:
        """
        Create a new project.
        
        Args:
            name: Project name
            description: Project description
            settings: Project settings
            
        Returns:
            int: Project ID or None if failed
        """
        now = datetime.now().isoformat()
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    "INSERT INTO projects (name, description, created_at, updated_at, settings) VALUES (?, ?, ?, ?, ?)",
                    (name, description, now, now, json.dumps(settings or {}))
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to create project: {str(e)}")
            return None
            
    def add_target(self, project_id: int, name: str, username: Optional[str] = None, data: Optional[Dict] = None) -> Optional[int]:
        """
        Add a target to a project.
        
        Args:
            project_id: Project ID
            name: Target name
            username: Target username
            data: Target data
            
        Returns:
            int: Target ID or None if failed
        """
        now = datetime.now().isoformat()
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    "INSERT INTO targets (project_id, name, username, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                    (project_id, name, username, json.dumps(data or {}), now, now)
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add target: {str(e)}")
            return None
            
    def add_location(self, target_id: int, latitude: float, longitude: float, 
                    date: Optional[str] = None, source: Optional[str] = None, 
                    source_type: Optional[str] = None, confidence: Optional[float] = None, 
                    context: Optional[Dict] = None) -> Optional[int]:
        """
        Add a location for a target.
        
        Args:
            target_id: Target ID
            latitude: Location latitude
            longitude: Location longitude
            date: Location date
            source: Location source
            source_type: Location source type
            confidence: Location confidence
            context: Location context
            
        Returns:
            int: Location ID or None if failed
        """
        now = datetime.now().isoformat()
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    "INSERT INTO locations (target_id, latitude, longitude, date, source, source_type, confidence, context, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (target_id, latitude, longitude, date, source, source_type, confidence, json.dumps(context or {}), now)
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add location: {str(e)}")
            return None

    def add_batch_locations(self, locations: List[Dict[str, Any]]) -> int:
        """
        Add multiple locations in a single transaction for better performance.
        
        Args:
            locations: List of location dictionaries
            
        Returns:
            int: Number of locations added
        """
        now = datetime.now().isoformat()
        added_count = 0
        
        try:
            with self._get_connection() as cursor:
                for location in locations:
                    cursor.execute(
                        "INSERT INTO locations (target_id, latitude, longitude, date, source, source_type, confidence, context, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (
                            location.get('target_id'),
                            location.get('latitude'),
                            location.get('longitude'),
                            location.get('date'),
                            location.get('source'),
                            location.get('source_type'),
                            location.get('confidence'),
                            json.dumps(location.get('context', {})),
                            now
                        )
                    )
                    added_count += 1
                    
            return added_count
        except sqlite3.Error as e:
            logger.error(f"Failed to add batch locations: {str(e)}")
            return 0

    def add_source(self, target_id: int, source_url: str, source_type: str,
                  source_date: Optional[str] = None, content_hash: Optional[str] = None, 
                  data: Optional[Dict] = None) -> Optional[int]:
        """
        Add a data source for a target.
        
        Args:
            target_id: Target ID
            source_url: Source URL
            source_type: Source type
            source_date: Source date
            content_hash: Content hash
            data: Source data
            
        Returns:
            int: Source ID or None if failed
        """
        now = datetime.now().isoformat()
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    "INSERT INTO sources (target_id, source_url, source_type, source_date, content_hash, data, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (target_id, source_url, source_type, source_date, content_hash, json.dumps(data or {}), now)
                )
                return cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add source: {str(e)}")
            return None
            
    def cache_content(self, url: str, content: str, headers: Optional[Dict] = None, 
                     expiry: Optional[str] = None) -> bool:
        """
        Cache scraped content.
        
        Args:
            url: URL to cache
            content: Content to cache
            headers: Response headers
            expiry: Cache expiry date
            
        Returns:
            bool: True if cached successfully
        """
        now = datetime.now().isoformat()
        try:
            with self._get_connection() as cursor:
                cursor.execute(
                    "INSERT OR REPLACE INTO cache (url, content, headers, timestamp, expiry) VALUES (?, ?, ?, ?, ?)",
                    (url, content, json.dumps(headers or {}), now, expiry)
                )
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to cache content: {str(e)}")
            return False
            
    def get_cached_content(self, url: str) -> Optional[Dict[str, Any]]:
        """
        Get cached content if available and not expired.
        
        Args:
            url: URL to get content for
            
        Returns:
            dict: Cached content or None
        """
        try:
            now = datetime.now().isoformat()
            with self._get_connection() as cursor:
                cursor.execute(
                    "SELECT content, headers, expiry FROM cache WHERE url = ? AND (expiry IS NULL OR expiry > ?)",
                    (url, now)
                )
                row = cursor.fetchone()
                
                if row:
                    return {
                        'content': row['content'],
                        'headers': json.loads(row['headers']) if row['headers'] else {}
                    }
                    
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get cached content: {str(e)}")
            return None
    
    def get_projects(self) -> List[Dict[str, Any]]:
        """
        Get all projects.
        
        Returns:
            list: List of project dictionaries
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
                return [dict(row) for row in cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get projects: {str(e)}")
            return []
            
    def get_targets(self, project_id: int) -> List[Dict[str, Any]]:
        """
        Get all targets for a project.
        
        Args:
            project_id: Project ID
            
        Returns:
            list: List of target dictionaries
        """
        try:
            with self._get_connection() as cursor:
                cursor.execute("SELECT * FROM targets WHERE project_id = ?", (project_id,))
                targets = [dict(row) for row in cursor.fetchall()]
                
                # Convert JSON data
                for target in targets:
                    if 'data' in target and target['data']:
                        target['data'] = json.loads(target['data'])
                        
                return targets
        except sqlite3.Error as e:
            logger.error(f"Failed to get targets: {str(e)}")
            return []
            
    def get_locations(self, target_id: int, 
                     start_date: Optional[str] = None, 
                     end_date: Optional[str] = None,
                     limit: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get locations for a target with optional filtering.
        
        Args:
            target_id: Target ID
            start_date: Start date for filtering
            end_date: End date for filtering
            limit: Maximum number of locations to return
            
        Returns:
            list: List of location dictionaries
        """
        try:
            with self._get_connection() as cursor:
                query = "SELECT * FROM locations WHERE target_id = ?"
                params = [target_id]
                
                if start_date:
                    query += " AND date >= ?"
                    params.append(start_date)
                    
                if end_date:
                    query += " AND date <= ?"
                    params.append(end_date)
                    
                query += " ORDER BY date DESC"
                
                if limit:
                    query += " LIMIT ?"
                    params.append(limit)
                
                cursor.execute(query, params)
                locations = [dict(row) for row in cursor.fetchall()]
                
                # Convert JSON context
                for location in locations:
                    if 'context' in location and location['context']:
                        location['context'] = json.loads(location['context'])
                        
                return locations
        except sqlite3.Error as e:
            logger.error(f"Failed to get locations: {str(e)}")
            return []

    def search_locations(self, search_params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Search locations with complex criteria.
        
        Args:
            search_params: Dictionary with search parameters
            
        Returns:
            list: List of location dictionaries
        """
        try:
            query = "SELECT * FROM locations WHERE 1=1"
            params = []
            
            # Filter by target_id if provided
            if 'target_id' in search_params:
                query += " AND target_id = ?"
                params.append(search_params['target_id'])
            
            # Filter by date range
            if 'start_date' in search_params:
                query += " AND date >= ?"
                params.append(search_params['start_date'])
                
            if 'end_date' in search_params:
                query += " AND date <= ?"
                params.append(search_params['end_date'])
                
            # Filter by source
            if 'source' in search_params:
                query += " AND source LIKE ?"
                params.append(f"%{search_params['source']}%")
                
            # Filter by coordinates range
            if all(k in search_params for k in ['min_lat', 'max_lat', 'min_lon', 'max_lon']):
                query += " AND latitude BETWEEN ? AND ? AND longitude BETWEEN ? AND ?"
                params.extend([
                    search_params['min_lat'],
                    search_params['max_lat'],
                    search_params['min_lon'],
                    search_params['max_lon']
                ])
                
            # Order by
            order_by = search_params.get('order_by', 'date')
            order_dir = search_params.get('order_dir', 'DESC')
            query += f" ORDER BY {order_by} {order_dir}"
            
            # Limit
            if 'limit' in search_params:
                query += " LIMIT ?"
                params.append(search_params['limit'])
                
            with self._get_connection() as cursor:
                cursor.execute(query, params)
                locations = [dict(row) for row in cursor.fetchall()]
                
                # Convert JSON context
                for location in locations:
                    if 'context' in location and location['context']:
                        location['context'] = json.loads(location['context'])
                        
                return locations
        except sqlite3.Error as e:
            logger.error(f"Failed to search locations: {str(e)}")
            return []

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
