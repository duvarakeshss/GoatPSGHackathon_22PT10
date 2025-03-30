import math
import logging

def distance(pos1, pos2):
    """Calculate Euclidean distance between two positions."""
    return math.sqrt((pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2)

def normalize_vector(vector):
    """Normalize a 2D vector to unit length."""
    length = math.sqrt(vector[0]**2 + vector[1]**2)
    return (vector[0] / length, vector[1] / length) if length != 0 else (0, 0)

def vector_angle(v1, v2):
    """Calculate the angle between two vectors (in radians)."""
    len1 = math.sqrt(v1[0]**2 + v1[1]**2)
    len2 = math.sqrt(v2[0]**2 + v2[1]**2)
    
    if len1 == 0 or len2 == 0:
        return 0  # Avoid division by zero
    
    dot = v1[0] * v2[0] + v1[1] * v2[1]
    angle = math.acos(max(-1, min(1, dot / (len1 * len2))))
    
    # Determine sign using cross product
    cross = v1[0] * v2[1] - v1[1] * v2[0]
    return -angle if cross < 0 else angle

def interpolate_positions(pos1, pos2, progress):
    """Linearly interpolate between two positions."""
    return (
        pos1[0] + (pos2[0] - pos1[0]) * progress,
        pos1[1] + (pos2[1] - pos1[1]) * progress
    )

def scale_positions(positions, scale_factor):
    """Scale a list of positions by a factor."""
    return [(p[0] * scale_factor, p[1] * scale_factor) for p in positions]

def is_point_in_polygon(point, polygon):
    """Check if a point is inside a polygon using the ray-casting algorithm."""
    x, y = point
    n = len(polygon)
    inside = False

    p1x, p1y = polygon[0]
    for i in range(1, n + 1):
        p2x, p2y = polygon[i % n]
        
        if min(p1y, p2y) < y <= max(p1y, p2y) and x <= max(p1x, p2x):
            xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x if p1y != p2y else p1x
            if x <= xinters:
                inside = not inside
                
        p1x, p1y = p2x, p2y
        
    return inside

def setup_logging(log_file_path, console_level=logging.INFO, file_level=logging.DEBUG):
    """Set up logging to both console and file, avoiding duplicate handlers."""
    logger = logging.getLogger()
    if logger.hasHandlers():
        return logger  # Prevent adding duplicate handlers
    
    logger.setLevel(logging.DEBUG)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(console_level)
    console_handler.setFormatter(logging.Formatter('%(levelname)s - %(message)s'))

    # File handler
    file_handler = logging.FileHandler(log_file_path)
    file_handler.setLevel(file_level)
    file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    logging.info(f"Logging initialized. Logs saved to {log_file_path}")
    
    return logger
