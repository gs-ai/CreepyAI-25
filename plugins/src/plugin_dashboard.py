#!/usr/bin/python
# -*- coding: utf-8 -*-

""""
Plugin Dashboard for CreepyAI
Provides a simple web-based dashboard for managing and monitoring plugins.
""""

import os
import sys
import json
import logging
import threading
import time
import webbrowser
from datetime import datetime
from typing import Dict, List, Any, Optional
import traceback

try:
    from http.server import HTTPServer, BaseHTTPRequestHandler
    from urllib.parse import urlparse, parse_qs
except ImportError:
    from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
    from urlparse import urlparse, parse_qs

from plugins.plugins_manager import PluginsManager

logger = logging.getLogger(__name__)

# HTML template for the dashboard
DASHBOARD_HTML = """"
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>CreepyAI Plugin Dashboard</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            line-height: 1.6;
            margin: 0;
            padding: 20px;
            color: #333;
            background-color: #f4f4f4;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: #333;
            color: #fff;
            padding: 20px;
            margin-bottom: 20px;
            border-radius: 5px;
        }
        .plugin-card {
            background: #fff;
            padding: 15px;
            margin-bottom: 20px;
            border-radius: 5px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .plugin-header {
            display: flex;
            justify-content: space-between;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
            margin-bottom: 10px;
        }
        .plugin-name {
            font-size: 18px;
            font-weight: bold;
        }
        .plugin-status {
            padding: 5px 10px;
            border-radius: 3px;
            font-size: 14px;
        }
        .status-configured {
            background: #d4edda;
            color: #155724;
        }
        .status-unconfigured {
            background: #f8d7da;
            color: #721c24;
        }
        .plugin-description {
            margin-bottom: 15px;
        }
        .plugin-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
        }
        .btn {
            padding: 8px 15px;
            background: #333;
            color: #fff;
            border: none;
            border-radius: 3px;
            cursor: pointer;
            text-decoration: none;
            display: inline-block;
        }
        .btn:hover {
            background: #555;
        }
        .btn-primary {
            background: #007bff;
        }
        .btn-primary:hover {
            background: #0069d9;
        }
        .btn-danger {
            background: #dc3545;
        }
        .btn-danger:hover {
            background: #c82333;
        }
        .config-form {
            margin-top: 15px;
            padding: 15px;
            background: #f8f9fa;
            border-radius: 5px;
            display: none;
        }
        .form-group {
            margin-bottom: 15px;
        }
        .form-label {
            display: block;
            margin-bottom: 5px;
            font-weight: bold;
        }
        .form-control {
            width: 100%;
            padding: 8px;
            border: 1px solid #ddd;
            border-radius: 3px;
        }
        .form-check {
            display: flex;
            align-items: center;
        }
        .form-check-input {
            margin-right: 10px;
        }
        .form-actions {
            display: flex;
            justify-content: flex-end;
            gap: 10px;
            margin-top: 15px;
        }
        .statistics {
            display: flex;
            margin-bottom: 20px;
            gap: 20px;
        }
        .stat-card {
            background: #fff;
            padding: 15px;
            border-radius: 5px;
            flex: 1;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }
        .stat-value {
            font-size: 24px;
            font-weight: bold;
            margin-top: 10px;
        }
    </style>
    <script>
        function toggleConfigForm(pluginId) {
            const form = document.getElementById(`config-form-${pluginId}`);
            form.style.display = form.style.display === 'none' ? 'block' : 'none';
        }
        
        function refreshDashboard() {
            location.reload();
        }
        
        function testPlugin(pluginId) {
            fetch(`/api/test_plugin?id=${pluginId}`)
                .then(response => response.json())
                .then(data => {
                    alert(data.message);
                })
                .catch(error => {
                    alert('Error testing plugin: ' + error);
                });
        }
        
        function savePluginConfig(pluginId) {
            const form = document.getElementById(`config-form-${pluginId}`);
            const formData = new FormData(form);
            
            fetch('/api/save_config', {
                method: 'POST',
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {:
                    alert('Configuration saved');
                    refreshDashboard();
                } else {
                    alert('Error saving configuration: ' + data.message);
                }
            })
            .catch(error => {
                alert('Error saving configuration: ' + error);
            });
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>CreepyAI Plugin Dashboard</h1>
            <p>Manage and monitor your CreepyAI plugins</p>
        </div>
        
        <div class="statistics">
            <div class="stat-card">
                <h3>Total Plugins</h3>
                <div class="stat-value">{total_plugins}</div>
            </div>
            <div class="stat-card">
                <h3>Configured Plugins</h3>
                <div class="stat-value">{configured_plugins}</div>
            </div>
            <div class="stat-card">
                <h3>Unconfigured Plugins</h3>
                <div class="stat-value">{unconfigured_plugins}</div>
            </div>
        </div>
        
        <div class="plugin-list">
            {plugin_cards}
        </div>
    </div>
</body>
</html>
""""

