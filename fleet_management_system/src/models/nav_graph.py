import json
import networkx as nx
import numpy as np
from ..utils.helpers import find_path_astar

class NavGraph:
    # Graph for robot navigation
    
    def __init__(self, json_file_path):
        # Init graph from JSON
        self.graph = nx.DiGraph()
        self.vertices = []
        self.lanes = []
        self.scale_factor = 50  # For vizulation
        self.offset_x = 300     # X offset
        self.offset_y = 300     # Y offset
        self.reserved_paths = {}  # Store active paths: robot_id -> path
        self.destination_reservations = {}  # Store destination reservations: vertex_id -> robot_id
        
        self.load_from_json(json_file_path)

    def load_from_json(self, json_file_path):
        # Load graph data from JSON
        try:
            with open(json_file_path, 'r') as f:
                data = json.load(f)
            
            # Get first level
            level_name = list(data['levels'].keys())[0]
            level_data = data['levels'][level_name]
            
            # Load vertices
            self.vertices = []
            for i, vertex_data in enumerate(level_data['vertices']):
                x, y, attrs = vertex_data
                
                name = attrs.get('name', f'v{i}')
                is_charger = attrs.get('is_charger', False)
                
                vertex = {
                    'id': i,
                    'x': x,
                    'y': y,
                    'name': name,
                    'is_charger': is_charger,
                    'occupying_robot': None
                }
                self.vertices.append(vertex)
                self.graph.add_node(i, **vertex)
            
            # Load lanes
            self.lanes = []
            for lane_data in level_data['lanes']:
                from_vertex, to_vertex, attrs = lane_data
                
                speed_limit = attrs.get('speed_limit', 0)
                
                lane = {
                    'from_vertex': from_vertex,
                    'to_vertex': to_vertex,
                    'speed_limit': speed_limit,
                    'occupying_robot': None,
                    'is_blocked': False
                }
                self.lanes.append(lane)
                self.graph.add_edge(from_vertex, to_vertex, **lane)
            
            self.calculate_bounds()
            
            print(f"Loaded navigation graph with {len(self.vertices)} vertices and {len(self.lanes)} lanes")
            
        except Exception as e:
            print(f"Error loading navigation graph: {e}")
            raise
    
    def calculate_bounds(self):
        # Calc viz bounds
        if not self.vertices:
            return
        
        # Use numpy for faster array operations
        coords = np.array([[v['x'], v['y']] for v in self.vertices])
        self.min_x, self.min_y = np.min(coords, axis=0)
        self.max_x, self.max_y = np.max(coords, axis=0)
        
        padding = 3.0
        dimensions = np.array([
            self.max_x - self.min_x,
            self.max_y - self.min_y
        ]) + padding
        
        screen_dims = np.array([800, 600])
        margins = np.array([100, 100])
        
        if np.all(dimensions > 0):
            self.scale_factor = min(
                (screen_dims - 2 * margins) / dimensions
            )
        
        self.offset_x = margins[0] + (screen_dims[0] - 2*margins[0] - dimensions[0] * self.scale_factor) / 2
        self.offset_y = margins[1] + (screen_dims[1] - 2*margins[1] - dimensions[1] * self.scale_factor) / 2

    def get_scaled_position(self, vertex_id, zoom_level=1.0, center_point=None):
        # Get scaled vertex position
        vertex = self.vertices[vertex_id]
        x = (vertex['x'] - self.min_x) * self.scale_factor + self.offset_x
        y = (vertex['y'] - self.min_y) * self.scale_factor + self.offset_y
        
        if zoom_level != 1.0 and center_point is not None:
            if isinstance(center_point, tuple) and len(center_point) == 2:
                center_x, center_y = center_point
                rel_x = x - center_x
                rel_y = y - center_y
                x = center_x + rel_x * zoom_level
                y = center_y + rel_y * zoom_level
        
        return (int(x), int(y))
    
    def get_vertex_at_position(self, x, y, tolerance=15):
        # Find vertex at screen pos
        for vertex in self.vertices:
            pos_x, pos_y = self.get_scaled_position(vertex['id'])
            distance = np.sqrt((pos_x - x)**2 + (pos_y - y)**2)
            if distance <= tolerance:
                return vertex['id']
        return None
    
    def is_vertex_available(self, vertex_id, robot_id):
        # Check if vertex is already reserved
        if vertex_id in self.destination_reservations:
            return self.destination_reservations[vertex_id] == robot_id
            
        # Check if vertex is currently occupied
        vertex = self.vertices[vertex_id]
        if vertex['occupying_robot'] is not None:
            return vertex['occupying_robot'] == robot_id
            
        # Check if vertex is part of another robot's path
        for path_robot_id, path in self.reserved_paths.items():
            if path_robot_id != robot_id and vertex_id in path:
                return False
                
        return True

    def get_shortest_path(self, start_vertex, end_vertex, robot_id=None):
        # Check if destination is already reserved by another robot
        if robot_id is not None and end_vertex in self.destination_reservations:
            if self.destination_reservations[end_vertex] != robot_id:
                return None
            
        path = find_path_astar(self.graph, start_vertex, end_vertex)
        if not path:
            return None
        
        return path

    def get_alternative_paths(self, start_vertex, end_vertex, max_paths=3):
        """Get alternative paths between two vertices."""
        paths = []
        if start_vertex == end_vertex:
            return [[start_vertex]]
            
        # Get the primary shortest path
        primary_path = self.get_shortest_path(start_vertex, end_vertex)
        if primary_path:
            paths.append(primary_path)
            
        # Try to find alternative paths by temporarily removing edges
        temp_graph = self.graph.copy()
        
        for _ in range(max_paths - 1):
            if not paths:
                break
                
            # Remove a random edge from the last found path
            last_path = paths[-1]
            for i in range(len(last_path) - 1):
                temp_graph.remove_edge(last_path[i], last_path[i + 1])
                
            # Try to find a new path in the modified graph
            try:
                alt_path = find_path_astar(temp_graph, start_vertex, end_vertex)
                if alt_path and alt_path not in paths:
                    paths.append(alt_path)
            except:
                break
                
        return paths

    def reserve_path(self, robot_id, path):
        if not path:
            return False
        
        # Check if destination is already taken
        end_vertex = path[-1]
        if end_vertex in self.destination_reservations and self.destination_reservations[end_vertex] != robot_id:
            return False
        
        # Reserve the path
        self.reserved_paths[robot_id] = path
        self.destination_reservations[end_vertex] = robot_id
        
        # Reserve initial vertex
        if not self.reserve_vertex(path[0], robot_id):
            return False
            
        return True

    def reserve_lane(self, from_vertex, to_vertex, robot_id):
        for lane in self.lanes:
            if lane['from_vertex'] == from_vertex and lane['to_vertex'] == to_vertex:
                if lane['occupying_robot'] is None and not lane['is_blocked']:
                    lane['occupying_robot'] = robot_id
                    return True
                return lane['occupying_robot'] == robot_id
        return False

    def reserve_vertex(self, vertex_id, robot_id):
        if vertex_id >= len(self.vertices):
            return False
            
        vertex = self.vertices[vertex_id]
        if vertex['occupying_robot'] is None:
            vertex['occupying_robot'] = robot_id
            return True
        return vertex['occupying_robot'] == robot_id

    def reserve_path(self, robot_id, path):
        if not path:
            return False
            
        # Check if destination is already taken
        end_vertex = path[-1]
        if end_vertex in self.destination_reservations and self.destination_reservations[end_vertex] != robot_id:
            return False
            
        # Check conflicts with other robots' paths
        for other_id, other_path in self.reserved_paths.items():
            if other_id != robot_id:
                if set(path[1:]).intersection(set(other_path[1:])):
                    return False
        
        self.reserved_paths[robot_id] = path
        self.destination_reservations[end_vertex] = robot_id
        
        # Reserve first vertex
        self.reserve_vertex(path[0], robot_id)
        return True

    def release_vertex(self, vertex_id, robot_id):
        if vertex_id in self.vertices:
            vertex = self.vertices[vertex_id]
            if vertex['occupying_robot'] == robot_id:
                vertex['occupying_robot'] = None
                return True
        return False

    def release_lane(self, from_vertex, to_vertex, robot_id):
        for lane in self.lanes:
            if (lane['from_vertex'] == from_vertex and 
                lane['to_vertex'] == to_vertex and 
                lane['occupying_robot'] == robot_id):
                lane['occupying_robot'] = None
                return True
        return False

    def clear_path(self, robot_id):
        if robot_id in self.reserved_paths:
            path = self.reserved_paths[robot_id]
            if path[-1] in self.destination_reservations:
                del self.destination_reservations[path[-1]]
            del self.reserved_paths[robot_id]