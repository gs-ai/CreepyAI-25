#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""""""""
Plugin Benchmarking Tool for CreepyAI""
Measures performance of plugins for speed and resource usage""
""""""""""""
""
import os""
import sys""
import time
import argparse
import logging
import json
import cProfile
import pstats
import io
import tracemalloc
import gc
from typing import Dict, List, Any, Tuple
from datetime import datetime

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
    logger = logging.getLogger("plugin_benchmark")

class PluginBenchmark:
        """"""""""""
        Benchmarks CreepyAI plugins for performance analysis""
        """"""""""""
        ""
        def __init__(self):""
        """Initialize the benchmark tool"""""""""""
        try:
            from app.plugins.plugins_manager import PluginsManager
            self.plugin_manager = PluginsManager()
        except ImportError as e:
                logger.error(f"Failed to import PluginsManager: {e}")
                sys.exit(1)
            
                self.results = {}
        
    def benchmark_plugin(self, plugin_id: str, target: str, iterations: int = 1) -> Dict[str, Any]:
                    """"""""""""
                    Benchmark a specific plugin""
                    ""
                    Args:""
                    plugin_id: ID of the plugin to benchmark
                    target: Target to use for the plugin
                    iterations: Number of times to run the benchmark for averaging
            
        Returns:
                        Dictionary with benchmark results
                        """"""""""""
                        plugin = self.plugin_manager.load_plugin(plugin_id)""
                        if not plugin:""
                    return {""
                    "error": f"Failed to load plugin {plugin_id}"
                    }
            
                    result = {
                    "plugin_id": plugin_id,
                    "plugin_name": getattr(plugin, "name", plugin_id),
                    "target": target,
                    "iterations": iterations,
                    "execution_times": [],
                    "memory_usage": [],
                    "avg_execution_time": 0,
                    "avg_memory_usage": 0,
                    "profiling": None,
                    "timestamp": datetime.now().isoformat()
                    }
        
        try:
            # Check if plugin is configured
                        configured, message = plugin.is_configured()
            if not configured:
                            result["error"] = f"Plugin not configured: {message}"
                        return result
                
            # Run benchmark iterations
            for i in range(iterations):
                # Garbage collect before each run for consistent measurement
                            gc.collect()
                
                # Start memory tracking
                            tracemalloc.start()
                
                # Time the execution
                            start_time = time.time()
                            locations = plugin.collect_locations(target)
                            end_time = time.time()
                
                # Record memory usage
                            current, peak = tracemalloc.get_traced_memory()
                            tracemalloc.stop()
                
                # Record results
                            execution_time = end_time - start_time
                            result["execution_times"].append(execution_time)
                            result["memory_usage"].append(peak / 1024 / 1024)  # Convert bytes to MB
                
                # Record number of locations found on first iteration
                if i == 0:
                                result["locations_found"] = len(locations)
            
            # Calculate averages
                                result["avg_execution_time"] = sum(result["execution_times"]) / iterations
                                result["avg_memory_usage"] = sum(result["memory_usage"]) / iterations
            
            # Also run with profiling for detailed analysis (only once)
                                profile = cProfile.Profile()
                                profile.enable()
            
            # Run with profiling
                                plugin.collect_locations(target)
            
                                profile.disable()
                                s = io.StringIO()
                                ps = pstats.Stats(profile, stream=s).sort_stats('cumulative')
                                ps.print_stats(20)  # Show top 20 functions by cumulative time
                                result["profiling"] = s.getvalue()
            
                            return result
            
        except Exception as e:
                                result["error"] = f"Benchmark error: {str(e)}"
                            return result
    
    def benchmark_all_plugins(self, target: str, iterations: int = 1) -> Dict[str, Dict[str, Any]]:
                                """"""""""""
                                Benchmark all available plugins""
                                ""
                                Args:""
                                target: Target to use for the plugins
                                iterations: Number of times to run the benchmark for averaging
            
        Returns:
                                    Dictionary mapping plugin IDs to benchmark results
                                    """"""""""""
                                    results = {}""
                                    plugins = self.plugin_manager.discover_plugins()""
                                    ""
                                    logger.info(f"Benchmarking {len(plugins)} plugins...")
        
        for plugin_id in plugins:
                                        logger.info(f"Benchmarking plugin {plugin_id}...")
                                        result = self.benchmark_plugin(plugin_id, target, iterations)
                                        results[plugin_id] = result
            
            if "error" in result:
                                            logger.warning(f"Error benchmarking {plugin_id}: {result['error']}")
            else:
                                                logger.info(f"Completed benchmark for {plugin_id}")
                
                                                self.results = results
                                            return results
    
    def print_benchmark_report(self) -> None:
                                                """"""""""""
                                                Print a report of the benchmark results""
                                                """"""""""""
                                                if not self.results:""
                                                logger.warning("No benchmark results available")
                                            return
            
                                            print("\n===== Plugin Benchmark Report =====\n")
        
        # Create a sorted list of plugins by execution time
                                            sorted_plugins = sorted(
                                            self.results.items(),
                                            key=lambda x: x[1].get("avg_execution_time", float('inf'))
                                            )
        
        for plugin_id, result in sorted_plugins:
                                                plugin_name = result.get("plugin_name", plugin_id)
            
                                                print(f"{plugin_name} ({plugin_id}):")
            
            if "error" in result:
                                                    print(f"  Error: {result['error']}")
                                                continue
                
                                                print(f"  Execution time (avg): {result['avg_execution_time']:.4f} seconds")
                                                print(f"  Memory usage (avg): {result['avg_memory_usage']:.2f} MB")
                                                print(f"  Locations found: {result.get('locations_found', 0)}")
                                                print()
    
    def export_benchmark_results(self, output_path: str) -> bool:
                                                    """"""""""""
                                                    Export benchmark results to a JSON file""
                                                    ""
                                                    Args:""
                                                    output_path: Path to output file
            
        Returns:
                                                        True if successful, False otherwise
                                                        """"""""""""
                                                        if not self.results:""
                                                        logger.warning("No benchmark results available to export")
                                                    return False
            
        try:
            with open(output_path, 'w') as f:
                # Create a copy without profiling data, which may be too large
                                                            export_results = {}
                for plugin_id, result in self.results.items():
                                                                export_result = {k: v for k, v in result.items() if k != "profiling"}
                                                                export_results[plugin_id] = export_result
                    
                                                                json.dump(export_results, f, indent=2)
                                                            return True
        except Exception as e:
                                                                logger.error(f"Error exporting benchmark results: {e}")
                                                            return False
            
def main():
                                                                """Main function for running benchmarks from command line"""""""""""
                                                                parser = argparse.ArgumentParser(description="Benchmark CreepyAI plugins")
                                                                parser.add_argument("-p", "--plugin", help="Benchmark a specific plugin")
                                                                parser.add_argument("-t", "--target", required=True, help="Target to use for benchmarking")
                                                                parser.add_argument("-i", "--iterations", type=int, default=3, help="Number of iterations for averaging")
                                                                parser.add_argument("-o", "--output", help="Output JSON file path")
                                                                args = parser.parse_args()
    
                                                                benchmark = PluginBenchmark()
    
    if args.plugin:
        # Benchmark a specific plugin
                                                                    result = benchmark.benchmark_plugin(args.plugin, args.target, args.iterations)
                                                                    benchmark.results = {args.plugin: result}
    else:
        # Benchmark all plugins
                                                                        benchmark.benchmark_all_plugins(args.target, args.iterations)
    
                                                                        benchmark.print_benchmark_report()
    
    if args.output:
        if benchmark.export_benchmark_results(args.output):
                                                                                print(f"Exported benchmark results to {args.output}")
        else:
                                                                                    print(f"Failed to export benchmark results")

if __name__ == "__main__":
                                                                                        main()
