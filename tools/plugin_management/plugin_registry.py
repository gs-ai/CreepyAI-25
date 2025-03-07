#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
Plugin Registry CLI Tool for CreepyAI
Manage and query the plugin registry
"""

import os
import sys
import argparse
import json
import logging
from typing import Dict, List, Any

# Add parent directory to path so we can import plugins
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(SCRIPT_DIR)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("plugin_registry_tool")

def list_capabilities():
    """List all capabilities registered in the system"""
    try:
        from plugins.plugin_registry import registry
        
        capabilities = registry.get_capabilities()
        print("\n===== Registered Capabilities =====\n")
        
        if not capabilities:
            print("No capabilities registered")
            return
            
        for capability_name, capability_info in sorted(capabilities.items()):
            provider = capability_info.get('plugin', 'Unknown')
            description = capability_info.get('description', 'No description')
            print(f"{capability_name}:")
            print(f"  Provider: {provider}")
            print(f"  Description: {description}")
            
            # Show metadata if available and not empty
            metadata = capability_info.get('metadata')
            if metadata:
                print("  Metadata:")
                for key, value in metadata.items():
                    print(f"    {key}: {value}")
            print()
    except ImportError as e:
        print(f"Error importing plugin registry: {e}")
        return 1

def list_services():
    """List all services registered in the system"""
    try:
        from plugins.plugin_registry import registry
        
        services = registry.get_services()
        print("\n===== Registered Services =====\n")
        
        if not services:
            print("No services registered")
            return
            
        for service_name, service_info in sorted(services.items()):
            provider = service_info.get('plugin', 'Unknown')
            description = service_info.get('description', 'No description')
            signature = service_info.get('signature', '()')
            
            print(f"{service_name}{signature}:")
            print(f"  Provider: {provider}")
            print(f"  Description: {description}")
            print()
    except ImportError as e:
        print(f"Error importing plugin registry: {e}")
        return 1

def list_hooks():
    """List all hooks registered in the system"""
    try:
        from plugins.plugin_registry import registry
        
        hooks = registry.get_hooks()
        print("\n===== Registered Hooks =====\n")
        
        if not hooks:
            print("No hooks registered")
            return
            
        for hook_name, handlers in sorted(hooks.items()):
            print(f"{hook_name}:")
            print(f"  Handlers: {len(handlers)}")
            
            for handler in handlers:
                print(f"    - {handler.get('plugin', 'Unknown')}")
            print()
    except ImportError as e:
        print(f"Error importing plugin registry: {e}")
        return 1

def get_statistics():
    """Show statistics about the registry"""
    try:
        from plugins.plugin_registry import registry
        
        stats = registry.get_statistics()
        print("\n===== Registry Statistics =====\n")
        
        print(f"Capabilities: {stats.get('capabilities_count', 0)}")
        print(f"Services: {stats.get('services_count', 0)}")
        print(f"Hooks: {stats.get('hooks_count', 0)}")
        print(f"Data types: {stats.get('data_types_count', 0)}")
        print(f"File extensions: {stats.get('extensions_count', 0)}")
        print(f"Integrations: {stats.get('integrations_count', 0)}")
        
        # Show service calls if any
        service_calls = stats.get('service_calls', {})
        if service_calls:
            print("\nService Calls:")
            for service_name, count in sorted(service_calls.items(), key=lambda x: x[1], reverse=True):
                print(f"  {service_name}: {count}")
        
        # Show hook invocations if any
        hook_invocations = stats.get('hook_invocations', {})
        if hook_invocations:
            print("\nHook Invocations:")
            for hook_name, count in sorted(hook_invocations.items(), key=lambda x: x[1], reverse=True):
                print(f"  {hook_name}: {count}")
                
    except ImportError as e:
        print(f"Error importing plugin registry: {e}")
        return 1

def call_service(service_name, *args):
    """Call a registered service and display the result"""
    try:
        from plugins.plugin_registry import registry
        
        print(f"Calling service: {service_name}{str(args)}")
        try:
            result = registry.call_service(service_name, *args)
            print("\nResult:")
            print(result)
        except KeyError:
            print(f"Error: Service '{service_name}' not found")
            return 1
        except Exception as e:
            print(f"Error calling service: {e}")
            return 1
            
    except ImportError as e:
        print(f"Error importing plugin registry: {e}")
        return 1

def invoke_hook(hook_name, data):
    """Invoke a hook with the provided data and display the results"""
    try:
        from plugins.plugin_registry import registry
        
        print(f"Invoking hook: {hook_name}")
        results = registry.invoke_hook(hook_name, data)
        
        if not results:
            print("No handlers responded to the hook")
            return
            
        print("\nResults:")
        for plugin_name, result in results.items():
            print(f"\n{plugin_name}:")
            print(result)
            
    except ImportError as e:
        print(f"Error importing plugin registry: {e}")
        return 1

def register_capability(plugin_name, capability_name, description, metadata=None):
    """Register a new capability"""
    try:
        from plugins.plugin_registry import registry
        
        metadata = metadata or {}
        success = registry.register_capability(plugin_name, capability_name, description, metadata)
        
        if success:
            print(f"Successfully registered capability '{capability_name}' for plugin '{plugin_name}'")
        else:
            print(f"Failed to register capability '{capability_name}' (might already be registered)")
            return 1
            
    except ImportError as e:
        print(f"Error importing plugin registry: {e}")
        return 1

def main():
    """Main function for the registry tool"""
    parser = argparse.ArgumentParser(description="CreepyAI Plugin Registry Tool")
    
    subparsers = parser.add_subparsers(dest='command', help='Command to run')
    
    # List capabilities command
    list_cap_parser = subparsers.add_parser('list-capabilities', help='List all registered capabilities')
    
    # List services command
    list_svc_parser = subparsers.add_parser('list-services', help='List all registered services')
    
    # List hooks command
    list_hooks_parser = subparsers.add_parser('list-hooks', help='List all registered hooks')
    
    # Get statistics command
    stats_parser = subparsers.add_parser('stats', help='Show registry statistics')
    
    # Call service command
    call_parser = subparsers.add_parser('call', help='Call a registered service')
    call_parser.add_argument('service', help='Name of the service to call')
    call_parser.add_argument('args', nargs='*', help='Arguments to pass to the service')
    
    # Invoke hook command
    hook_parser = subparsers.add_parser('hook', help='Invoke a hook')
    hook_parser.add_argument('hook', help='Name of the hook to invoke')
    hook_parser.add_argument('data', help='JSON data string to pass to the hook')
    
    # Register capability command
    reg_parser = subparsers.add_parser('register', help='Register a new capability')
    reg_parser.add_argument('plugin', help='Name of the plugin registering the capability')
    reg_parser.add_argument('capability', help='Name of the capability')
    reg_parser.add_argument('description', help='Description of the capability')
    reg_parser.add_argument('--metadata', help='JSON string with metadata')
    
    args = parser.parse_args()
    
    # Execute the appropriate command
    if args.command == 'list-capabilities':
        return list_capabilities()
    elif args.command == 'list-services':
        return list_services()
    elif args.command == 'list-hooks':
        return list_hooks()
    elif args.command == 'stats':
        return get_statistics()
    elif args.command == 'call':
        return call_service(args.service, *args.args)
    elif args.command == 'hook':
        try:
            data = json.loads(args.data)
            return invoke_hook(args.hook, data)
        except json.JSONDecodeError:
            print("Error: data must be valid JSON")
            return 1
    elif args.command == 'register':
        metadata = {}
        if args.metadata:
            try:
                metadata = json.loads(args.metadata)
            except json.JSONDecodeError:
                print("Error: metadata must be valid JSON")
                return 1
        return register_capability(args.plugin, args.capability, args.description, metadata)
    else:
        parser.print_help()
        return 0

if __name__ == "__main__":
    sys.exit(main())
