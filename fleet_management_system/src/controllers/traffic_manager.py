import logging

class TrafficManager:
    """
    Manages traffic negotiation and collision avoidance between robots.
    Tracks lane and vertex occupancy to prevent conflicts and ensure smooth navigation.
    """
    def __init__(self, nav_graph):
        """
        Initialize the TrafficManager.

        :param nav_graph: The navigation graph representing the environment layout.
        """
        self.nav_graph = nav_graph
        self.lane_occupancy = {}  # Maps lane_idx to robot_id
        self.vertex_occupancy = {}  # Maps vertex_idx to list of robot_ids
        
    def occupy_lane(self, lane_idx, robot_id):
        """
        Mark a lane as occupied by a specific robot.

        :param lane_idx: The index of the lane to be occupied.
        :param robot_id: The ID of the robot occupying the lane.
        """
        if lane_idx in self.lane_occupancy:
            current_robot = self.lane_occupancy[lane_idx]
            if current_robot != robot_id:
                logging.warning(f"Lane {lane_idx} is occupied by {current_robot}, cannot assign to {robot_id}.")
                return False  # Deny access to occupied lane
        
        self.lane_occupancy[lane_idx] = robot_id
        logging.info(f"Lane {lane_idx} occupied by robot {robot_id}")
        return True
        
    def release_lane(self, lane_idx, robot_id):
        """
        Mark a lane as free, only if the correct robot releases it.

        :param lane_idx: The index of the lane to be released.
        :param robot_id: The ID of the robot releasing the lane.
        """
        if lane_idx in self.lane_occupancy and self.lane_occupancy[lane_idx] == robot_id:
            del self.lane_occupancy[lane_idx]
            logging.info(f"Lane {lane_idx} released by robot {robot_id}")
            return True
        logging.warning(f"Robot {robot_id} attempted to release lane {lane_idx}, but it was occupied by another robot.")
        return False
            
    def can_use_lane(self, robot, lane_idx):
        """
        Check if a robot can use a lane.

        :param robot: The robot attempting to use the lane.
        :param lane_idx: The index of the lane.
        :return: True if the lane is available, False otherwise.
        """
        return lane_idx not in self.lane_occupancy or self.lane_occupancy[lane_idx] == robot.id
        
    def occupy_vertex(self, vertex_idx, robot_id):
        """
        Mark a vertex as occupied by a robot.

        :param vertex_idx: The index of the vertex to be occupied.
        :param robot_id: The ID of the occupying robot.
        """
        if vertex_idx not in self.vertex_occupancy:
            self.vertex_occupancy[vertex_idx] = []
        if robot_id not in self.vertex_occupancy[vertex_idx]:
            self.vertex_occupancy[vertex_idx].append(robot_id)
        logging.info(f"Robot {robot_id} occupied vertex {vertex_idx}")
            
    def release_vertex(self, vertex_idx, robot_id):
        """
        Mark a vertex as no longer occupied by a robot.

        :param vertex_idx: The index of the vertex to be released.
        :param robot_id: The ID of the robot leaving the vertex.
        """
        if vertex_idx in self.vertex_occupancy and robot_id in self.vertex_occupancy[vertex_idx]:
            self.vertex_occupancy[vertex_idx].remove(robot_id)
            if not self.vertex_occupancy[vertex_idx]:  # Remove empty lists to keep dict clean
                del self.vertex_occupancy[vertex_idx]
            logging.info(f"Robot {robot_id} released vertex {vertex_idx}")
        else:
            logging.warning(f"Robot {robot_id} attempted to release vertex {vertex_idx}, but it was not occupied.")
                
    def is_vertex_occupied(self, vertex_idx):
        """
        Check if a vertex is occupied by any robot.

        :param vertex_idx: The index of the vertex.
        :return: True if the vertex is occupied, False otherwise.
        """
        return bool(self.vertex_occupancy.get(vertex_idx, []))  # Avoid KeyError
        
    def find_alternative_path(self, robot, target_vertex_idx, excluded_lanes=None):
        """
        Find an alternative path avoiding specified lanes.

        :param robot: The robot looking for an alternative path.
        :param target_vertex_idx: The target vertex the robot wants to reach.
        :param excluded_lanes: A list of lanes to avoid (optional).
        :return: A list representing the alternative path.
        """
        if excluded_lanes is None:
            excluded_lanes = set(self.lane_occupancy.keys())  # Avoid all occupied lanes
        return self.nav_graph.find_path(robot.current_vertex_idx, target_vertex_idx, excluded_lanes)
        
    def check_conflicts(self, robots):
        """
        Check for and resolve conflicts between robots.

        :param robots: A list of robots to check for conflicts.
        """
        conflicts = []
        for lane, robot_id in self.lane_occupancy.items():
            occupying_robot = next((r for r in robots if r.id == robot_id), None)
            if occupying_robot:
                for other_robot in robots:
                    if other_robot.id != robot_id and other_robot.current_lane_idx == lane:
                        conflicts.append((robot_id, other_robot.id))
        
        if conflicts:
            logging.warning(f"Traffic conflicts detected: {conflicts}")
            # Placeholder for future resolution (e.g., rerouting or priority-based waiting)
        else:
            logging.info("No traffic conflicts detected.")
        
    def get_lane_occupancy_status(self):
        """
        Get the current occupancy status of all lanes.

        :return: A dictionary mapping lane indices to occupying robots.
        """
        return dict(self.lane_occupancy)
        
    def get_vertex_occupancy_status(self):
        """
        Get the current occupancy status of all vertices.

        :return: A dictionary mapping vertex indices to occupying robots.
        """
        return {k: list(v) for k, v in self.vertex_occupancy.items()}
