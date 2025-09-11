from typing import Dict, List
from .constants import Color, Face
from .execution import apply_move

class CubeState:
    """Represents the current state of the Rubik's Cube"""
    def __init__(self):
        # Initialize cube with None values (unknown)
        self.faces = {face: [[None for _ in range(3)] for _ in range(3)] for face in Face}
        
    def set_face(self, face: Face, colors: List[List[Color]]):
        """Set the colors for a specific face"""
        self.faces[face] = colors
        
    def get_face(self, face: Face) -> List[List[Color]]:
        """Get the colors for a specific face"""
        return self.faces[face]
    
    def is_complete(self) -> bool:
        """Check if all faces have been scanned"""
        for face in Face:
            if any(None in row for row in self.faces[face]):
                return False
        return True
    
    def as_string(self) -> str:
        """Convert the cube state to a string representation for the solver"""
        result = ""
        for face in [Face.UP, Face.RIGHT, Face.FRONT, Face.DOWN, Face.LEFT, Face.BACK]:
            for row in self.faces[face]:
                for cell in row:
                    if cell == Color.WHITE:
                        result += "W"
                    elif cell == Color.YELLOW:
                        result += "Y"
                    elif cell == Color.RED:
                        result += "R"
                    elif cell == Color.ORANGE:
                        result += "O"
                    elif cell == Color.BLUE:
                        result += "B"
                    elif cell == Color.GREEN:
                        result += "G"
                    else:
                        result += "?"
        return result
    
    def color_count(self):
        """Count the number of each color on the cube"""
        from collections import Counter
        counts = Counter()
        for face in Face:
            for row in self.faces[face]:
                for cell in row:
                    if cell is not None:
                        counts[cell] += 1
        return counts
    
    def is_valid(self) -> bool:
        """Check if the cube state is valid (has exactly 9 of each color)"""
        counts = self.color_count()
        # Check that we have exactly 9 of each color (except UNKNOWN)
        for color in Color:
            if color != Color.UNKNOWN:
                if counts[color] != 9:
                    print(f"Invalid cube: {color.name} has {counts[color]} squares (should be 9)")
                    return False
        return True
    
    def reset_face(self, face: Face):
        """Reset a specific face to unknown state"""
        self.faces[face] = [[None for _ in range(3)] for _ in range(3)]
        
    def copy(self) -> 'CubeState':
        """Create a deep copy of the cube state"""
        new_state = CubeState()
        for face in Face:
            new_state.faces[face] = [row[:] for row in self.faces[face]]
        return new_state
        
    def move(self, move_str: str):
        """Perform a cube move (F, R, U, L, D, B and their inverses/double turns)"""
        apply_move(self, move_str)
    
    def set_solved(self):
        """Set the cube to a solved state."""
        color_map = {
            Face.UP: Color.WHITE,
            Face.DOWN: Color.YELLOW,
            Face.FRONT: Color.GREEN,
            Face.BACK: Color.BLUE,
            Face.LEFT: Color.ORANGE,
            Face.RIGHT: Color.RED,
        }
        for face, color in color_map.items():
            # Create a proper 3x3 grid with 9 squares of the same color
            self.faces[face] = []
            for row in range(3):
                face_row = []
                for col in range(3):
                    face_row.append(color)
                self.faces[face].append(face_row)
    
    def is_solved(self) -> bool:
        """Check if the cube is in a solved state (all faces have uniform colors)"""
        # Define the expected solved state
        solved_colors = {
            Face.UP: Color.WHITE,
            Face.DOWN: Color.YELLOW,
            Face.FRONT: Color.GREEN,
            Face.BACK: Color.BLUE,
            Face.LEFT: Color.ORANGE,
            Face.RIGHT: Color.RED,
        }
        
        # Check each face
        for face, expected_color in solved_colors.items():
            face_data = self.faces[face]
            for row in face_data:
                for cell in row:
                    if cell != expected_color:
                        return False
        return True
    
    def _rotate_adjacent(self, face: Face, clockwise: bool):
        # Update adjacent edge/corner stickers for F, R, U, L, D faces
        if face == Face.FRONT:
            if clockwise:
                temp = [self.faces[Face.UP][2][i] for i in range(3)]
                for i in range(3):
                    self.faces[Face.UP][2][i] = self.faces[Face.LEFT][2-i][2]
                    self.faces[Face.LEFT][2-i][2] = self.faces[Face.DOWN][0][2-i]
                    self.faces[Face.DOWN][0][2-i] = self.faces[Face.RIGHT][i][0]
                    self.faces[Face.RIGHT][i][0] = temp[i]
            else:
                temp = [self.faces[Face.UP][2][i] for i in range(3)]
                for i in range(3):
                    self.faces[Face.UP][2][i] = self.faces[Face.RIGHT][i][0]
                    self.faces[Face.RIGHT][i][0] = self.faces[Face.DOWN][0][2-i]
                    self.faces[Face.DOWN][0][2-i] = self.faces[Face.LEFT][2-i][2]
                    self.faces[Face.LEFT][2-i][2] = temp[i]
        elif face == Face.RIGHT:
            if clockwise:
                temp = [self.faces[Face.UP][i][2] for i in range(3)]
                for i in range(3):
                    self.faces[Face.UP][i][2] = self.faces[Face.FRONT][i][2]
                    self.faces[Face.FRONT][i][2] = self.faces[Face.DOWN][i][2]
                    self.faces[Face.DOWN][i][2] = self.faces[Face.BACK][2-i][0]
                    self.faces[Face.BACK][2-i][0] = temp[i]
            else:
                temp = [self.faces[Face.UP][i][2] for i in range(3)]
                for i in range(3):
                    self.faces[Face.UP][i][2] = self.faces[Face.BACK][2-i][0]
                    self.faces[Face.BACK][2-i][0] = self.faces[Face.DOWN][i][2]
                    self.faces[Face.DOWN][i][2] = self.faces[Face.FRONT][i][2]
                    self.faces[Face.FRONT][i][2] = temp[i]
        elif face == Face.UP:
            if clockwise:
                temp = [self.faces[Face.FRONT][0][i] for i in range(3)]
                for i in range(3):
                    self.faces[Face.FRONT][0][i] = self.faces[Face.RIGHT][0][i]
                    self.faces[Face.RIGHT][0][i] = self.faces[Face.BACK][0][i]
                    self.faces[Face.BACK][0][i] = self.faces[Face.LEFT][0][i]
                    self.faces[Face.LEFT][0][i] = temp[i]
            else:
                temp = [self.faces[Face.FRONT][0][i] for i in range(3)]
                for i in range(3):
                    self.faces[Face.FRONT][0][i] = self.faces[Face.LEFT][0][i]
                    self.faces[Face.LEFT][0][i] = self.faces[Face.BACK][0][i]
                    self.faces[Face.BACK][0][i] = self.faces[Face.RIGHT][0][i]
                    self.faces[Face.RIGHT][0][i] = temp[i]
        elif face == Face.LEFT:
            if clockwise:
                temp = [self.faces[Face.UP][i][0] for i in range(3)]
                for i in range(3):
                    self.faces[Face.UP][i][0] = self.faces[Face.BACK][2-i][2]
                    self.faces[Face.BACK][2-i][2] = self.faces[Face.DOWN][i][0]
                    self.faces[Face.DOWN][i][0] = self.faces[Face.FRONT][i][0]
                    self.faces[Face.FRONT][i][0] = temp[i]
            else:
                temp = [self.faces[Face.UP][i][0] for i in range(3)]
                for i in range(3):
                    self.faces[Face.UP][i][0] = self.faces[Face.FRONT][i][0]
                    self.faces[Face.FRONT][i][0] = self.faces[Face.DOWN][i][0]
                    self.faces[Face.DOWN][i][0] = self.faces[Face.BACK][2-i][2]
                    self.faces[Face.BACK][2-i][2] = temp[i]
        elif face == Face.DOWN:
            if clockwise:
                temp = [self.faces[Face.FRONT][2][i] for i in range(3)]
                for i in range(3):
                    self.faces[Face.FRONT][2][i] = self.faces[Face.LEFT][2][i]
                    self.faces[Face.LEFT][2][i] = self.faces[Face.BACK][2][i]
                    self.faces[Face.BACK][2][i] = self.faces[Face.RIGHT][2][i]
                    self.faces[Face.RIGHT][2][i] = temp[i]
            else:
                temp = [self.faces[Face.FRONT][2][i] for i in range(3)]
                for i in range(3):
                    self.faces[Face.FRONT][2][i] = self.faces[Face.RIGHT][2][i]
                    self.faces[Face.RIGHT][2][i] = self.faces[Face.BACK][2][i]
                    self.faces[Face.BACK][2][i] = self.faces[Face.LEFT][2][i]
                    self.faces[Face.LEFT][2][i] = temp[i] 