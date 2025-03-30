import math
import random
import networkx as nx
import time

def distance(pos1, pos2):
    # Calculate Euclidean distance
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def liner_interpolation(a, b, t):
    # Linear interpolation
    return a + (b - a) * t

def linear_interplotion_pos(pos1, pos2, t):
    # Interpolate between positions
    return (liner_interpolation(pos1[0], pos2[0], t), liner_interpolation(pos1[1], pos2[1], t))

def find_path_astar(graph, start, end):
    # A* algorithm for path finding
    try:
        path = nx.astar_path(graph, start, end)
        return path
    except nx.NetworkXNoPath:
        return None

def find_path_avoiding_obstacles(graph, start, end, obstacles):
    # Find path avoiding obstacles
    temp_graph = graph.copy()
    
    for vertex in obstacles:
        if temp_graph.has_node(vertex):
            temp_graph.remove_node(vertex)
    
    try:
        path = nx.shortest_path(temp_graph, start, end)
        return path
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return None

def generate_unique_id(prefix=""):
    # Generate unique timestamp-based ID
    timestamp = int(time.time() * 1000)
    random_part = random.randint(1200, 9999)
    return f"{prefix}{timestamp}_{random_part}"

def format_time(seconds):
    # Format seconds to readable time
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        seconds = seconds % 60
        return f"{minutes}m {seconds:.0f}s"
    else:
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600) / 60)
        return f"{hours}h {minutes}m"