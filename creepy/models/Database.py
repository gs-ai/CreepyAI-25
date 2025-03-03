import sqlite3
import json
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class Database:
    """Handles database operations for CreepyAI."""
    
    def __init__(self, db_path=None):
        self.db_path = db_path or os.path.join(os.path.expanduser("~"), ".creepyai", "creepyai.db")
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.conn = None
        self.cursor = None
        self._connect()
        self._setup_tables()
        
    def _connect(self):
        """Connect to the SQLite database."""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            self.cursor = self.conn.cursor()
            logger.info("Database connection established")
        except sqlite3.Error as e:
            logger.error(f"Database connection error: {str(e)}")
            raise
            
    def _setup_tables(self):
        """Create necessary tables if they don't exist."""
        try:
            # Projects table
            self.cursor.execute('''
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
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS targets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                project_id INTEGER,
                name TEXT NOT NULL,
                username TEXT,
                data TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL,
                FOREIGN KEY (project_id) REFERENCES projects (id)
            )
            ''')
            
            # Locations table
            self.cursor.execute('''
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
                FOREIGN KEY (target_id) REFERENCES targets (id)
            )
            ''')
            
            # Sources table (for tracking non-API sources)
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_id INTEGER,
                source_url TEXT,
                source_type TEXT,
                source_date TEXT,
                content_hash TEXT,
                data TEXT,
                created_at TEXT NOT NULL,
                FOREIGN KEY (target_id) REFERENCES targets (id)
            )
            ''')
            
            # Cache table for scraped content
            self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS cache (
                url TEXT PRIMARY KEY,
                content TEXT,
                headers TEXT,
                timestamp TEXT NOT NULL,
                expiry TEXT
            )
            ''')
            
            self.conn.commit()
            logger.info("Database tables created successfully")
        except sqlite3.Error as e:
            logger.error(f"Database setup error: {str(e)}")
            raise
    
    def create_project(self, name, description="", settings=None):
        """Create a new project."""
        now = datetime.now().isoformat()
        try:
            self.cursor.execute(
                "INSERT INTO projects (name, description, created_at, updated_at, settings) VALUES (?, ?, ?, ?, ?)",
                (name, description, now, now, json.dumps(settings or {}))
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to create project: {str(e)}")
            return None
            
    def add_target(self, project_id, name, username=None, data=None):
        """Add a target to a project."""
        now = datetime.now().isoformat()
        try:
            self.cursor.execute(
                "INSERT INTO targets (project_id, name, username, data, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?)",
                (project_id, name, username, json.dumps(data or {}), now, now)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add target: {str(e)}")
            return None
            
    def add_location(self, target_id, latitude, longitude, date=None, source=None, source_type=None, confidence=None, context=None):
        """Add a location for a target."""
        now = datetime.now().isoformat()
        try:
            self.cursor.execute(
                "INSERT INTO locations (target_id, latitude, longitude, date, source, source_type, confidence, context, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (target_id, latitude, longitude, date, source, source_type, confidence, json.dumps(context or {}), now)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add location: {str(e)}")
            return None

    # New methods for non-API sources
    def add_source(self, target_id, source_url, source_type, source_date=None, content_hash=None, data=None):
        """Add a data source for a target."""
        now = datetime.now().isoformat()
        try:
            self.cursor.execute(
                "INSERT INTO sources (target_id, source_url, source_type, source_date, content_hash, data, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (target_id, source_url, source_type, source_date, content_hash, json.dumps(data or {}), now)
            )
            self.conn.commit()
            return self.cursor.lastrowid
        except sqlite3.Error as e:
            logger.error(f"Failed to add source: {str(e)}")
            return None
            
    def cache_content(self, url, content, headers=None, expiry=None):
        """Cache scraped content."""
        now = datetime.now().isoformat()
        try:
            self.cursor.execute(
                "INSERT OR REPLACE INTO cache (url, content, headers, timestamp, expiry) VALUES (?, ?, ?, ?, ?)",
                (url, content, json.dumps(headers or {}), now, expiry)
            )
            self.conn.commit()
            return True
        except sqlite3.Error as e:
            logger.error(f"Failed to cache content: {str(e)}")
            return False
            
    def get_cached_content(self, url):
        """Get cached content if available and not expired."""
        try:
            now = datetime.now().isoformat()
            self.cursor.execute(
                "SELECT content, headers, expiry FROM cache WHERE url = ? AND (expiry IS NULL OR expiry > ?)",
                (url, now)
            )
            row = self.cursor.fetchone()
            if row:
                return {
                    'content': row['content'],
                    'headers': json.loads(row['headers']) if row['headers'] else {}
                }
            return None
        except sqlite3.Error as e:
            logger.error(f"Failed to get cached content: {str(e)}")
            return None
    
    def get_projects(self):
        """Get all projects."""
        try:
            self.cursor.execute("SELECT * FROM projects ORDER BY updated_at DESC")
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get projects: {str(e)}")
            return []
            
    def get_targets(self, project_id):
        """Get all targets for a project."""
        try:
            self.cursor.execute("SELECT * FROM targets WHERE project_id = ?", (project_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get targets: {str(e)}")
            return []
            
    def get_locations(self, target_id):
        """Get all locations for a target."""
        try:
            self.cursor.execute("SELECT * FROM locations WHERE target_id = ?", (target_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get locations: {str(e)}")
            return []

    def get_sources(self, target_id):
        """Get all data sources for a target."""
        try:
            self.cursor.execute("SELECT * FROM sources WHERE target_id = ?", (target_id,))
            return [dict(row) for row in self.cursor.fetchall()]
        except sqlite3.Error as e:
            logger.error(f"Failed to get sources: {str(e)}")
            return []

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
