#!/usr/bin/env python3
"""
Fleet Management System with Traffic Negotiation for Multi-Robots
Main entry point for the application
"""

import os
import sys
import logging
import argparse

from models.nav_graph import NavGraph
from controllers.fleet_manager import FleetManager
from controllers.traffic_manager import TrafficManager
from gui.fleet_gui import FleetGUI
from utils.helpers import setup_logging

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description='Fleet Management System')
    parser.add_argument('--nav-graph', type=str, default='data/nav_graph.json',
                        help='Path to navigation graph JSON file')
    parser.add_argument('--log-file', type=str, default='src/logs/fleet_logs.txt',
                        help='Path to log file')
    parser.add_argument('--debug', action='store_true',
                        help='Enable debug logging')
    return parser.parse_args()

def load_nav_graph(file_path):
    """Load navigation graph from JSON file"""
    if not os.path.exists(file_path):
        logging.error(f"Navigation graph file {file_path} not found.")
        sys.exit(1)
    try:
        return NavGraph(file_path)
    except Exception as e:
        logging.error(f"Failed to load navigation graph: {e}")
        sys.exit(1)

def main():
    """Main entry point for the application"""
    args = parse_arguments()
    
    os.makedirs(os.path.dirname(args.log_file), exist_ok=True)
    setup_logging(args.log_file, console_level=logging.DEBUG if args.debug else logging.INFO)
    
    logging.info(f"Loading navigation graph from {args.nav_graph}")
    nav_graph = load_nav_graph(args.nav_graph)
    
    logging.info(f"Loaded graph with {len(nav_graph.vertices)} vertices and {len(nav_graph.lanes)} lanes")
    
    logging.info("Initializing traffic manager")
    traffic_manager = TrafficManager(nav_graph)
    
    logging.info("Initializing fleet manager")
    fleet_manager = FleetManager(nav_graph, traffic_manager)
    
    logging.info("Starting GUI")
    try:
        gui = FleetGUI(nav_graph, fleet_manager, traffic_manager)
        gui.run()
    except Exception as e:
        logging.error(f"Error running GUI: {e}")

if __name__ == "__main__":
    main()