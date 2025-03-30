# Fleet Management System

A Python-based fleet management system with a graphical interface for managing and controlling multiple robots in a networked environment. The system provides real-time visualization, path planning, and traffic management capabilities.

## Features

- **Interactive GUI**: Built with Pygame for real-time visualization and control

  - Custom vertex and edge rendering
  - Robot state visualization with color coding
- **Robot Management**:

  - Real-time status monitoring
  - Real-time state updates
  - Individual and fleet-wide commands
  - Automatic task queuing and execution
  - Collision avoidance and deadlock prevention
- **Path Planning**:

  - A* algorithm for optimal path finding
  - Dynamic path recalculation
  - Multi-robot coordination
  - Traffic-aware routing
- **Traffic Management**:

  - Vertex reservation system
  - Deadlock detection and resolution
  - Priority-based conflict resolution
  - Safe distance maintenance

### State Management

Robots can be in the following states:

- IDLE: Awaiting commands
- MOVING: Executing path
- CHARGING: At charging station
- WAITING: Waiting for other robots
- UNKOWN: Requires attention

### Setup Steps

1. Clone the repository:

   ```bash
   git clone https://github.com/duvarakeshss/GoatPSGHackathon_22PT10
   cd fleet_management_system
   ```
2. Create and activate virtual environment:

   ```bash
   # Windows
   python -m venv venv
   .\venv\Scripts\activate

   # Linux/MacOS
   python3 -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

### Configuration

Edit `data/nav_graph.json` to customize the navigation network:

## Usage

### Starting the Application

1. Activate virtual environment (if not already active)
2. Run the main application:
   ```bash
   python src/main.py
   ```
3. If passing arguments
   ```bash
   python src/main.py --nav_graph data/nav_graph.json --log_file src/logs/fleet_logs.txt --width 1080 --height 800
   ```

### Controls

- **Keyboard Controls**:

  - 'S': Switch to Spawn mode
  - 'A': Switch to Assign mode
  - 'C': Toggle camera follow mode
  - 'R': Reset view
  - 'Q': Quit application
- **Mouse Controls**:

  - Left Click:

    - Spawn mode: Create robot at vertex
    - Assign mode: Select robot/destination

### Robot Management

1. **Spawning Robots**:

   - Press 'S' for spawn mode
   - Click on any vertex to create robot
2. **Assigning Tasks**:

   - Press 'A' for assign mode
   - Click robot to select
   - Click destination vertex

### Project Structure

```
fleet_management_system/
├── data/
│   └── nav_graph.json          # Navigation data
├── src/
│   ├── controllers/            # System controllers
│   │   ├── fleet_manager.py    # Robot fleet management
│   │   └── traffic_manager.py  # Collision prevention
│   ├── gui/                    # GUI implementation
│   │   ├── fleet_gui.py        # GUI class
│   ├── models/                 # Data models
│   │   ├── nav_graph.py        # Navigation graph
│   │   └── robot.py            # Robot implementation
│   ├── utils/                  # Utility functions
│   │   ├── helpers.py          # Common utilities
|   ├── logs/              	    # storing logs
│   │   └── logger.py           # Logging system
│   └── main.py                 # Application entry
└── requirements.txt        	# Dependencies
```

### Logging System

Logs are stored in `src/logs/fleet_logs.txt` with the following format:

```
[TIMESTAMP] [LEVEL] [COMPONENT] Message
```

Example log entries:

```
[2023-11-15 14:30:22] [INFO] [FleetManager] Robot R001 spawned at vertex V123
[2023-11-15 14:30:25] [WARN] [TrafficManager] Potential collision detected
```

### Error Handling

Common errors and solutions:

1. **Connection Errors**:

   - Check network connectivity
   - Verify port availability
   - Restart application
2. **Path Planning Failures**:

   - Ensure valid start/end points
   - Check for disconnected vertices
   - Verify graph integrity

## Requirements

### Core Dependencies

- Python 3.7+
- Pygame 2.0+
- NumPy
- NetworkX
