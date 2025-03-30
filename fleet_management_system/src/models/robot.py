import logging
import time
import uuid

class RobotStatus:
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    CHARGING = "charging"
    TASK_COMPLETE = "task_complete"

class Robot:
    def __init__(self, robot_id, start_vertex_idx, nav_graph, color=None):
        self.id = robot_id or str(uuid.uuid4())[:8]
        self.nav_graph = nav_graph
        self.current_vertex_idx = start_vertex_idx
        self.target_vertex_idx = None
        self.status = RobotStatus.IDLE
        self.path = []
        self.current_path_index = 0
        self.current_lane_idx = None
        self.color = color or self._generate_random_color()
        self.position = nav_graph.get_vertex_position(start_vertex_idx)
        self.progress = 0.0  # Progress along the lane
        self.speed = 0.05  # Movement speed
        self.waiting_since = None  
        logging.info(f"Robot {self.id} initialized at vertex {start_vertex_idx}")
        
    def _generate_random_color(self):
        import random
        return (random.randint(50, 200), random.randint(50, 200), random.randint(50, 200))
        
    def assign_task(self, target_vertex_idx):
        self.target_vertex_idx = target_vertex_idx
        self.path = self.nav_graph.find_path(self.current_vertex_idx, target_vertex_idx)
        self.current_path_index = 0
        self.progress = 0.0
        
        if self.path:
            self.status = RobotStatus.MOVING
            logging.info(f"Robot {self.id} moving from {self.current_vertex_idx} to {target_vertex_idx}")
            return True
        else:
            logging.warning(f"Robot {self.id} could not find a path to {target_vertex_idx}")
            return False
            
    def update(self, traffic_manager):
        if self.status in {RobotStatus.IDLE, RobotStatus.TASK_COMPLETE, RobotStatus.CHARGING}:
            return
        
        if self.status == RobotStatus.WAITING:
            next_vertex = self.path[self.current_path_index + 1]
            lane_idx = self.nav_graph.get_lane_index(self.current_vertex_idx, next_vertex)
            
            if traffic_manager.can_use_lane(self, lane_idx):
                self.status = RobotStatus.MOVING
                self.current_lane_idx = lane_idx
                traffic_manager.occupy_lane(lane_idx, self.id)
                self.waiting_since = None
                logging.info(f"Robot {self.id} resumed movement on lane {lane_idx}")
            elif self.waiting_since and time.time() - self.waiting_since > 10:
                self.path = self.nav_graph.find_path(self.current_vertex_idx, self.target_vertex_idx)
                self.current_path_index = 0
                self.progress = 0.0
                logging.info(f"Robot {self.id} recalculated path")
            return
        
        if self.status == RobotStatus.MOVING:
            if self.current_path_index < len(self.path) - 1:
                current_vertex = self.path[self.current_path_index]
                next_vertex = self.path[self.current_path_index + 1]
                
                lane_idx = self.nav_graph.get_lane_index(current_vertex, next_vertex)
                if lane_idx is None:
                    logging.error(f"Robot {self.id} cannot find lane from {current_vertex} to {next_vertex}")
                    self.status = RobotStatus.IDLE
                    return
                if not traffic_manager.can_use_lane(self, lane_idx):
                    self.status = RobotStatus.WAITING
                    self.waiting_since = self.waiting_since or time.time()
                    logging.info(f"Robot {self.id} waiting for lane {lane_idx}")
                    return
                
                self.current_lane_idx = lane_idx
                traffic_manager.occupy_lane(lane_idx, self.id)
                start_pos = self.nav_graph.get_vertex_position(current_vertex)
                end_pos = self.nav_graph.get_vertex_position(next_vertex)
                
                self.progress += self.speed
                if self.progress >= 1.0:
                    self.progress = 0.0
                    self.current_path_index += 1
                    self.current_vertex_idx = next_vertex
                    self.position = end_pos
                    traffic_manager.release_lane(self.current_lane_idx)
                    self.current_lane_idx = None
                    logging.info(f"Robot {self.id} arrived at {next_vertex}")
                    
                    if next_vertex == self.target_vertex_idx:
                        self.status = RobotStatus.TASK_COMPLETE
                        logging.info(f"Robot {self.id} completed its task")
                else:
                    self.position = (
                        start_pos[0] + (end_pos[0] - start_pos[0]) * self.progress,
                        start_pos[1] + (end_pos[1] - start_pos[1]) * self.progress
                    )
                    
    def get_status_display(self):
        if self.status == RobotStatus.WAITING and self.waiting_since:
            wait_time = time.time() - self.waiting_since
            return f"{self.status} ({int(wait_time)}s)"
        return self.status