# HTML template for an individual plugin card
PLUGIN_CARD_HTML = """"
<div class="plugin-card">
    <div class="plugin-header">
        <div class="plugin-name">{name}</div>
        <div class="plugin-status {status_class}">{status}</div>
    </div>
    <div class="plugin-description">{description}</div>
    <div class="plugin-meta">
        <div><strong>ID:</strong> {plugin_id}</div>
        <div><strong>Type:</strong> {plugin_type}</div>
        <div><strong>Version:</strong> {version}</div>
    </div>
    <div class="plugin-actions">
        <button class="btn" onclick="toggleConfigForm('{plugin_id}')">Configure</button>
        <button class="btn btn-primary" onclick="testPlugin('{plugin_id}')">Test</button>
    </div>
    
    <form id="config-form-{plugin_id}" class="config-form">
        <input type="hidden" name="plugin_id" value="{plugin_id}">
        {config_fields}
        <div class="form-actions">
            <button type="button" class="btn" onclick="toggleConfigForm('{plugin_id}')">Cancel</button>
            <button type="button" class="btn btn-primary" onclick="savePluginConfig('{plugin_id}')">Save Configuration</button>
        </div>
    </form>
</div>
""""

class DashboardHandler(BaseHTTPRequestHandler):
    """HTTP request handler for the plugin dashboard."""
    
    def __init__(self, *args, **kwargs):
        self.plugins_manager = kwargs.pop('plugins_manager', None)
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests."""
        parsed_url = urlparse(self.path)
        path = parsed_url.path
        
        # API endpoint for testing a plugin
        if path == '/api/test_plugin':
            self._handle_test_plugin(parse_qs(parsed_url.query))
        # Main dashboard
        elif path == '/' or path == '/index.html':
            self._serve_dashboard()
        # Static files
        else:
            self._serve_static_file(path)
    
    def do_POST(self):
        """Handle POST requests."""
        if self.path == '/api/save_config':
            self._handle_save_config()
        else:
            self.send_error(404, "Not Found")
    
    def _serve_dashboard(self):
        """Serve the main dashboard page."""
        try:
            # Discover plugins if not already done
            if not self.plugins_manager.plugins:
                self.plugins_manager.discover_plugins()
                
            # Count configured plugins
            configured_plugins = 0
            unconfigured_plugins = 0
            
            # Generate plugin cards HTML
            plugin_cards = []
            
            for plugin_id, plugin_info in self.plugins_manager.plugins.items():
                plugin_instance = self.plugins_manager.load_plugin(plugin_id)
                
                if plugin_instance:
                    # Check if plugin is configured
                    is_configured, status_message = plugin_instance.is_configured() if hasattr(plugin_instance, 'is_configured') else (True, "")
                    
                    if is_configured:
                        configured_plugins += 1
                    else:
                        unconfigured_plugins += 1
                    
                    # Get plugin version
                    version = plugin_instance.get_version() if hasattr(plugin_instance, 'get_version') else "1.0.0"
                    
                    # Generate configuration fields
                    config_fields = self._generate_config_fields(plugin_instance)
                    
                    # Create plugin card
                    plugin_card = PLUGIN_CARD_HTML.format(
                        name=plugin_info.get('name', plugin_id),
                        description=plugin_info.get('description', ''),
                        plugin_id=plugin_id,
                        plugin_type=plugin_info.get('type', 'unknown'),
                        version=version,
                        status="Configured" if is_configured else "Needs Configuration",
                        status_class="status-configured" if is_configured else "status-unconfigured",
                        config_fields=config_fields
                    )
                    
                    plugin_cards.append(plugin_card)
            
            # Build dashboard HTML
            html = DASHBOARD_HTML.format(
                total_plugins=len(self.plugins_manager.plugins),
                configured_plugins=configured_plugins,
                unconfigured_plugins=unconfigured_plugins,
                plugin_cards='\n'.join(plugin_cards)
            )
            
            # Send response
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
            
        except Exception as e:
            logger.error(f"Error serving dashboard: {str(e)}")
            logger.error(traceback.format_exc())
            self.send_error(500, f"Internal Server Error: {str(e)}")
    
    def _generate_config_fields(self, plugin_instance) -> str:
        """Generate HTML form fields for plugin configuration."""
        fields = []
        
        # Get configuration options from plugin if available
        if hasattr(plugin_instance, 'get_configuration_options'):
            config_options = plugin_instance.get_configuration_options()
            
            for option in config_options:
                option_name = option.get('name', '')
                option_type = option.get('type', 'string')
                display_name = option.get('display_name', option_name)
                default_value = option.get('default', '')
                description = option.get('description', '')
                required = option.get('required', False)
                
                # Get current value if available
                current_value = ''
                if hasattr(plugin_instance, 'config'):
                    current_value = plugin_instance.config.get(option_name, default_value)
                
                # Create form field based on type
                if option_type == 'string' or option_type == 'directory' or option_type == 'file':
                    # Text input
                    field = f""""
                    <div class="form-group">
                        <label class="form-label" for="{option_name}">{display_name}</label>
                        <input type="text" class="form-control" id="{option_name}" name="{option_name}" 
                               value="{current_value}" placeholder="{description}" {"required" if required else ""}>
                    </div>
                    """"
                elif option_type == 'boolean':
                    # Checkbox
                    checked = 'checked' if current_value else ''
                    field = f""""
                    <div class="form-group">
                        <div class="form-check">
                            <input type="checkbox" class="form-check-input" id="{option_name}" name="{option_name}" {checked}>
                            <label class="form-label" for="{option_name}">{display_name}</label>
                        </div>
                        <small>{description}</small>
                    </div>
                    """"
                elif option_type == 'integer':
                    # Number input
                    min_value = option.get('min', '')
                    max_value = option.get('max', '')
                    min_attr = f'min="{min_value}"' if min_value != '' else ''
                    max_attr = f'max="{max_value}"' if max_value != '' else ''
                    field = f""""
                    <div class="form-group">
                        <label class="form-label" for="{option_name}">{display_name}</label>
                        <input type="number" class="form-control" id="{option_name}" name="{option_name}" 
                               value="{current_value}" {min_attr} {max_attr} {"required" if required else ""}>
                        <small>{description}</small>
                    </div>
                    """"
                elif option_type == 'select':
                    # Select dropdown
                    options = option.get('options', [])
                    options_html = ''
                    for opt in options:
                        selected = 'selected' if opt == current_value else ''
                        options_html += f'<option value="{opt}" {selected}>{opt}</option>'
                    
                    field = f""""
                    <div class="form-group">
                        <label class="form-label" for="{option_name}">{display_name}</label>
                        <select class="form-control" id="{option_name}" name="{option_name}" {"required" if required else ""}>
                            {options_html}
                        </select>
                        <small>{description}</small>
                    </div>
                    """"
                elif option_type == 'array':
                    # Textarea for array (one item per line)
                    current_array = current_value
                    if isinstance(current_array, list):
                        current_array = '\n'.join(current_array)
                    
                    field = f""""
                    <div class="form-group">
                        <label class="form-label" for="{option_name}">{display_name}</label>
                        <textarea class="form-control" id="{option_name}" name="{option_name}" 
                                  rows="4" placeholder="One item per line" {"required" if required else ""}>{current_array}</textarea>
                        <small>{description}</small>
                    </div>
                    """"
                else:
                    # Default to text input
                    field = f""""
                    <div class="form-group">
                        <label class="form-label" for="{option_name}">{display_name}</label>
                        <input type="text" class="form-control" id="{option_name}" name="{option_name}" 
                               value="{current_value}" {"required" if required else ""}>
                        <small>{description}</small>
                    </div>
                    """"
                
                fields.append(field)
        
        return '\n'.join(fields)
    
    def _handle_test_plugin(self, query_params):
        """Handle API request to test a plugin."""
        try:
            plugin_id = query_params.get('id', [''])[0]
            
            if not plugin_id or plugin_id not in self.plugins_manager.plugins:
                self._send_json_response({
                    'success': False,
                    'message': f"Plugin {plugin_id} not found"
                })
                return
                
            # Load the plugin
            plugin_instance = self.plugins_manager.load_plugin(plugin_id)
            
            if not plugin_instance:
                self._send_json_response({
                    'success': False,
                    'message': f"Error loading plugin {plugin_id}"
                })
                return
                
            # Check if it's configured'
            is_configured, status_message = plugin_instance.is_configured() if hasattr(plugin_instance, 'is_configured') else (True, "")
            
            if not is_configured:
                self._send_json_response({
                    'success': False,
                    'message': f"Plugin is not configured: {status_message}"
                })
                return
                
            # Try running the plugin
            test_target = "test"
            
            # Set a timeout for the test
            test_result = {
                'success': False,
                'message': "Test timed out",
                'locations': []
            }
            
            def run_test():
                try:
                    locations = plugin_instance.collect_locations(test_target)
                    
                    test_result['success'] = True
                    test_result['message'] = f"Test successful: found {len(locations)} locations"
                    test_result['locations'] = locations
                except Exception as e:
                    test_result['success'] = False
                    test_result['message'] = f"Test failed: {str(e)}"
            
            # Run the test in a separate thread with timeout
            test_thread = threading.Thread(target=run_test)
            test_thread.daemon = True
            test_thread.start()
            test_thread.join(timeout=10)  # Wait up to 10 seconds
            
            # Format response
            self._send_json_response({
                'success': test_result['success'],
                'message': test_result['message'],
                'location_count': len(test_result['locations'])
            })
            
        except Exception as e:
            logger.error(f"Error testing plugin: {str(e)}")
            logger.error(traceback.format_exc())
            self._send_json_response({
                'success': False,
                'message': f"Error testing plugin: {str(e)}"
            })
    
    def _handle_save_config(self):
        """Handle API request to save plugin configuration."""
        try:
            # Parse form data
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            
            # Parse form data
            form_data = {}
            for field in post_data.split('&'):
                key, value = field.split('=', 1)
                form_data[key] = value
            
            plugin_id = form_data.get('plugin_id', '')
            
            if not plugin_id or plugin_id not in self.plugins_manager.plugins:
                self._send_json_response({
                    'success': False,
                    'message': f"Plugin {plugin_id} not found"
                })
                return
                
            # Load the plugin
            plugin_instance = self.plugins_manager.load_plugin(plugin_id)
            
            if not plugin_instance:
                self._send_json_response({
                    'success': False,
                    'message': f"Error loading plugin {plugin_id}"
                })
                return
                
            # Update configuration
            if hasattr(plugin_instance, 'config'):
                for key, value in form_data.items():
                    if key != 'plugin_id':
                        # Parse value based on expected type
                        plugin_instance.config[key] = value
                
                # Save configuration
                if hasattr(:
