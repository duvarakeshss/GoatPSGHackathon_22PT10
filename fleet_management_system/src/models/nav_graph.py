import json
import numpy as np
import logging

class NavGraph:
    """
    Represents the navigation graph for robots to navigate through.
    This class loads a JSON-based navigation graph, storing vertices (nodes)
    and lanes (edges). It provides methods for pathfinding, lane occupancy tracking,
    and vertex management.
    """
    def __init__(self, json_file_path):
        """
        Initialize the navigation graph by loading data from a JSON file.
        
        :param json_file_path: Path to the JSON file containing graph data.
        """
        self.vertices = []  # List of vertices (x, y, attributes)
        self.lanes = []     # List of lanes [from_idx, to_idx]
        self.vertex_names = {}  # Maps vertex names to indices
        self.lane_occupancy = {}  # Tracks occupied lanes
        self.load_from_json(json_file_path)
        
    def load_from_json(self, json_file_path):
        """
        Load navigation graph data from a JSON file.
        
        :param json_file_path: Path to the JSON file.
        """
        try:
            with open(json_file_path, 'r') as file:
                data = json.load(file)
            
            # Support both flat and hierarchical (level-based) structures
            if "levels" in data:
                level_data = data["levels"].get("level1", {})  # Adjust this if using multiple levels
            else:
                level_data = data

            self.vertices = level_data.get('vertices', [])
            self.lanes = level_data.get('lanes', [])

            # Map vertex names to indices
            for i, vertex in enumerate(self.vertices):
                if len(vertex) >= 3 and isinstance(vertex[2], dict) and 'name' in vertex[2]:
                    self.vertex_names[vertex[2]['name']] = i

            logging.info(f"Loaded navigation graph with {len(self.vertices)} vertices and {len(self.lanes)} lanes")
        except Exception as e:
            logging.error(f"Failed to load navigation graph: {e}")
            raise

            
    def get_vertex_position(self, vertex_idx):
        """Get the (x, y) position of a vertex."""
        if 0 <= vertex_idx < len(self.vertices):
            return self.vertices[vertex_idx][0], self.vertices[vertex_idx][1]
        return None
        
    def get_vertex_by_name(self, name):
        """Get the index of a vertex by its name."""
        return self.vertex_names.get(name)
        
    def get_vertex_attributes(self, vertex_idx):
        """Get attributes of a vertex."""
        if 0 <= vertex_idx < len(self.vertices) and len(self.vertices[vertex_idx]) >= 3:
            return self.vertices[vertex_idx][2]
        return {}
        
    def is_charger(self, vertex_idx):
        """Check if a vertex is a charging station."""
        attrs = self.get_vertex_attributes(vertex_idx)
        return attrs.get('is_charger', False)
        
    def get_neighbors(self, vertex_idx):
        """Get neighboring vertices of a given vertex."""
        neighbors = []
        for lane in self.lanes:
            if lane[0] == vertex_idx:
                neighbors.append(lane[1])
            elif lane[1] == vertex_idx:
                neighbors.append(lane[0])
        return neighbors
        
    def find_path(self, start_idx, goal_idx):
        """Find a path from start to goal using Breadth-First Search (BFS)."""
        if start_idx == goal_idx:
            return [start_idx]
            
        visited = set([start_idx])
        queue = [[start_idx]]
        
        while queue:
            path = queue.pop(0)
            current = path[-1]
            
            for neighbor in self.get_neighbors(current):
                if neighbor == goal_idx:
                    return path + [neighbor]
                if neighbor not in visited:
                    visited.add(neighbor)
                    queue.append(path + [neighbor])
        
        logging.warning(f"No path found from {start_idx} to {goal_idx}")
        return None  # No path found
        
    def occupy_lane(self, lane_idx, robot_id):
        """Mark a lane as occupied by a robot."""
        self.lane_occupancy[lane_idx] = robot_id
        
    def release_lane(self, lane_idx):
        """Mark a lane as unoccupied."""
        if lane_idx in self.lane_occupancy:
            del self.lane_occupancy[lane_idx]
            
    def is_lane_occupied(self, lane_idx):
        """Check if a lane is occupied."""
        return lane_idx in self.lane_occupancy
        
    def get_lane_index(self, from_idx, to_idx):
        """Get the index of a lane between two vertices."""
        for i, lane in enumerate(self.lanes):
            if (lane[0] == from_idx and lane[1] == to_idx) or (lane[0] == to_idx and lane[1] == from_idx):
                return i
        return None
        
    def get_nearest_vertex(self, position):
        """Find the vertex closest to a given position using Euclidean distance."""
        if not self.vertices:
            return None
        
        positions = np.array(self.vertices)[:, :2]  # Extract x, y
        distances = np.linalg.norm(positions - np.array(position), axis=1)
        return np.argmin(distances)
