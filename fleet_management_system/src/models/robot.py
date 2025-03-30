import time
import numpy as np
from ..utils.helpers import format_time

class Robot:
    """Robot class for the fleet management system."""
    
    # Define possible robot states
    IDLE = "idle"
    MOVING = "moving"
    WAITING = "waiting"
    CHARGING = "charging"
    COMPLETED = "completed"
    
    
    def __init__(self, robot_id, start_vertex, nav_graph, color):
        self.id = robot_id
        self.current_vertex = start_vertex
        self.nav_graph = nav_graph
        self.color = color
        self.state = self.IDLE
        self.path = []
        self.current_path_index = 0
        self.target_vertex = None
        
        self.position = nav_graph.get_scaled_position(start_vertex)
        self.target_position = self.position
        self.move_speed = 10.0  # pixels per second
        self.last_action_time = time.time()
        self.paused = False
        self.last_action_time = time.time()
        self.paused = False
        
        # Reserve starting position
        self.nav_graph.reserve_vertex(start_vertex, self.id)

    def assign_task(self, destination_vertex):
        if self.state not in [self.IDLE, self.COMPLETED]:
            return False
            
        # Check if destination is already assigned to another robot
        for vertex in self.nav_graph.vertices:
            if vertex.get('occupying_robot') is not None and vertex['id'] == destination_vertex:
                return False
        
        # Get path and check for collisions
        path = self.nav_graph.get_shortest_path(self.current_vertex, destination_vertex, self.id)
        if not path:
            return False
            
        # Reserve path
        if not self.nav_graph.reserve_path(self.id, path):
            return False
        
        self.path = path
        self.current_path_index = 0
        self.target_vertex = destination_vertex
        self.state = self.MOVING
        self.target_position = self.nav_graph.get_scaled_position(path[1])
        return True

    def update(self, delta_time):
        status_update = {
            'robot_id': self.id,
            'state': self.state,
            'position': self.current_vertex,
            'event': None
        }
        
        if self.state == self.MOVING and self.path:
            # Move towards target position
            dx = self.target_position[0] - self.position[0]
            dy = self.target_position[1] - self.position[1]
            distance = np.sqrt(dx*dx + dy*dy)
            
            if distance < self.move_speed:
                # Reached next vertex
                self.current_path_index += 1
                self.position = self.target_position
                self.current_vertex = self.path[self.current_path_index]
                
                if self.current_path_index >= len(self.path) - 1:
                    # Reached final destination
                    self.state = self.COMPLETED
                    status_update['event'] = 'reached_destination'
                else:
                    # Check next move with traffic manager
                    next_vertex = self.path[self.current_path_index + 1]
                    arrival_time = time.time() + (distance / self.move_speed)
                    
                    if self.nav_graph.traffic_manager.reserve_lane(self.id, self.current_vertex, next_vertex, arrival_time):
                        self.target_position = self.nav_graph.get_scaled_position(next_vertex)
                        status_update['event'] = f'moving_to_{next_vertex}'
                    else:
                        self.state = self.WAITING
                        status_update['event'] = 'waiting_for_clearance'
            else:
                # Continue moving
                move_x = (dx/distance) * self.move_speed * delta_time
                move_y = (dy/distance) * self.move_speed * delta_time
                self.position = (self.position[0] + move_x, self.position[1] + move_y)
        
        status_update['state'] = self.state
        return status_update
    
    def get_status_display(self):
        if self.state == self.IDLE:
            idle_time = format_time(time.time() - self.last_action_time)
            return f"Robot {self.id}: Idle for {idle_time}"
        elif self.state == self.MOVING:
            return f"Robot {self.id}: Moving to vertex {self.path[self.current_path_index + 1]}"
        elif self.state == self.WAITING:
            wait_time = format_time(time.time() - self.last_action_time)
            return f"Robot {self.id}: Waiting for {wait_time} to move to vertex {self.path[self.current_path_index + 1]}"
        elif self.state == self.CHARGING:
            charge_time = format_time(time.time() - self.last_action_time)
            return f"Robot {self.id}: Charging for {charge_time}"
        elif self.state == self.COMPLETED:
            return f"Robot {self.id}: Task completed"
        
        return f"Robot {self.id}: Unknown state"
    
    def pause_movement(self):
        
        #Pause the robot's movement by setting its state to 'paused'.
        
        self.paused = True
        self.state = "paused"

    def resume_movement(self):
        # Resume the robot's movement only if it is safe to do so.
        if not self.paused:
            return  # Do nothing if already moving
        self.paused = False
        self.state = "moving"
