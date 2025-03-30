import time
from ..models.robot import Robot


class FleetManager:
    def __init__(self, nav_graph, log_file_path):
        self.nav_graph = nav_graph
        self.robots = {}
        self.next_robot_id = 0
        self.selected_robot = None
        self.log_file_path = log_file_path
        
        # Robot colors
        self.robot_colors = [
            (255, 0, 0),    # Red
            (0, 255, 0),    # Green
            (0, 0, 255),    # Blue
            (255, 255, 0),  # Yellow
            (255, 0, 255),  # Magenta
            (0, 255, 255),  # Cyan
            (255, 128, 0),  # Orange
            (128, 0, 128),  # Purple
            (0, 128, 0),    # Dark Green
            (128, 128, 0),  # Olive
            (128, 0, 0),    # Maroon
            (0, 128, 128),  # Teal
            (192, 192, 192), # Silver
            (128, 0, 64),   # Dark Pink
            (64, 128, 128), # Steel Blue
            (128, 64, 0),   # Brown
            (0, 64, 128),   # Navy Blue
            (128, 128, 255), # Light Blue
            (255, 128, 192), # Pink
            (128, 255, 128), # Light Green
            (255, 215, 0),   # Gold
            (165, 42, 42),   # Brown
            (219, 112, 147), # Pale Violet Red
            (0, 191, 255),   # Deep Sky Blue
        ]
        self._init_logging()
    
    def _init_logging(self):
        # Init log file
        try:
            with open(self.log_file_path, 'a') as f:
                f.write(f"Fleet Management System Log - {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            self.log_event("system", "Fleet Management System Started")
        except Exception as e:
            print(f"Error initializing log file: {e}")
    
    def log_event(self, source, message):
        # Log event to file
        try:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            with open(self.log_file_path, 'a') as f:
                f.write(f"[{timestamp}] [{source}] {message}\n")
        except Exception as e:
            print(f"Error writing to log file: {e}")
    
    def spawn_robot(self, vertex_id):
        # Spawn new robot at vertex
        if self.nav_graph.vertices[vertex_id]['occupying_robot'] is not None:
            self.log_event("system", f"Cannot spawn robot at vertex {vertex_id}: Vertex occupied")
            return None
        
        color_index = self.next_robot_id % len(self.robot_colors)
        robot_color = self.robot_colors[color_index]
        
        robot = Robot(self.next_robot_id, vertex_id, self.nav_graph, robot_color)
        self.robots[self.next_robot_id] = robot
        
        self.log_event(f"robot_{self.next_robot_id}", f"Spawned at vertex {vertex_id}")
        
        current_id = self.next_robot_id
        self.next_robot_id += 1
        
        return current_id
    
    def select_robot(self, x, y, tolerance=20):
        # Select robot at screen position
        min_distance = tolerance
        selected = None
        
        for robot_id, robot in self.robots.items():
            rx, ry = robot.position
            distance = ((rx - x) ** 2 + (ry - y) ** 2) ** 0.5
            
            if distance < min_distance:
                min_distance = distance
                selected = robot_id
        
        if selected is not None:
            self.selected_robot = selected
            self.log_event(f"robot_{selected}", "Selected for task assignment")
        
        return selected
    
    def assign_navigation_task(self, robot_id, destination_vertex):
        # Assign task to selected robot
        if robot_id not in self.robots:
            return False
        
        robot = self.robots[robot_id]
        success = robot.assign_task(destination_vertex)
        
        if success:
            source_vertex = robot.current_vertex
            self.log_event(f"robot_{robot.id}", 
                          f"Assigned navigation task from vertex {source_vertex} to {destination_vertex}")
            return True
        else:
            self.log_event(f"robot_{robot.id}", 
                          f"Failed to assign navigation task to vertex {destination_vertex}")
            return False
    
    def update(self, delta_time):
        # Update robots
        for robot_id, robot in self.robots.items():
            status_update = robot.update(delta_time)
            
            if status_update['event']:
                self.log_event(f"robot_{robot_id}", 
                              f"State: {status_update['state']}, Event: {status_update['event']}")
    
    def get_all_robot_statuses(self):
        # Get all robot status info
        return {robot_id: robot.get_status_display() for robot_id, robot in self.robots.items()}