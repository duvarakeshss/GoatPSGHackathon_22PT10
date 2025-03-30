import logging
import uuid
from models.robot import Robot

class FleetManager:
    def __init__(self, nav_graph, traffic_manager):
        self.nav_graph = nav_graph
        self.traffic_manager = traffic_manager
        self.robots = {}
        self.robot_colors = {}
        self.next_robot_id = 1

    def spawn_robot(self, vertex_idx, color=None):
        if not self.nav_graph.is_valid_vertex(vertex_idx):
            logging.error(f"Invalid spawn location: Vertex {vertex_idx} does not exist.")
            return None

        robot_id = f"R{self.next_robot_id}"
        self.next_robot_id += 1

        robot = Robot(robot_id, vertex_idx, self.nav_graph, color)
        self.robots[robot_id] = robot

        logging.info(f"Spawned robot {robot_id} at vertex {vertex_idx}")
        return robot

    def assign_task(self, robot_id, target_vertex_idx):
        if robot_id not in self.robots:
            logging.error(f"Task assignment failed: Robot {robot_id} not found.")
            return False

        if not self.nav_graph.is_valid_vertex(target_vertex_idx):
            logging.error(f"Invalid task: Target vertex {target_vertex_idx} does not exist.")
            return False

        robot = self.robots[robot_id]
        
        if robot.status == self.RobotStatus.MOVING:
            logging.warning(f"Robot {robot_id} is already in motion and cannot take a new task.")
            return False
        
        success = robot.assign_task(target_vertex_idx)
        if success:
            logging.info(f"Task assigned: Robot {robot_id} moving to vertex {target_vertex_idx}.")
        else:
            logging.warning(f"Task assignment failed: No path found for Robot {robot_id}.")
        
        return success

    def update_all_robots(self):
        for robot_id, robot in self.robots.items():
            robot.update(self.traffic_manager)

    def get_robot_by_position(self, position, radius=10):
        import math
        nearest_robot = None
        min_dist = float('inf')

        for robot in self.robots.values():
            dist = math.dist(robot.position, position)
            if dist <= radius and dist < min_dist:
                nearest_robot = robot
                min_dist = dist

        return nearest_robot

    def get_robot_statuses(self):
        return {robot_id: robot.status for robot_id, robot in self.robots.items()}

    def get_active_tasks(self):
        return [
            {
                'robot_id': robot_id,
                'from_vertex': robot.current_vertex_idx,
                'to_vertex': robot.target_vertex_idx,
                'status': robot.status
            }
            for robot_id, robot in self.robots.items() if robot.target_vertex_idx is not None
        ]
