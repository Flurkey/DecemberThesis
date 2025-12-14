from enum import Enum
import numpy as np

class Color(Enum):
    """Enum for the six possible colors of a Rubik's Cube
    Used in:
    - camera.py: Color detection and HSV ranges
    - app.py: UI display and color mapping
    - state.py: State representation and validation
    - solver.py: Cube solving logic
    """
    WHITE = 0
    YELLOW = 1
    RED = 2
    ORANGE = 3
    BLUE = 4
    GREEN = 5
    UNKNOWN = 6

class Face(Enum):
    """Enum for the six faces of a Rubik's Cube
    Used in:
    - app.py: Face selection UI and cube display
    - state.py: Face rotation and state management
    - solver.py: Solving algorithms and move execution
    - notation.py: Move notation mapping
    """
    UP = 0      # White
    DOWN = 1    # Yellow
    FRONT = 5   # Blue
    BACK = 4   # Green
    LEFT = 3    # Orange
    RIGHT = 2   # Red


# Color ranges in HSV
# Used in camera.py for color detection
COLOR_RANGES = {
    Color.WHITE: (np.array([0, 0, 150]), np.array([180, 60, 255])),
    Color.YELLOW: (np.array([20, 100, 100]), np.array([35, 255, 255])),
    Color.RED: (np.array([0, 100, 100]), np.array([10, 255, 255])),  # Red also wraps around HSV
    Color.ORANGE: (np.array([10, 100, 100]), np.array([25, 255, 255])),
    Color.BLUE: (np.array([100, 100, 100]), np.array([130, 255, 255])),
    Color.GREEN: (np.array([50, 100, 100]), np.array([70, 255, 255]))
}

# The second range for red (which wraps around the HSV scale)
# Used in camera.py for red color detection
RED_RANGE_2 = (np.array([170, 100, 100]), np.array([180, 255, 255]))

# Default DroidCam URL (can be configured via the UI)
# Used in camera.py for camera initialization
DEFAULT_DROIDCAM_URL = "http://192.168.0.102:4747/video"
DEFAULT_DROIDCAM_SNAPSHOT_URL = "http://192.168.0.102:4747/cam/1/frame.jpg"

# Color to string mapping for display
# Used in app.py for UI display
COLOR_NAMES = {
    Color.WHITE: "White",
    Color.YELLOW: "Yellow",
    Color.RED: "Red",
    Color.ORANGE: "Orange",
    Color.BLUE: "Blue",
    Color.GREEN: "Green",
    Color.UNKNOWN: "Unknown"
}

# Face to string mapping for display
# Used in app.py for UI display
FACE_NAMES = {
    Face.UP: "Up (White)",
    Face.DOWN: "Down (Yellow)",
    Face.FRONT: "Front (Red)",
    Face.BACK: "Back (Orange)",
    Face.LEFT: "Left (Green)",
    Face.RIGHT: "Right (Blue)"
} 