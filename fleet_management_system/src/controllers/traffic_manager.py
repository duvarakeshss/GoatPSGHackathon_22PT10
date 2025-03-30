import time
class TrafficManager:
    # Manages traffic and collision avoidance
    
    SAFETY_TIME_GAP = 3  # Min seconds between robots
    
    def __init__(self, nav_graph):
        self.nav_graph = nav_graph
        self.lane_reservations = {}  # (from, to): (robot_id, until)
        
        # Initialize traffic manager in nav_graph
        nav_graph.traffic_manager = self
    
    def check_path_conflicts(self, robot_id, path):
        current_time = time.time()
        
        # Check each segment of the path
        for i in range(len(path) - 1):
            from_vertex, to_vertex = path[i], path[i+1]
            
            # Check if lane is already reserved
            if (from_vertex, to_vertex) in self.lane_reservations:
                reserved_robot, reserved_until = self.lane_reservations[(from_vertex, to_vertex)]
                if reserved_robot != robot_id and current_time < reserved_until:
                    return True
            
            # Check for head-on collisions
            if (to_vertex, from_vertex) in self.lane_reservations:
                return True
        
        return False
    
    def reserve_lane(self, robot_id, from_vertex, to_vertex, arrival_time):
        # Reserve lane for robot
        self.lane_reservations[(from_vertex, to_vertex)] = (robot_id, arrival_time + self.SAFETY_TIME_GAP)
        return True
    
    def update(self):
        # Update traffic system
        return {
            'deadlocks_resolved': 0,
            'lane_reservations': self.lane_reservations
        }
