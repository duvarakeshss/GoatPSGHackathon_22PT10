import os
import sys
import time
import pygame
import argparse

# Add root directory to system path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import required modules
from src.models.nav_graph import NavGraph
from src.models.robot import Robot
from src.controllers.fleet_manager import FleetManager
from src.controllers.traffic_manager import TrafficManager
from src.gui.fleet_gui import FleetGUI

def run():
    # Set up command line argument parser
    cmd_parser = argparse.ArgumentParser(description='Fleet Management System')
    cmd_parser.add_argument('--nav_graph', type=str, default='data/nav_graph.json',
                        help='Path to navigation graph JSON file')
    cmd_parser.add_argument('--log_file', type=str, default='src/logs/fleet_logs.txt',
                        help='Path to log file')
    cmd_parser.add_argument('--width', type=int, default=1000,
                        help='Window width')
    cmd_parser.add_argument('--height', type=int, default=800,
                        help='Window height')
    
    # Parse command line arguments
    config = cmd_parser.parse_args()
    
    # Create log directory if it doesn't exist
    os.makedirs(os.path.dirname(config.log_file), exist_ok=True)
    
    # Initialize application components
    try:
        # Load navigation map from file
        navigation_map = NavGraph(config.nav_graph)
        
        # Create traffic control system
        movement_coordinator = TrafficManager(navigation_map)
        
        # Create fleet management controller
        robot_controller = FleetManager(navigation_map, config.log_file)
        
        # Set up graphical interface
        display = FleetGUI(config.width, config.height, navigation_map, robot_controller, movement_coordinator)
        
        # Display startup information
        display.add_message("Fleet Management System initialized")
        display.add_message("Press S for Spawn mode, A for Assign mode")
        display.add_log("System started")
        display.add_log(f"Loaded nav graph with {len(navigation_map.vertices)} vertices")
        
        # Begin main application loop
        is_active = True
        previous_timestamp = time.time()
        
        while is_active:
            # Calculate time between frames
            current_timestamp = time.time()
            frame_time = current_timestamp - previous_timestamp
            previous_timestamp = current_timestamp
            
            # Process user input and window events
            is_active = display.handle_events()
            
            # Update system state
            robot_controller.update(frame_time)
            traffic_report = movement_coordinator.update()
            display.update(frame_time)
            
            # Record significant traffic events
            if traffic_report['deadlocks_resolved'] > 0:
                display.add_log(f"Resolved {traffic_report['deadlocks_resolved']} traffic deadlocks")
            
            # Draw updated state to screen
            display.render()
            
            # Maintain consistent frame rate (60fps)
            pygame.time.delay(60)
        
        # Perform cleanup when exiting
        pygame.quit()
        
    except Exception as e:
        # Handle any errors
        print(f"Error: {e}")
        pygame.quit()
        sys.exit(1)

# Execute main function when script is run directly
if __name__ == "__main__":
    run()