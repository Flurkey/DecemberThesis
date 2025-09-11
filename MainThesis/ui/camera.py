import cv2
import numpy as np
from typing import Optional, List, Tuple
from cube.constants import Color, DEFAULT_DROIDCAM_URL
import time

class CameraHandler:
    """Handles camera capture and color detection for the Rubik's Cube"""
    def __init__(self, droidcam_url: str = DEFAULT_DROIDCAM_URL):
        self.droidcam_url = droidcam_url
        self.cap = None
        self.grid_size = 50  # Size of each grid cell in pixels
        self.grid_margin = 2  # Margin between grid cells
        self.grid_offset_x = 100  # X offset for grid
        self.grid_offset_y = 100  # Y offset for grid
        self.camera_available = True
        
    def start(self):
        """Start the camera capture"""
        try:
            self.cap = cv2.VideoCapture(self.droidcam_url)
            if not self.cap.isOpened():
                self.camera_available = False
                print("Camera not available - running in manual mode")
        except Exception as e:
            self.camera_available = False
            print(f"Camera not available - running in manual mode: {str(e)}")
            
    def stop(self):
        """Stop the camera capture"""
        if self.cap:
            self.cap.release()
            self.cap = None
            
    def get_frame(self) -> Optional[np.ndarray]:
        """Get the current frame from the camera"""
        if not self.camera_available:
            # Return a blank frame with grid
            frame = np.zeros((480, 640, 3), dtype=np.uint8)
            frame = self.draw_grid(frame)
            return frame
            
        if not self.cap:
            return None
            
        ret, frame = self.cap.read()
        if not ret:
            return None
            
        return frame
        
    def draw_grid(self, frame: np.ndarray) -> np.ndarray:
        """Draw the 3x3 grid on the frame"""
        height, width = frame.shape[:2]
        grid_width = 3 * self.grid_size + 2 * self.grid_margin
        grid_height = 3 * self.grid_size + 2 * self.grid_margin
        
        # Center the grid
        self.grid_offset_x = (width - grid_width) // 2
        self.grid_offset_y = (height - grid_height) // 2
        
        # Draw grid cells
        for row in range(3):
            for col in range(3):
                x = self.grid_offset_x + col * (self.grid_size + self.grid_margin)
                y = self.grid_offset_y + row * (self.grid_size + self.grid_margin)
                cv2.rectangle(frame, (x, y), 
                            (x + self.grid_size, y + self.grid_size),
                            (255, 255, 255), 2)

        return frame
    
    def get_cell_colors(self, frame: np.ndarray) -> List[List[Color]]:
        """Get the colors of each cell in the grid"""
        if not self.camera_available:
            # Return a default face (all white) when no camera is available
            return [[Color.WHITE for _ in range(3)] for _ in range(3)]
            
        colors = [[None for _ in range(3)] for _ in range(3)]
        
        for row in range(3):
            for col in range(3):
                x = self.grid_offset_x + col * (self.grid_size + self.grid_margin)
                y = self.grid_offset_y + row * (self.grid_size + self.grid_margin)
                
                # Get center region of cell
                cell_center_x = x + self.grid_size // 2
                cell_center_y = y + self.grid_size // 2
                sample_size = 10
                
                # Sample colors from center region
                color_samples = []
                for dx in range(-sample_size//2, sample_size//2):
                    for dy in range(-sample_size//2, sample_size//2):
                        px = cell_center_x + dx
                        py = cell_center_y + dy
                        if 0 <= px < frame.shape[1] and 0 <= py < frame.shape[0]:
                            color_samples.append(frame[py, px])
                            
                if color_samples:
                    # Convert to HSV for better color detection
                    avg_color = np.mean(color_samples, axis=0).astype(np.uint8)
                    hsv_color = cv2.cvtColor(avg_color.reshape(1, 1, 3), cv2.COLOR_BGR2HSV)[0][0]
                    
                    # Detect color based on HSV ranges
                    colors[row][col] = self._detect_color(hsv_color)
                    
        return colors
        
    def _detect_color(self, hsv: np.ndarray) -> Color:
        """Detect the cube color from HSV values"""
        h, s, v = hsv
        
        # White detection
        if s < 30 and v > 150:
            return Color.WHITE
            
        # Yellow detection
        if h >= 20 and h <= 35 and s > 100:
            return Color.YELLOW
            
        # Red detection (wraps around in HSV)
        if (h <= 10 or h >= 170) and s > 100:
            return Color.RED
            
        # Orange detection
        if h >= 10 and h <= 20 and s > 100:
            return Color.ORANGE
            
        # Green detection
        if h >= 35 and h <= 85 and s > 100:
            return Color.GREEN
            
        # Blue detection
        if h >= 85 and h <= 130 and s > 100:
            return Color.BLUE
            
        return Color.UNKNOWN
        
    def capture_face(self) -> Optional[List[List[Color]]]:
        """Capture and process a cube face"""
        if not self.camera_available:
            # Return a default face (all white) when no camera is available
            return [[Color.WHITE for _ in range(3)] for _ in range(3)]
            
        if not self.cap:
            return None
            
        # Wait for camera to stabilize (reduced from 0.5 to 0.1 seconds)
        time.sleep(0.1)
        
        # Capture multiple frames and average the results
        num_frames = 3  # Reduced from 5 to 3 frames
        all_colors = []
        
        for _ in range(num_frames):
            frame = self.get_frame()
            if frame is None:
                continue
                
            colors = self.get_cell_colors(frame)
            all_colors.append(colors)
            time.sleep(0.05)  # Reduced from 0.1 to 0.05 seconds
            
        if not all_colors:
            return None
            
        # Process results
        result = [[None for _ in range(3)] for _ in range(3)]
        for row in range(3):
            for col in range(3):
                # Get most common color for this cell
                cell_colors = [colors[row][col] for colors in all_colors]
                color_counts = {}
                for color in cell_colors:
                    if color != Color.UNKNOWN:
                        color_counts[color] = color_counts.get(color, 0) + 1
                        
                if color_counts:
                    result[row][col] = max(color_counts.items(), key=lambda x: x[1])[0]
                else:
                    result[row][col] = Color.UNKNOWN
                    
        return result 