import pygame
import json
import math

# Load the navigation graph file
with open("data/nav_graph.json", "r") as f:
    nav_graph = json.load(f)

# Pygame Initialization
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Fleet Management Visualization")
clock = pygame.time.Clock()

# Extract lane and vertex data
lanes = nav_graph["levels"]["level1"]["lanes"]
vertices = nav_graph["levels"]["level1"]["vertices"]

# Normalize coordinates to fit the screen
min_x = min(v[0] for v in vertices)
max_x = max(v[0] for v in vertices)
min_y = min(v[1] for v in vertices)
max_y = max(v[1] for v in vertices)

scale_x = WIDTH / (max_x - min_x + 2)
scale_y = HEIGHT / (max_y - min_y + 2)
center_x = WIDTH // 2
center_y = HEIGHT // 2

def transform_coordinates(x, y):
    """Transforms the graph coordinates to Pygame's coordinate system."""
    new_x = int((x - min_x) * scale_x + center_x - (WIDTH // 2))
    new_y = int((y - min_y) * scale_y + center_y - (HEIGHT // 2))
    return new_x, new_y

# Transform vertex positions
transformed_vertices = [transform_coordinates(v[0], v[1]) for v in vertices]

# Initialize a moving vehicle
class Vehicle:
    def __init__(self, path):
        self.path = path  # List of vertex indices forming the path
        self.current_index = 0  # Start at the first vertex
        self.speed = 2  # Pixels per frame
        self.position = list(transformed_vertices[self.path[0]])

    def move(self):
        if self.current_index < len(self.path) - 1:
            start = transformed_vertices[self.path[self.current_index]]
            end = transformed_vertices[self.path[self.current_index + 1]]

            # Calculate movement direction
            dx, dy = end[0] - self.position[0], end[1] - self.position[1]
            distance = math.hypot(dx, dy)
            if distance < self.speed:
                self.current_index += 1  # Move to next node
                self.position = list(end)  # Snap to the node
            else:
                self.position[0] += self.speed * (dx / distance)
                self.position[1] += self.speed * (dy / distance)

    def draw(self):
        pygame.draw.circle(screen, (0, 255, 0), (int(self.position[0]), int(self.position[1])), 8)  # Green vehicle

# Example path for the vehicle (Modify this to change movement route)
example_path = [0, 4, 5, 11, 6, 7, 12, 8, 9, 2]  # Sequence of vertex indices
vehicle = Vehicle(example_path)

def draw_graph():
    screen.fill((255, 255, 255))  # White background
    
    # Draw lanes (edges)
    for lane in lanes:
        start_idx, end_idx, _ = lane
        pygame.draw.line(screen, (0, 0, 0), transformed_vertices[start_idx], transformed_vertices[end_idx], 2)
    
    # Draw vertices (nodes)
    for i, (x, y) in enumerate(transformed_vertices):
        is_charger = "is_charger" in vertices[i][2] and vertices[i][2]["is_charger"]
        color = (0, 0, 255) if is_charger else (255, 0, 0)  # Blue for chargers, red for others
        pygame.draw.circle(screen, color, (x, y), 6)
        if vertices[i][2]["name"]:
            font = pygame.font.Font(None, 20)
            text = font.render(vertices[i][2]["name"], True, (0, 0, 0))
            screen.blit(text, (x + 5, y - 10))

running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    vehicle.move()  # Move vehicle
    draw_graph()  # Redraw graph
    vehicle.draw()  # Draw vehicle

    pygame.display.flip()
    clock.tick(30)  # 30 FPS

pygame.quit()
