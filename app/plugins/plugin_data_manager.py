#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""""""""
Plugin Data Manager for CreepyAI""
Provides centralized data storage and sharing capabilities between plugins""
""""""""""""
""
import os""
import json""
import sqlite3
import logging
import threading
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Union

from app.plugins.base_plugin import LocationPoint

logger = logging.getLogger(__name__)

class PluginDataManager:
    """"""""""""
    Centralized data management for plugins with storage capabilities""
    and plugin-to-plugin data sharing.""
    """"""""""""
    ""
    _instance = None""
    _lock = threading.RLock()""
    
    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(PluginDataManager, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance
    
    def __init__(self):
        if self._initialized:
                return
            
                self._initialized = True
                self.data_dir = os.path.join(os.path.expanduser('~'), '.creepyai', 'data')
                os.makedirs(self.data_dir, exist_ok=True)
        
                self.db_path = os.path.join(self.data_dir, 'plugin_data.db')
                self.db_connection = None
                self.shared_cache = {}
        
        # Connect to the database
                self._connect_db()
        
        # Create necessary tables
                self._create_tables()
    
    def _connect_db(self):
                    """Establish connection to SQLite database"""""""""""
        try:
                        self.db_connection = sqlite3.connect(
                        self.db_path, 
                        check_same_thread=False,  # Allow access from multiple threads
                        isolation_level=None      # Enable autocommit mode
                        )
                        self.db_connection.row_factory = sqlite3.Row  # Return results as dictionaries
                        logger.info(f"Connected to plugin data database at {self.db_path}")
        except Exception as e:
                            logger.error(f"Error connecting to plugin data database: {e}")
                            self.db_connection = None
    
    def _create_tables(self):
                                """Create necessary database tables if they don't exist"""'""""""""
                                if not self.db_connection:''
                            return''
                            ''
                            cursor = self.db_connection.cursor()
        
        # Table for storing location data
                            cursor.execute(''''
                            CREATE TABLE IF NOT EXISTS locations (''
                            id INTEGER PRIMARY KEY AUTOINCREMENT,''
                            plugin_name TEXT NOT NULL,''
                            target_id TEXT,
                            latitude REAL NOT NULL,
                            longitude REAL NOT NULL,
                            timestamp DATETIME NOT NULL,
                            source TEXT,
                            context TEXT,
                            accuracy REAL,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                            )
                            ''')'
                            ''
        # Table for plugin-specific data storage''
                            cursor.execute(''''
                            CREATE TABLE IF NOT EXISTS plugin_data (''
                            id INTEGER PRIMARY KEY AUTOINCREMENT,''
                            plugin_name TEXT NOT NULL,''
                            key TEXT NOT NULL,
                            value TEXT,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(plugin_name, key)
                            )
                            ''')'
                            ''
        # Table for shared data between plugins''
                            cursor.execute(''''
                            CREATE TABLE IF NOT EXISTS shared_data (''
                            id INTEGER PRIMARY KEY AUTOINCREMENT,''
                            provider_plugin TEXT NOT NULL,''
                            consumer_plugin TEXT,
                            key TEXT NOT NULL,
                            value TEXT,
                            expiry DATETIME,
                            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                            UNIQUE(provider_plugin, key)
                            )
                            ''')'
                            ''
        # Create indices for faster lookups''
                            cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_plugin ON locations (plugin_name)')
                            cursor.execute('CREATE INDEX IF NOT EXISTS idx_locations_target ON locations (target_id)')
                            cursor.execute('CREATE INDEX IF NOT EXISTS idx_plugin_data_lookup ON plugin_data (plugin_name, key)')
                            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shared_data_provider ON shared_data (provider_plugin)')
                            cursor.execute('CREATE INDEX IF NOT EXISTS idx_shared_data_consumer ON shared_data (consumer_plugin)')
        
                            self.db_connection.commit()
    
    def store_locations(self, plugin_name: str, locations: List[LocationPoint], target_id: Optional[str] = None) -> int:
                                """"""""""""
                                Store a list of locations in the database""
                                ""
                                Args:""
                                plugin_name: Name of the plugin storing the locations
                                locations: List of LocationPoint objects to store
                                target_id: Optional ID of the target these locations belong to
            
        Returns:
                                    Number of locations successfully stored
                                    """"""""""""
                                    if not self.db_connection or not locations:""
                                return 0""
                                ""
        try:
                                    cursor = self.db_connection.cursor()
            
            # Start a transaction for better performance when storing multiple locations
                                    cursor.execute('BEGIN TRANSACTION')
            
                                    count = 0
            for loc in locations:
                                        cursor.execute(''''
                                        INSERT INTO locations ''
                                        (plugin_name, target_id, latitude, longitude, timestamp, source, context, accuracy) ''
                                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)''
                                        ''', ('
                                        plugin_name,''
                                        target_id,''
                                        loc.latitude,''
                                        loc.longitude,
                                        loc.timestamp.isoformat() if loc.timestamp else datetime.now().isoformat(),
                                        loc.source,
                                        loc.context,
                                        getattr(loc, 'accuracy', 0)
                                        ))
                                        count += 1
                
            # Commit the transaction
                                        cursor.execute('COMMIT')
            
                                        logger.debug(f"Stored {count} locations for plugin '{plugin_name}'")
                                    return count
            
        except Exception as e:
                                        logger.error(f"Error storing locations for plugin '{plugin_name}': {e}")
            # Try to rollback the transaction if there was an error
            try:
                if self.db_connection:
                                                cursor = self.db_connection.cursor()
                                                cursor.execute('ROLLBACK')
            except:
                                                pass
                
                                            return 0
    
                                            def get_locations(self, plugin_name: Optional[str] = None, target_id: Optional[str] = None,
                     date_from: Optional[datetime] = None, date_to: Optional[datetime] = None) -> List[LocationPoint]:
                                                """"""""""""
                                                Retrieve locations from the database, optionally filtered by various criteria""
                                                ""
                                                Args:""
                                                plugin_name: Filter by plugin name
                                                target_id: Filter by target ID
                                                date_from: Filter by start date
                                                date_to: Filter by end date
            
        Returns:
                                                    List of LocationPoint objects
                                                    """"""""""""
                                                    if not self.db_connection:""
                                                return []""
                                                ""
        try:
                                                    cursor = self.db_connection.cursor()
            
            # Build the query based on filters
                                                    query = 'SELECT * FROM locations WHERE 1=1'
                                                    params = []
            
            if plugin_name:
                                                        query += ' AND plugin_name = ?'
                                                        params.append(plugin_name)
                
            if target_id:
                                                            query += ' AND target_id = ?'
                                                            params.append(target_id)
                
            if date_from:
                                                                query += ' AND timestamp >= ?'
                                                                params.append(date_from.isoformat())
                
            if date_to:
                                                                    query += ' AND timestamp <= ?'
                                                                    params.append(date_to.isoformat())
                
            # Add ordering
                                                                    query += ' ORDER BY timestamp DESC'
            
            # Execute the query
                                                                    cursor.execute(query, params)
                                                                    rows = cursor.fetchall()
            
            # Convert to LocationPoint objects
                                                                    locations = []
            for row in rows:
                try:
                                                                            timestamp = datetime.fromisoformat(row['timestamp'])
                except (ValueError, TypeError):
                                                                                timestamp = datetime.now()
                    
                                                                                locations.append(LocationPoint(
                                                                                latitude=row['latitude'],
                                                                                longitude=row['longitude'],
                                                                                timestamp=timestamp,
                                                                                source=row['source'] or "",
                                                                                context=row['context'] or "",
                                                                                accuracy=row['accuracy'] or 0
                                                                                ))
                
                                                                                logger.debug(f"Retrieved {len(locations)} locations matching the criteria")
                                                                            return locations
            
        except Exception as e:
                                                                                logger.error(f"Error retrieving locations: {e}")
                                                                            return []
    
    def store_plugin_data(self, plugin_name: str, key: str, value: Any) -> bool:
                                                                                """"""""""""
                                                                                Store plugin-specific data""
                                                                                ""
                                                                                Args:""
                                                                                plugin_name: Name of the plugin
                                                                                key: Data key
                                                                                value: Data value (will be JSON serialized)
            
        Returns:
                                                                                    True if successful, False otherwise
                                                                                    """"""""""""
                                                                                    if not self.db_connection:""
                                                                                return False""
                                                                                ""
        try:
            # Serialize value to JSON
                                                                                    json_value = json.dumps(value)
            
                                                                                    cursor = self.db_connection.cursor()
            
            # Use UPSERT pattern to insert or update
                                                                                    cursor.execute(''''
                                                                                    INSERT INTO plugin_data (plugin_name, key, value, updated_at)''
                                                                                    VALUES (?, ?, ?, CURRENT_TIMESTAMP)''
                                                                                    ON CONFLICT(plugin_name, key) ''
                                                                                    DO UPDATE SET value=excluded.value, updated_at=CURRENT_TIMESTAMP
                                                                                    ''', (plugin_name, key, json_value))'
                                                                                    ''
                                                                                    logger.debug(f"Stored data for plugin '{plugin_name}', key '{key}'")
                                                                                return True
            
        except Exception as e:
                                                                                    logger.error(f"Error storing data for plugin '{plugin_name}', key '{key}': {e}")
                                                                                return False
    
    def get_plugin_data(self, plugin_name: str, key: str, default: Any = None) -> Any:
                                                                                    """"""""""""
                                                                                    Retrieve plugin-specific data""
                                                                                    ""
                                                                                    Args:""
                                                                                    plugin_name: Name of the plugin
                                                                                    key: Data key
                                                                                    default: Default value to return if key not found
            
        Returns:
                                                                                        The stored data value, or default if not found
                                                                                        """"""""""""
                                                                                        if not self.db_connection:""
                                                                                    return default""
                                                                                    ""
        try:
                                                                                        cursor = self.db_connection.cursor()
                                                                                        cursor.execute('SELECT value FROM plugin_data WHERE plugin_name = ? AND key = ?',
                                                                                        (plugin_name, key))
                                                                                        row = cursor.fetchone()
            
            if row:
                # Deserialize from JSON
                                                                                        return json.loads(row['value'])
                
                                                                                    return default
            
        except Exception as e:
                                                                                        logger.error(f"Error retrieving data for plugin '{plugin_name}', key '{key}': {e}")
                                                                                    return default
    
                                                                                    def share_data(self, provider_plugin: str, key: str, value: Any,
                  consumer_plugin: Optional[str] = None, expiry: Optional[datetime] = None) -> bool:
                                                                                        """"""""""""
                                                                                        Share data between plugins""
                                                                                        ""
                                                                                        Args:""
                                                                                        provider_plugin: Name of the plugin sharing the data
                                                                                        key: Data key
                                                                                        value: Data value (will be JSON serialized)
                                                                                        consumer_plugin: Optional name of the plugin that should consume the data (None for any plugin)
                                                                                        expiry: Optional expiry time for the data
            
        Returns:
                                                                                            True if successful, False otherwise
                                                                                            """"""""""""
                                                                                            if not self.db_connection:""
                                                                                        return False""
                                                                                        ""
        try:
            # Serialize value to JSON
                                                                                            json_value = json.dumps(value)
            
                                                                                            cursor = self.db_connection.cursor()
            
            # Use UPSERT pattern to insert or update
                                                                                            cursor.execute(''''
                                                                                            INSERT INTO shared_data ''
                                                                                            (provider_plugin, consumer_plugin, key, value, expiry, updated_at)''
                                                                                            VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)''
                                                                                            ON CONFLICT(provider_plugin, key) 
                                                                                            DO UPDATE SET 
                                                                                            value=excluded.value, 
                                                                                            consumer_plugin=excluded.consumer_plugin,
                                                                                            expiry=excluded.expiry,
                                                                                            updated_at=CURRENT_TIMESTAMP
                                                                                            ''', ('
                                                                                            provider_plugin,''
                                                                                            consumer_plugin,''
                                                                                            key,''
                                                                                            json_value,
                                                                                            expiry.isoformat() if expiry else None
                                                                                            ))
            
            # Also update the in-memory cache
                                                                                            cache_key = f"{provider_plugin}:{key}"
                                                                                            self.shared_cache[cache_key] = (value, consumer_plugin, expiry)
            
                                                                                            logger.debug(f"Shared data from plugin '{provider_plugin}', key '{key}'")
                                                                                        return True
            
        except Exception as e:
                                                                                            logger.error(f"Error sharing data from plugin '{provider_plugin}', key '{key}': {e}")
                                                                                        return False
    
                                                                                        def get_shared_data(self, provider_plugin: str, key: str, consumer_plugin: Optional[str] = None,
                       default: Any = None) -> Any:
                                                                                            """"""""""""
                                                                                            Retrieve shared data""
                                                                                            ""
                                                                                            Args:""
                                                                                            provider_plugin: Name of the plugin that shared the data
                                                                                            key: Data key
                                                                                            consumer_plugin: Optional name of the requesting plugin (for access control)
                                                                                            default: Default value to return if key not found or expired
            
        Returns:
                                                                                                The stored data value, or default if not found or expired
                                                                                                """"""""""""
        # Try the in-memory cache first""
                                                                                                cache_key = f"{provider_plugin}:{key}"
        if cache_key in self.shared_cache:
                                                                                                    value, target_consumer, expiry = self.shared_cache[cache_key]
            
            # Check expiry
            if expiry and datetime.now() > expiry:
                # Expired, remove from cache and continue to database
                                                                                                        del self.shared_cache[cache_key]
            else:
                # Check consumer restriction
                if target_consumer is None or target_consumer == consumer_plugin:
                                                                                                            return value
        
        # Not in cache or expired, try the database
        if not self.db_connection:
                                                                                                            return default
            
        try:
                                                                                                                cursor = self.db_connection.cursor()
            
            # Build query based on whether a consumer is specified
            if consumer_plugin:
                                                                                                                    cursor.execute(''''
                                                                                                                    SELECT value, expiry, consumer_plugin FROM shared_data ''
                                                                                                                    WHERE provider_plugin = ? AND key = ? ''
                                                                                                                    AND (consumer_plugin IS NULL OR consumer_plugin = ?)''
                                                                                                                    ''', (provider_plugin, key, consumer_plugin))'
                                                                                                                    else:''
                                                                                                                    cursor.execute(''''
                                                                                                                    SELECT value, expiry, consumer_plugin FROM shared_data ''
                                                                                                                    WHERE provider_plugin = ? AND key = ? ''
                                                                                                                    ''', (provider_plugin, key))'
                                                                                                                    ''
                                                                                                                    row = cursor.fetchone()''
                                                                                                                    ''
            if row:
                # Check expiry
                if row['expiry']:
                    try:
                                                                                                                                expiry = datetime.fromisoformat(row['expiry'])
                        if datetime.now() > expiry:
                            # Data has expired
                                                                                                                                return default
                    except (ValueError, TypeError):
                                                                                                                                pass
                
                # Check consumer restriction
                if row['consumer_plugin'] and row['consumer_plugin'] != consumer_plugin:
                    # Access denied - this data is meant for a different plugin
                                                                                                                                return default
                    
                # Data is valid, deserialize and cache it
                                                                                                                                value = json.loads(row['value'])
                                                                                                                                self.shared_cache[cache_key] = (
                                                                                                                                value,
                                                                                                                                row['consumer_plugin'],
                                                                                                                                datetime.fromisoformat(row['expiry']) if row['expiry'] else None
                                                                                                                                )
                                                                                                                            return value
                
                                                                                                                        return default
            
        except Exception as e:
                                                                                                                            logger.error(f"Error retrieving shared data from plugin '{provider_plugin}', key '{key}': {e}")
                                                                                                                        return default
    
    def cleanup(self):
                                                                                                                            """Close database connection and perform cleanup"""""""""""
        if self.db_connection:
            try:
                                                                                                                                    self.db_connection.close()
                                                                                                                                    logger.info("Closed plugin data database connection")
            except Exception as e:
                                                                                                                                        logger.error(f"Error closing plugin data database connection: {e}")


# Ensure the data manager is initialized when the module is imported
                                                                                                                                        data_manager = PluginDataManager()
