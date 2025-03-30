import pygame
import time
import numpy as np

class FleetGUI:
    # GUI using Pygame
    
    # Colors
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GRAY = (200, 200, 200)
    LIGHT_GRAY = (220, 220, 220)
    DARK_GRAY = (100, 100, 100)
    
    VERTEX_COLOR = (50, 100, 150)
    VERTEX_HIGHLIGHT = (100, 150, 200)
    CHARGER_COLOR = (50, 200, 50)
    
    LANE_COLOR = (120, 120, 190)
    LANE_HIGHLIGHT = (100, 200, 255)
    LANE_OCCUPIED = (255, 80, 80)
    
    ROBOT_OUTLINE = (0, 0, 0)
    MESSAGE_COLOR = (255, 100, 100)
    
    def __init__(self, width, height, nav_graph, fleet_manager, traffic_manager):
        # Init GUI
        self.width = width
        self.height = height
        self.nav_graph = nav_graph
        self.fleet_manager = fleet_manager
        self.traffic_manager = traffic_manager
        
        pygame.init()
        pygame.font.init()
        
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Fleet Management System")
        
        self.font_small = pygame.font.SysFont('Arial', 12)
        self.font_medium = pygame.font.SysFont('Arial', 16)
        self.font_large = pygame.font.SysFont('Arial', 24)
        
        self.clock = pygame.time.Clock()
        
        self.mode = "spawn"
        self.hover_vertex = None
        self.selected_robot = None
        self.messages = []
        self.message_timeout = 3.0
        
        self.preview_path = None
        self.logs = []
        self.max_logs = 4  # Keep only 4 most recent logs
        self.max_display_logs = 4  # But only display 4

    def add_message(self, message):
        # Add screen message
        self.messages.append({
            'text': message,
            'time': time.time()
        })
    
    def add_log(self, log_entry):
        # Add log entry at the beginning
        self.logs.insert(0, log_entry)
        if len(self.logs) > self.max_logs:
            self.logs.pop()  # Remove the oldest entry

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:  # Changed from K_ESCAPE to K_q
                    return False
                elif event.key == pygame.K_s:
                    self.mode = "spawn"
                    self.add_message("Mode: Spawn Robots")
                elif event.key == pygame.K_a:
                    self.mode = "assign"
                    self.add_message("Mode: Assign Tasks")
            
            elif event.type == pygame.MOUSEMOTION:
                mouse_x, mouse_y = event.pos
                self.hover_vertex = self.nav_graph.get_vertex_at_position(mouse_x, mouse_y)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    mouse_x, mouse_y = event.pos
                    
                    if self.mode == "spawn":
                        # Spawn a robot at the clicked vertex
                        vertex_id = self.nav_graph.get_vertex_at_position(mouse_x, mouse_y)
                        if vertex_id is not None:
                            robot_id = self.fleet_manager.spawn_robot(vertex_id)
                            if robot_id is not None:
                                self.add_message(f"Spawned Robot {robot_id} at vertex {vertex_id}")
                                self.add_log(f"Spawned Robot {robot_id} at vertex {vertex_id}")
                            else:
                                self.add_message(f"Cannot spawn robot: Vertex {vertex_id} is occupied")
                    
                    elif self.mode == "assign":
                        # First check if we clicked on a robot
                        robot_id = self.fleet_manager.select_robot(mouse_x, mouse_y)
                        if robot_id is not None:
                            self.selected_robot = robot_id
                            self.add_message(f"Selected Robot {robot_id}")
                            self.preview_path = None
                        else:
                            # If a robot is already selected, assign destination
                            if self.selected_robot is not None:
                                vertex_id = self.nav_graph.get_vertex_at_position(mouse_x, mouse_y)
                                if vertex_id is not None:
                                    success = self.fleet_manager.assign_navigation_task(self.selected_robot, vertex_id)
                                    if success:
                                        self.add_message(f"Assigned Robot {self.selected_robot} to vertex {vertex_id}")
                                        self.add_log(f"Robot {self.selected_robot} moving to vertex {vertex_id}")
                                        self.preview_path = None
                                    else:
                                        self.add_message(f"Failed to assign task to Robot {self.selected_robot}")
        
        return True

    def update(self, delta_time):
        # Update GUI state
        current_time = time.time()
        self.messages = [msg for msg in self.messages 
                         if current_time - msg['time'] < self.message_timeout]
        
        self.update_path_preview()  # Changed from update_path_overview to update_path_preview

    def update_path_preview(self):  # Method name changed to match usage
        # Update preview path for selected robot
        if self.mode == "assign" and self.selected_robot is not None and self.hover_vertex is not None:
            if self.selected_robot in self.fleet_manager.robots:
                robot = self.fleet_manager.robots[self.selected_robot]
                current_vertex = robot.current_vertex
                self.preview_path = self.nav_graph.get_shortest_path(current_vertex, self.hover_vertex)
    
    # Add these colors at the top of the class with other color definitions
    GRADIENT_TOP = (40, 40, 60)
    GRADIENT_BOTTOM = (80, 80, 100)
    
    def render(self):
        """Render the GUI."""
        # Create gradient background
        height_step = self.height // 100
        for i in range(100):
            progress = i / 100
            color = (
                int(self.GRADIENT_TOP[0] + (self.GRADIENT_BOTTOM[0] - self.GRADIENT_TOP[0]) * progress),
                int(self.GRADIENT_TOP[1] + (self.GRADIENT_BOTTOM[1] - self.GRADIENT_TOP[1]) * progress),
                int(self.GRADIENT_TOP[2] + (self.GRADIENT_BOTTOM[2] - self.GRADIENT_TOP[2]) * progress)
            )
            pygame.draw.rect(self.screen, color, (0, i * height_step, self.width, height_step))
        
        # Rest of the render code remains the same
        # Calculate center offset for the graph
        graph_width = self.nav_graph.max_x - self.nav_graph.min_x
        graph_height = self.nav_graph.max_y - self.nav_graph.min_y
        
        # Update nav_graph scale and offset to center the graph
        self.nav_graph.scale = min(
            (self.width * 0.8) / graph_width,
            (self.height * 0.8) / graph_height
        )
        
        # Add additional offset (30 pixels right, 120 pixels ≈ 6cm down)
        self.nav_graph.offset_x = (self.width - graph_width * self.nav_graph.scale) / 2 + 30
        self.nav_graph.offset_y = (self.height - graph_height * self.nav_graph.scale) / 2 + 120
        
        # Draw lanes
        self.draw_lanes()
        
        # Draw vertices
        self.draw_vertices()
        
        # Draw robots
        self.draw_robots()
        
        # Draw path preview
        if self.preview_path:
            self.draw_path_preview()
        
        # Draw UI elements
        self.draw_ui()
        
        # Draw messages
        self.draw_messages()
        
        # Draw logs (moved to left corner)
        self.draw_logs()
        
        # Update the display
        pygame.display.flip()
    
    def draw_lanes(self):
        """Draw the lanes of the navigation graph."""
        # First pass: draw all lane lines
        for lane in self.nav_graph.lanes:
            from_vertex = lane['from_vertex']
            to_vertex = lane['to_vertex']
            
            from_pos = self.nav_graph.get_scaled_position(from_vertex)
            to_pos = self.nav_graph.get_scaled_position(to_vertex)
            
            # Determine lane color based on occupation
            color = self.LANE_COLOR
            width = 2
            
            if lane['occupying_robot'] is not None:
                color = self.LANE_OCCUPIED
                width = 3
            
            # Draw the lane with slightly thicker line
            pygame.draw.line(self.screen, color, from_pos, to_pos, width)
        
        # Second pass: draw all arrows (so they appear on top of crossing lines)
        for lane in self.nav_graph.lanes:
            from_vertex = lane['from_vertex']
            to_vertex = lane['to_vertex']
            
            from_pos = self.nav_graph.get_scaled_position(from_vertex)
            to_pos = self.nav_graph.get_scaled_position(to_vertex)
            
            # Determine lane color based on occupation
            color = self.LANE_COLOR
            if lane['occupying_robot'] is not None:
                color = self.LANE_OCCUPIED
                
            # Draw an arrow to show direction
            self.draw_arrows(from_pos, to_pos, color)
    
    def draw_arrows(self, start_pos, end_pos, color, arrow_size=8):
        
        import numpy as np
        
        # Calculate direction vector
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Normalize
        length = ((dx ** 2) + (dy ** 2)) ** 0.5
        if length == 0:
            return
        
        dx /= length
        dy /= length
        
        # Calculate arrow head position (70% along the line)
        arrow_pos = (
            int(start_pos[0] + dx * length * 0.7),
            int(start_pos[1] + dy * length * 0.7)
        )
        
        # Calculate perpendicular vector
        perp_dx = -dy
        perp_dy = dx
        
        # Calculate arrow points
        left_point = (
            int(arrow_pos[0] - dx * arrow_size + perp_dx * arrow_size / 2),
            int(arrow_pos[1] - dy * arrow_size + perp_dy * arrow_size / 2)
        )
        
        right_point = (
            int(arrow_pos[0] - dx * arrow_size - perp_dx * arrow_size / 2),
            int(arrow_pos[1] - dy * arrow_size - perp_dy * arrow_size / 2)
        )
        
        # Draw arrow head
        pygame.draw.polygon(self.screen, color, [arrow_pos, left_point, right_point])
    
    def draw_vertices(self):
        """Draw the vertices of the navigation graph."""
        for vertex in self.nav_graph.vertices:
            vertex_id = vertex['id']
            position = self.nav_graph.get_scaled_position(vertex_id)
            
            # Determine vertex color
            color = self.VERTEX_COLOR
            
            # Highlight if hovering or if it's a charging station
            if vertex_id == self.hover_vertex:
                color = self.VERTEX_HIGHLIGHT
                radius = 14  # Bigger when hovered
            elif vertex.get('is_charger', False):
                color = self.CHARGER_COLOR
                radius = 12  # Slightly bigger for chargers
            else:
                radius = 10
            
            # Draw the vertex with outline for better visibility
            pygame.draw.circle(self.screen, color, position, radius)
            pygame.draw.circle(self.screen, self.BLACK, position, radius, 1)
            
            # Draw vertex ID
            id_text = self.font_small.render(str(vertex_id), True, self.WHITE)
            self.screen.blit(id_text, (position[0] - id_text.get_width() // 2, 
                                      position[1] - id_text.get_height() // 2))
            
            # Draw vertex name below
            if vertex['name']:
                # Create a slightly darker background for better text visibility
                name_text = self.font_small.render(vertex['name'], True, self.BLACK)
                text_width = name_text.get_width()
                text_height = name_text.get_height()
                
                # Draw text background
                bg_rect = pygame.Rect(
                    position[0] - text_width // 2 - 2,
                    position[1] + 12 - 2,
                    text_width + 4,
                    text_height + 4
                )
                pygame.draw.rect(self.screen, (240, 240, 240), bg_rect)
                pygame.draw.rect(self.screen, self.DARK_GRAY, bg_rect, 1)
                
                # Draw the name text
                self.screen.blit(name_text, (position[0] - text_width // 2, 
                                           position[1] + 12))
    
    def draw_robots(self):
        """Draw all robots."""
        for robot_id, robot in self.fleet_manager.robots.items():
            # Draw robot
            position = robot.position
            color = robot.color
            
            # Draw robot body
            pygame.draw.circle(self.screen, color, position, 12)
            pygame.draw.circle(self.screen, self.ROBOT_OUTLINE, position, 12, 2)
            
            # Highlight selected robot
            if robot_id == self.selected_robot:
                pygame.draw.circle(self.screen, self.WHITE, position, 16, 2)
            
            # Draw robot ID
            id_text = self.font_small.render(str(robot_id), True, self.WHITE)
            self.screen.blit(id_text, (position[0] - id_text.get_width() // 2, 
                                      position[1] - id_text.get_height() // 2))
            
            # Draw robot state indicator
            self.draw_robot_state(robot, position)
    
    def draw_robot_state(self, robot, position):
     
        state = robot.state
        indicator_pos = (position[0], position[1] - 20)
        
        # Choose color based on state
        if state == robot.IDLE:
            color = (200, 200, 200)  # Gray
        elif state == robot.MOVING:
            color = (0, 200, 0)  # Green
        elif state == robot.WAITING:
            color = (200, 200, 0)  # Yellow
        elif state == robot.CHARGING:
            color = (0, 200, 200)  # Cyan
        elif state == robot.COMPLETED:
            color = (0, 0, 200)  # Blue
        else:
            color = (100, 100, 100)
        
        # Draw state indicator
        pygame.draw.circle(self.screen, color, indicator_pos, 5)
        pygame.draw.circle(self.screen, self.BLACK, indicator_pos, 5, 1)
    
    def draw_path_preview(self):
       
        if not self.preview_path or len(self.preview_path) < 2:
            return
        
        # Draw path segments
        for i in range(len(self.preview_path) - 1):
            from_vertex = self.preview_path[i]
            to_vertex = self.preview_path[i + 1]
            
            from_pos = self.nav_graph.get_scaled_position(from_vertex)
            to_pos = self.nav_graph.get_scaled_position(to_vertex)
            
            # Draw line with dashed style
            self.draw_dashed_line(from_pos, to_pos, (0, 100, 200))
    
    def draw_dashed_line(self, start_pos, end_pos, color, dash_length=5, gap_length=3):
        
        # Calculate direction vector
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        
        # Calculate distance
        distance = ((dx ** 2) + (dy ** 2)) ** 0.5
        
        # Calculate number of dashes
        dash_count = int(distance / (dash_length + gap_length))
        
        # Normalize direction
        if distance > 0:
            dx /= distance
            dy /= distance
        
        # Draw dashes
        for i in range(dash_count):
            start = i * (dash_length + gap_length)
            x1 = start_pos[0] + dx * start
            y1 = start_pos[1] + dy * start
            
            end = start + dash_length
            x2 = start_pos[0] + dx * min(end, distance)
            y2 = start_pos[1] + dy * min(end, distance)
            
            pygame.draw.line(self.screen, color, (x1, y1), (x2, y2), 2)
    
    def draw_ui(self):
        # UI elements
        # Draw mode indicator with white label and red value
        mode_label = self.font_medium.render("Mode: ", True, self.WHITE)
        mode_value = self.font_medium.render('Spawn' if self.mode == 'spawn' else 'Assign', True, (255, 0, 0))
        
        self.screen.blit(mode_label, (10, 10))
        self.screen.blit(mode_value, (10 + mode_label.get_width(), 10))
        
        # Draw instructions box
        instructions = [
            "Press S: Switch to Spawn mode",
            "Press A: Switch to Assign mode",
            "Left Click: Spawn robot (in Spawn mode) or select/assign destination (in Assign mode)",
            "Q: Quit"
        ]
        
        # Calculate box dimensions
        padding = 10
        line_height = 20
        box_width = 400
        box_height = (len(instructions) + 1) * line_height + padding * 2
        
        # Draw instruction box
        box_rect = pygame.Rect(10, 35, box_width, box_height)
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, box_rect)
        pygame.draw.rect(self.screen, self.DARK_GRAY, box_rect, 1)
        
        # Draw instructions with black text
        for i, instruction in enumerate(instructions):
            text = self.font_small.render(instruction, True, self.BLACK)
            self.screen.blit(text, (20, 45 + i * 20))
        
        # Draw mini-map overview
        self.draw_minimap()
        
        # Draw robot statuses
        statuses = self.fleet_manager.get_all_robot_statuses()
        status_y = 40
        
        for robot_id, status in statuses.items():
            if robot_id in self.fleet_manager.robots:
                robot = self.fleet_manager.robots[robot_id]
                
                # Choose text color based on robot state
                text_color = self.WHITE
                if robot.state == robot.MOVING:
                    text_color = (0, 200, 0)  # Same green as the moving indicator
                
                # Draw status text with robot color indicator
                pygame.draw.circle(self.screen, robot.color, (self.width - 20, status_y + 6), 6)
                pygame.draw.circle(self.screen, self.BLACK, (self.width - 20, status_y + 6), 6, 1)
                
                status_text = self.font_small.render(status, True, text_color)
                self.screen.blit(status_text, (self.width - 30 - status_text.get_width(), status_y))
                status_y += 20
    
    def draw_minimap(self):
        """Draw a minimap overview of the entire graph."""
        # Define minimap size and position
        minimap_width = 150
        minimap_height = 120
        minimap_x = 10  # Changed to left side
        minimap_y = self.height - minimap_height - 10
        
        # Draw minimap background
        pygame.draw.rect(self.screen, (240, 240, 240), 
                         (minimap_x, minimap_y, minimap_width, minimap_height))
        pygame.draw.rect(self.screen, self.BLACK, 
                         (minimap_x, minimap_y, minimap_width, minimap_height), 1)
        
        # Calculate scaling for the minimap with padding
        padding = 20  # Increased padding for better centering
        graph_width = self.nav_graph.max_x - self.nav_graph.min_x
        graph_height = self.nav_graph.max_y - self.nav_graph.min_y
        
        # Calculate scale to fit the graph with padding
        x_scale = (minimap_width - 2 * padding) / graph_width
        y_scale = (minimap_height - 2 * padding) / graph_height
        scale = min(x_scale, y_scale)
        
        # Calculate offsets to center the graph
        scaled_width = graph_width * scale
        scaled_height = graph_height * scale
        x_offset = minimap_x + (minimap_width - scaled_width) / 2
        y_offset = minimap_y + (minimap_height - scaled_height) / 2
        
        # Draw lanes with centered coordinates
        for lane in self.nav_graph.lanes:
            from_vertex = self.nav_graph.vertices[lane['from_vertex']]
            to_vertex = self.nav_graph.vertices[lane['to_vertex']]
            
            from_x = x_offset + (from_vertex['x'] - self.nav_graph.min_x) * scale
            from_y = y_offset + (from_vertex['y'] - self.nav_graph.min_y) * scale
            to_x = x_offset + (to_vertex['x'] - self.nav_graph.min_x) * scale
            to_y = y_offset + (to_vertex['y'] - self.nav_graph.min_y) * scale
            
            pygame.draw.line(self.screen, self.LANE_COLOR, (from_x, from_y), (to_x, to_y), 1)
        
        # Draw vertices
        for vertex in self.nav_graph.vertices:
            x = x_offset + (vertex['x'] - self.nav_graph.min_x) * scale
            y = y_offset + (vertex['y'] - self.nav_graph.min_y) * scale
            
            color = self.VERTEX_COLOR
            if vertex.get('is_charger', False):
                color = self.CHARGER_COLOR
                
            pygame.draw.circle(self.screen, color, (x, y), 2)
        
        # Draw robots
        for robot_id, robot in self.fleet_manager.robots.items():
            # Get the real position and convert to minimap coordinates
            vertex = self.nav_graph.vertices[robot.current_vertex]
            x = x_offset + (vertex['x'] - self.nav_graph.min_x) * scale
            y = y_offset + (vertex['y'] - self.nav_graph.min_y) * scale
            
            pygame.draw.circle(self.screen, robot.color, (x, y), 3)
        
        # Draw title
        title_text = self.font_small.render("Overview", True, self.BLACK)
        self.screen.blit(title_text, (minimap_x + 5, minimap_y + 2))
    
    def draw_messages(self):
        """Draw notification messages."""
        message_y = self.height - 30
        
        for message in reversed(self.messages):
            text = self.font_medium.render(message['text'], True, self.MESSAGE_COLOR)
            self.screen.blit(text, (self.width // 2 - text.get_width() // 2, message_y))
            message_y -= 25
    
    def draw_logs(self):
        """Draw log entries."""
        log_x = self.width - 310
        log_y = self.height - 150
        
        # Draw background
        pygame.draw.rect(self.screen, self.LIGHT_GRAY, (log_x, log_y, 300, 120))
        
        # Draw title in blue
        title_text = self.font_medium.render("Recent Events:", True, (0, 0, 255))
        self.screen.blit(title_text, (log_x + 5, log_y + 5))
        
        # Draw log entries (most recent first, limited to 4)
        entry_y = log_y + 30
        for log in self.logs[:4]:  # Only show 4 most recent logs
            text = self.font_small.render(log, True, self.BLACK)
            self.screen.blit(text, (log_x + 10, entry_y))
            entry_y += 18
            
