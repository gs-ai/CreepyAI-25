#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Monitor for CreepyAI
Monitors plugin performance, resource usage, and health
"""

import os
import sys
import time
import json
import logging
import threading
import traceback
import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
import psutil
import platform

# Import required CreepyAI modules
from plugins.plugins_manager import PluginsManager
from plugins.plugin_registry import registry

logger = logging.getLogger(__name__)

class PluginMonitor:
    """
    Monitors and reports on plugin health, performance, and resource usage
    """
    
    def __init__(self, plugins_manager: Optional[PluginsManager] = None):
        """Initialize the monitor with the plugin manager"""
        self.plugins_manager = plugins_manager or PluginsManager()
        
        # Monitoring state
        self.is_monitoring = False
        self.monitoring_thread = None
        self.stop_event = threading.Event()
        
        # Monitoring config
        self.monitor_interval = 60  # seconds
        self.log_threshold_cpu = 80  # percent
        self.log_threshold_memory = 100 * 1024 * 1024  # 100MB
        self.history_max_samples = 100
        self.collect_call_metrics = True
        self.collect_memory_metrics = True
        self.enable_auto_restart = False
        
        # Monitoring data
        self.stats = {
            'start_time': time.time(),
            'plugins': {},
            'system': {},
            'calls': {},
            'errors': {},
        }
        
        # Create data storage directory
        self.data_dir = os.path.join(os.path.expanduser('~'), '.creepyai', 'monitor')
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Performance data file
        self.perf_data_file = os.path.join(self.data_dir, 'performance_data.json')
        
        # Load existing data if available
        self._load_stats()
        
    def _load_stats(self) -> None:
        """Load previously saved statistics"""
        try:
            if os.path.exists(self.perf_data_file):
                with open(self.perf_data_file, 'r') as f:
                    data = json.load(f)
                    # Only load plugin-specific and call metrics
                    if 'plugins' in data:
                        self.stats['plugins'] = data['plugins']
                    if 'calls' in data:
                        self.stats['calls'] = data['calls']
        except Exception as e:
            logger.error(f"Failed to load monitoring data: {e}")
    
    def _save_stats(self) -> None:
        """Save current statistics to file"""
        try:
            with open(self.perf_data_file, 'w') as f:
                # Add timestamp to stats
                save_data = {
                    'timestamp': time.time(),
                    'plugins': self.stats['plugins'],
                    'calls': self.stats['calls'],
                    'errors': self.stats['errors']
                }
                json.dump(save_data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save monitoring data: {e}")
            
    def start_monitoring(self) -> bool:
        """
        Start the monitoring thread
        
        Returns:
            True if monitoring started successfully, False otherwise
        """
        if self.is_monitoring:
            logger.warning("Monitoring is already active")
            return False
            
        try:
            # Discover plugins
            self.plugins_manager.discover_plugins()
            
            # Reset stop event
            self.stop_event.clear()
            
            # Start monitoring thread
            self.monitoring_thread = threading.Thread(
                target=self._monitoring_loop,
                daemon=True,
                name="PluginMonitorThread"
            )
            self.monitoring_thread.start()
            
            self.is_monitoring = True
            logger.info("Plugin monitoring started")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start monitoring: {e}")
            return False
    
    def stop_monitoring(self) -> None:
        """Stop the monitoring thread"""
        if not self.is_monitoring:
            return
            
        # Signal thread to stop
        self.stop_event.set()
        
        # Wait for thread to finish
        if self.monitoring_thread and self.monitoring_thread.is_alive():
            self.monitoring_thread.join(timeout=5)
            
        self.is_monitoring = False
        logger.info("Plugin monitoring stopped")
        
        # Save final stats
        self._save_stats()
    
    def _monitoring_loop(self) -> None:
        """Main monitoring loop that runs in a separate thread"""
        logger.info("Monitoring loop started")
        
        while not self.stop_event.is_set():
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect plugin metrics
                self._collect_plugin_metrics()
                
                # Collect registry metrics
                self._collect_registry_metrics()
                
                # Analyze metrics and detect issues
                self._analyze_metrics()
                
                # Save stats periodically
                self._save_stats()
                
                # Wait for next collection interval or until stopped
                self.stop_event.wait(self.monitor_interval)
                
            except Exception as e:
                logger.error(f"Error in monitoring loop: {e}")
                logger.debug(traceback.format_exc())
                # Wait a bit before retrying to avoid spinning if there's a persistent error
                time.sleep(5)
    
    def _collect_system_metrics(self) -> None:
        """Collect system-wide metrics"""
        try:
            # Get system metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Store in stats
            self.stats['system'] = {
                'timestamp': time.time(),
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_used': memory.used,
                'memory_available': memory.available,
                'disk_percent': disk.percent,
                'disk_free': disk.free,
                'boot_time': psutil.boot_time(),
                'python_version': platform.python_version(),
                'platform': platform.platform(),
                'processes': len(psutil.pids())
            }
            
        except Exception as e:
            logger.error(f"Failed to collect system metrics: {e}")
    
    def _collect_plugin_metrics(self) -> None:
        """Collect metrics for each plugin"""
        # Get current process
        try:
            process = psutil.Process()
            
            # Get currently loaded plugins
            plugins = self.plugins_manager.plugin_instances
            
            timestamp = time.time()
            
            # Update metrics for each loaded plugin
            for plugin_id, plugin_instance in plugins.items():
                if plugin_id not in self.stats['plugins']:
                    # Initialize plugin stats
                    self.stats['plugins'][plugin_id] = {
                        'first_seen': timestamp,
                        'call_count': 0,
                        'error_count': 0,
                        'last_error': None,
                        'last_call': None,
                        'avg_response_time': 0,
                        'memory_samples': [],
                        'cpu_samples': [],
                    }
                
                # Only measure memory if enabled
                if self.collect_memory_metrics:
                    try:
                        # This is approximate since we can't isolate memory per plugin
                        # We can use it as a relative measure compared to system baseline
                        memory_info = process.memory_info()
                        memory_usage = memory_info.rss
                        
                        # Add to history, limited to max samples
                        plugin_stats = self.stats['plugins'][plugin_id]
                        plugin_stats['memory_samples'].append({
                            'timestamp': timestamp,
                            'value': memory_usage
                        })
                        
                        # Trim history if needed
                        if len(plugin_stats['memory_samples']) > self.history_max_samples:
                            plugin_stats['memory_samples'] = plugin_stats['memory_samples'][-self.history_max_samples:]
                    except Exception as e:
                        logger.debug(f"Could not get memory info for {plugin_id}: {e}")
        
        except Exception as e:
            logger.error(f"Failed to collect plugin metrics: {e}")
    
    def _collect_registry_metrics(self) -> None:
        """Collect metrics from the plugin registry"""
        try:
            # Get statistics from the registry
            registry_stats = registry.get_statistics()
            
            # Update call counts from registry
            for service_name, call_count in registry_stats.get('service_calls', {}).items():
                if service_name not in self.stats['calls']:
                    self.stats['calls'][service_name] = {
                        'count': call_count,
                        'first_call': time.time(),
                        'last_call': time.time()
                    }
                else:
                    # Update last call time if count has increased
                    if call_count > self.stats['calls'][service_name]['count']:
                        self.stats['calls'][service_name]['last_call'] = time.time()
                    # Update count
                    self.stats['calls'][service_name]['count'] = call_count
            
            # Update hook invocation counts
            for hook_name, invocation_count in registry_stats.get('hook_invocations', {}).items():
                hook_key = f"hook:{hook_name}"
                if hook_key not in self.stats['calls']:
                    self.stats['calls'][hook_key] = {
                        'count': invocation_count,
                        'first_call': time.time(),
                        'last_call': time.time()
                    }
                else:
                    # Update last call time if count has increased
                    if invocation_count > self.stats['calls'][hook_key]['count']:
                        self.stats['calls'][hook_key]['last_call'] = time.time()
                    # Update count
                    self.stats['calls'][hook_key]['count'] = invocation_count
                    
        except Exception as e:
            logger.error(f"Failed to collect registry metrics: {e}")
    
    def _analyze_metrics(self) -> None:
        """Analyze collected metrics to detect issues"""
        try:
            # Check for memory issues
            system_memory = self.stats['system'].get('memory_percent', 0)
            if system_memory > 90:
                logger.warning(f"High system memory usage: {system_memory}%")
            
            # Check for CPU issues
            system_cpu = self.stats['system'].get('cpu_percent', 0)
            if system_cpu > 90:
                logger.warning(f"High system CPU usage: {system_cpu}%")
            
            # Check for inactive plugins
            current_time = time.time()
            for plugin_id, plugin_stats in self.stats['plugins'].items():
                # Check if plugin hasn't been used recently but is loaded
                if plugin_id in self.plugins_manager.plugin_instances:
                    last_call = plugin_stats.get('last_call')
                    if last_call and (current_time - last_call) > 24 * 60 * 60:  # 24 hours
                        logger.info(f"Plugin {plugin_id} has not been used in 24 hours")
            
        except Exception as e:
            logger.error(f"Error analyzing metrics: {e}")
    
    def record_plugin_call(self, plugin_id: str, method_name: str, duration: float, success: bool) -> None:
        """
        Record metrics for a plugin method call
        
        Args:
            plugin_id: ID of the plugin
            method_name: Name of the method that was called
            duration: Duration of the call in seconds
            success: Whether the call was successful
        """
        if not self.collect_call_metrics:
            return
            
        try:
            # Initialize plugin stats if needed
            if plugin_id not in self.stats['plugins']:
                self.stats['plugins'][plugin_id] = {
                    'first_seen': time.time(),
                    'call_count': 0,
                    'error_count': 0,
                    'last_error': None,
                    'last_call': None,
                    'avg_response_time': 0,
                    'memory_samples': [],
                    'cpu_samples': [],
                }
            
            plugin_stats = self.stats['plugins'][plugin_id]
            current_time = time.time()
            
            # Update call statistics
            plugin_stats['call_count'] += 1
            plugin_stats['last_call'] = current_time
            
            # Update error statistics if the call failed
            if not success:
                plugin_stats['error_count'] += 1
                plugin_stats['last_error'] = current_time
                
                # Record error in global error stats
                error_key = f"{plugin_id}.{method_name}"
                if error_key not in self.stats['errors']:
                    self.stats['errors'][error_key] = {
                        'count': 1,
                        'first_error': current_time,
                        'last_error': current_time
                    }
                else:
                    self.stats['errors'][error_key]['count'] += 1
                    self.stats['errors'][error_key]['last_error'] = current_time
            
            # Update average response time
            call_count = plugin_stats['call_count']
            if call_count == 1:
                plugin_stats['avg_response_time'] = duration
            else:
                # Moving average
                plugin_stats['avg_response_time'] = (
                    plugin_stats['avg_response_time'] * (call_count - 1) + duration
                ) / call_count
                
            # Record the call in calls stats
            call_key = f"{plugin_id}.{method_name}"
            if call_key not in self.stats['calls']:
                self.stats['calls'][call_key] = {
                    'count': 1,
                    'first_call': current_time,
                    'last_call': current_time,
                    'success_count': 1 if success else 0,
                    'error_count': 0 if success else 1,
                    'avg_duration': duration
                }
            else:
                call_stats = self.stats['calls'][call_key]
                call_stats['count'] += 1
                call_stats['last_call'] = current_time
                if success:
                    call_stats['success_count'] += 1
                else:
                    call_stats['error_count'] += 1
                    
                # Update average duration
                call_stats['avg_duration'] = (
                    call_stats['avg_duration'] * (call_stats['count'] - 1) + duration
                ) / call_stats['count']
                
        except Exception as e:
            logger.error(f"Failed to record plugin call: {e}")
    
    def get_plugin_stats(self, plugin_id: str = None) -> Dict[str, Any]:
        """
        Get statistics for all plugins or a specific plugin
        
        Args:
            plugin_id: Optional ID of the plugin to get stats for
            
        Returns:
            Dictionary containing plugin statistics
        """
        if plugin_id:
            return self.stats['plugins'].get(plugin_id, {}).copy()
        else:
            return self.stats['plugins'].copy()
    
    def get_system_stats(self) -> Dict[str, Any]:
        """
        Get system statistics
        
        Returns:
            Dictionary containing system statistics
        """
        return self.stats['system'].copy()
    
    def get_call_stats(self) -> Dict[str, Any]:
        """
        Get call statistics
        
        Returns:
            Dictionary containing call statistics
        """
        return self.stats['calls'].copy()
    
    def get_error_stats(self) -> Dict[str, Any]:
        """
        Get error statistics
        
        Returns:
            Dictionary containing error statistics
        """
        return self.stats['errors'].copy()
    
    def get_plugin_health_report(self, plugin_id: str = None) -> Dict[str, Any]:
        """
        Generate a health report for all plugins or a specific plugin
        
        Args:
            plugin_id: Optional ID of the plugin to report on
            
        Returns:
            Health report dictionary
        """
        report = {
            'timestamp': time.time(),
            'uptime': time.time() - self.stats['start_time'],
            'plugins': {},
            'system_health': self._get_system_health()
        }
        
        # Get all plugin IDs to report on
        plugin_ids = [plugin_id] if plugin_id else self.stats['plugins'].keys()
        
        for pid in plugin_ids:
            if pid not in self.stats['plugins']:
                continue
                
            plugin_stats = self.stats['plugins'][pid]
            
            # Calculate error rate
            call_count = plugin_stats.get('call_count', 0)
            error_count = plugin_stats.get('error_count', 0)
            error_rate = (error_count / call_count) * 100 if call_count > 0 else 0
            
            # Calculate memory trend
            memory_trend = 'stable'
            memory_samples = plugin_stats.get('memory_samples', [])
            if len(memory_samples) >= 5:
                # Calculate trend from last 5 samples
                recent_samples = memory_samples[-5:]
                first_value = recent_samples[0]['value']
                last_value = recent_samples[-1]['value']
                
                if last_value > first_value * 1.2:  # 20% increase
                    memory_trend = 'increasing'
                elif last_value < first_value * 0.8:  # 20% decrease
                    memory_trend = 'decreasing'
            
            # Determine health status
            health_status = 'healthy'
            if error_rate > 20:
                health_status = 'unhealthy'
            elif error_rate > 5:
                health_status = 'degraded'
                
            # Check if plugin is loaded
            is_loaded = pid in self.plugins_manager.plugin_instances
                
            # Generate report for this plugin
            report['plugins'][pid] = {
                'health_status': health_status,
                'loaded': is_loaded,
                'call_count': call_count,
                'error_count': error_count,
                'error_rate': error_rate,
                'avg_response_time': plugin_stats.get('avg_response_time', 0),
                'last_call': plugin_stats.get('last_call'),
                'last_error': plugin_stats.get('last_error'),
                'memory_trend': memory_trend
            }
            
        return report
    
    def _get_system_health(self) -> Dict[str, Any]:
        """
        Determine system health based on metrics
        
        Returns:
            System health report
        """
        system_stats = self.stats['system']
        
        # Default to healthy
        health_status = 'healthy'
        issues = []
        
        # Check memory
        memory_percent = system_stats.get('memory_percent', 0)
        if memory_percent > 90:
            health_status = 'unhealthy'
            issues.append(f"Memory usage is critical: {memory_percent}%")
        elif memory_percent > 80:
            health_status = 'degraded'
            issues.append(f"Memory usage is high: {memory_percent}%")
            
        # Check CPU
        cpu_percent = system_stats.get('cpu_percent', 0)
        if cpu_percent > 90:
            health_status = 'unhealthy'
            issues.append(f"CPU usage is critical: {cpu_percent}%")
        elif cpu_percent > 80:
            health_status = 'degraded'
            issues.append(f"CPU usage is high: {cpu_percent}%")
            
        # Check disk
        disk_percent = system_stats.get('disk_percent', 0)
        if disk_percent > 90:
            health_status = 'unhealthy'
            issues.append(f"Disk usage is critical: {disk_percent}%")
        elif disk_percent > 80:
            health_status = 'degraded'
            issues.append(f"Disk usage is high: {disk_percent}%")
            
        return {
            'status': health_status,
            'issues': issues,
            'cpu_percent': cpu_percent,
            'memory_percent': memory_percent,
            'disk_percent': disk_percent
        }


# Create a global monitor instance
plugin_monitor = PluginMonitor()

# Decorator for monitoring plugin method calls
def monitor_call(method):
    """Decorator to monitor plugin method calls"""
    def wrapper(self, *args, **kwargs):
        plugin_id = self.__class__.__name__
        method_name = method.__name__
        start_time = time.time()
        success = True
        
        try:
            result = method(self, *args, **kwargs)
            return result
        except Exception as e:
            success = False
            raise
        finally:
            duration = time.time() - start_time
            plugin_monitor.record_plugin_call(plugin_id, method_name, duration, success)
            
    return wrapper
