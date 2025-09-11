import tkinter as tk
from tkinter import ttk, messagebox
import cv2
from PIL import Image, ImageTk
import numpy as np
from typing import Optional

from cube.constants import Color, Face
from cube.state import CubeState
from cube.rubiks_cube_bridge import RubiksCubeBridge
from ui.camera import CameraHandler
from ui.manual_solver import ManualSolutionInput

class RubiksCubeApp(tk.Tk):
    """Main application window for the Rubik's Cube solver"""
    def __init__(self):
        super().__init__()
        
        self.title("Rubik's Cube Solver")
        
        # Make the window full screen
        self.state('zoomed')  # On Windows, this maximizes the window
        # Alternative for cross-platform: self.attributes('-fullscreen', True)
        
        # Get screen dimensions for proper sizing
        self.update_idletasks()
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        
        # Initialize components
        self.cube_state = CubeState()
        self.camera = CameraHandler()
        self.current_face = Face.UP
        self.solver = None
        self.is_solving = False
        self.solution_step = -1
        
        self._create_widgets()
        self._create_bindings()
        
        # Start camera
        try:
            self.camera.start()
            self.after(100, self._update_camera)
        except Exception as e:
            # Automatically launch in manual mode without showing messagebox
            print(f"Camera connection failed: {e}")
            print("Launching in manual mode...")
            # No messagebox - just continue in manual mode
            
    def _create_widgets(self):
        """Create all UI widgets"""
        # Main container
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Left panel - Camera feed (centered)
        self.camera_frame = ttk.LabelFrame(self.main_container, text="Camera Feed")
        self.camera_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame to center the camera label
        self.camera_center_frame = ttk.Frame(self.camera_frame)
        self.camera_center_frame.pack(expand=True, fill=tk.BOTH)
        
        self.camera_label = ttk.Label(self.camera_center_frame)
        self.camera_label.pack(expand=True)  # This will center the camera feed
        
        # Right panel - Cube state and controls
        self.control_frame = ttk.Frame(self.main_container)
        self.control_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=5, pady=5)
        
        # Face selection
        self.face_frame = ttk.LabelFrame(self.control_frame, text="Current Face")
        self.face_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.face_var = tk.StringVar(value=self.current_face.name)
        for face in Face:
            ttk.Radiobutton(self.face_frame, text=face.name,
                          variable=self.face_var, value=face.name,
                          command=self._on_face_change).pack(side=tk.LEFT)
                          
        # Capture controls
        self.capture_frame = ttk.Frame(self.control_frame)
        self.capture_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.capture_button = ttk.Button(self.capture_frame, text="Capture Face",
                                       command=self._capture_face)
        self.capture_button.pack(side=tk.LEFT, padx=5)
        
        self.reset_button = ttk.Button(self.capture_frame, text="Reset Face",
                                     command=self._reset_face)
        self.reset_button.pack(side=tk.LEFT, padx=5)
        
        self.complete_button = ttk.Button(self.capture_frame, text="Complete", command=self._complete_cube)
        self.complete_button.pack(side=tk.LEFT, padx=5)
        
        self.scramble_button = ttk.Button(self.capture_frame, text="Scramble", command=self._scramble_cube)
        self.scramble_button.pack(side=tk.LEFT, padx=5)
        
        self.simple_scramble_button = ttk.Button(self.capture_frame, text="Simple Scramble", command=self._simple_scramble_cube)
        self.simple_scramble_button.pack(side=tk.LEFT, padx=5)
        
        # Cube display
        self.display_frame = ttk.LabelFrame(self.control_frame, text="Cube State")
        self.display_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.face_displays = {}
        self._create_cube_display()
        
        orientation_info = (
            "Cube Orientation:\n"
            "  White = Up (UP)\n"
            "  Yellow = Down (DOWN)\n"
            "  Green = Front (FRONT)\n"
            "  Blue = Back (BACK)\n"
            "  Orange = Left (LEFT)\n"
            "  Red = Right (RIGHT)"
        )
        ttk.Label(self.display_frame, text=orientation_info, font=("Arial", 10)).grid(row=2, column=2, columnspan=4, sticky='w', padx=5, pady=2)
        
        # Solver controls
        self.solver_frame = ttk.Frame(self.control_frame)
        self.solver_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.solve_button = ttk.Button(self.solver_frame, text="Solve Cube",
                                      command=self._solve_cube)
        self.solve_button.pack(side=tk.LEFT, padx=5)
        
        self.manual_solve_button = ttk.Button(self.solver_frame, text="Manual Solution",
                                           command=self._open_manual_solution)
        self.manual_solve_button.pack(side=tk.LEFT, padx=5)
        
        self.prev_button = ttk.Button(self.solver_frame, text="Previous Step",
                                    command=self._previous_step, state=tk.DISABLED)
        self.prev_button.pack(side=tk.LEFT, padx=5)
        
        self.next_button = ttk.Button(self.solver_frame, text="Next Step",
                                    command=self._next_step, state=tk.DISABLED)
        self.next_button.pack(side=tk.LEFT, padx=5)
        
        # Solution steps display
        self.steps_frame = ttk.LabelFrame(self.control_frame, text="Solution Steps")
        self.steps_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.steps_text = tk.Text(self.steps_frame, height=10, width=40)
        self.steps_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
    def _create_cube_display(self):
        """Create the cube state display grids"""
        # Create a 4x3 grid of face displays
        faces = [
            [None, Face.UP, None, None],
            [Face.LEFT, Face.FRONT, Face.RIGHT, Face.BACK],
            [None, Face.DOWN, None, None]
        ]
        
        for row, face_row in enumerate(faces):
            for col, face in enumerate(face_row):
                if face is not None:
                    frame = ttk.Frame(self.display_frame)
                    frame.grid(row=row, column=col, padx=5, pady=5)
                    
                    # Create 3x3 grid for face
                    cells = []
                    for i in range(3):
                        cell_row = []
                        for j in range(3):
                            cell = tk.Frame(frame, width=30, height=30,
                                          relief=tk.RAISED, borderwidth=1)
                            cell.grid(row=i, column=j, padx=1, pady=1)
                            cell.grid_propagate(False)
                            cell_row.append(cell)
                        cells.append(cell_row)
                    
                    self.face_displays[face] = cells
                    
    def _create_bindings(self):
        """Create event bindings"""
        # Bind click events for face grids
        for face, cells in self.face_displays.items():
            for row in range(3):
                for col in range(3):
                    cells[row][col].bind("<Button-1>", 
                                       lambda e, f=face, r=row, c=col: self._on_cell_click(f, r, c))
                                       
    def _update_camera(self):
        """Update the camera feed"""
        frame = self.camera.get_frame()
        if frame is not None:
            # Draw grid on frame
            frame = self.camera.draw_grid(frame)
            
            # Convert to PhotoImage
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            image = Image.fromarray(frame)
            photo = ImageTk.PhotoImage(image=image)
            
            self.camera_label.configure(image=photo)
            self.camera_label.image = photo
            
        self.after(16, self._update_camera)  # Update at ~60 FPS (reduced from 33ms to 16ms)
        
    def _on_face_change(self):
        """Handle face selection change"""
        face_name = self.face_var.get()
        self.current_face = Face[face_name]
        
    def _capture_face(self):
        """Capture the current face colors"""
        colors = self.camera.capture_face()
        if colors:
            self.cube_state.set_face(self.current_face, colors)
            self._update_display()
            
            # Auto-advance to next face
            current_idx = list(Face).index(self.current_face)
            next_idx = (current_idx + 1) % len(Face)
            self.current_face = list(Face)[next_idx]
            self.face_var.set(self.current_face.name)
            
            # Show message if in manual mode
            if not self.camera.camera_available:
                messagebox.showinfo("Manual Mode", 
                                  "In manual mode, each face is set to all white by default.\n"
                                  "You can click on the cells to change their colors.")
            
    def _reset_face(self):
        """Reset the current face"""
        self.cube_state.reset_face(self.current_face)
        self._update_display()
        
    def _complete_cube(self):
        """Set the cube to a solved state and update the display."""
        self.cube_state.set_solved()
        self._update_display()
        
    def _scramble_cube(self):
        """Set the cube state to a simple, manageable scrambled state."""
        # Start with a solved cube
        self.cube_state.set_solved()
        
        # Apply a sequence of moves to create a manageable scramble
        # This creates a simple scramble that's only a few moves away from solved
        scramble_moves = ["R", "U", "R'", "U'", "F", "F'"]
        
        for move in scramble_moves:
            self.cube_state.move(move)
        
        self._update_display()
    
    def _simple_scramble_cube(self):
        """Set the cube to a random scramble starting from a complete solved state."""
        import random
        
        # Start with a complete solved cube (same as Complete button)
        self.cube_state.set_solved()
        
        # Define available moves
        faces = ['R', 'L', 'U', 'D', 'F', 'B']
        modifiers = ['', "'", '2']  # clockwise, counter-clockwise, double
        
        # Generate a random scramble (15-20 moves)
        scramble_length = random.randint(15, 20)
        scramble_moves = []
        
        last_face = None
        for i in range(scramble_length):
            # Avoid repeating the same face twice in a row
            while True:
                face = random.choice(faces)
                if face != last_face:
                    break
            
            modifier = random.choice(modifiers)
            move = face + modifier
            scramble_moves.append(move)
            last_face = face
        
        # Apply the scramble moves to the complete cube
        for move in scramble_moves:
            self.cube_state.move(move)
        
        # Output the scramble to console
        scramble_string = " ".join(scramble_moves)
        print(f"\nSIMPLE SCRAMBLE: {scramble_string}")
        print(f"Scramble length: {len(scramble_moves)} moves")
        
        self._update_display()
        
    def _update_display(self):
        """Update the cube state display"""
        for face in Face:
            colors = self.cube_state.get_face(face)
            for row in range(3):
                for col in range(3):
                    color = colors[row][col]
                    bg_color = self._get_display_color(color)
                    self.face_displays[face][row][col].configure(bg=bg_color)
                    
    def _get_display_color(self, color: Optional[Color]) -> str:
        """Get the display color for a cube color"""
        if color == Color.WHITE:
            return "white"
        elif color == Color.YELLOW:
            return "yellow"
        elif color == Color.RED:
            return "red"
        elif color == Color.ORANGE:
            return "orange"
        elif color == Color.BLUE:
            return "blue"
        elif color == Color.GREEN:
            return "green"
        return "gray"
        
    def _on_cell_click(self, face: Face, row: int, col: int):
        """Handle click on a face cell"""
        colors = self.cube_state.get_face(face)
        current_color = colors[row][col]
        
        # Cycle through colors
        color_order = [
            Color.WHITE, Color.YELLOW, Color.RED,
            Color.ORANGE, Color.BLUE, Color.GREEN
        ]
        
        if current_color in color_order:
            next_idx = (color_order.index(current_color) + 1) % len(color_order)
            new_color = color_order[next_idx]
        else:
            new_color = Color.WHITE
            
        colors[row][col] = new_color
        self.cube_state.set_face(face, colors)
        self._update_display()
        
    def _solve_cube(self):
        """Start solving the cube using the proven rubiks_cube solver via bridge"""
        if not self.cube_state.is_complete():
            messagebox.showerror("Error", "Please scan all faces first")
            return
            
        if not self.cube_state.is_valid():
            messagebox.showerror("Error", "Invalid cube state")
            return
            
        try:
            self.solve_button.configure(state=tk.DISABLED)
            self.is_solving = True
            
            # Store the original scrambled state
            original_state = self.cube_state.copy()
            
            # Create bridge and solve using proven rubiks_cube solver
            bridge = RubiksCubeBridge()
            if not bridge.rubiks_cube_available:
                messagebox.showerror("Error", "rubiks_cube solver not available. Please install it first.")
                return
                
            # Solve using the bridge (which calls the proven rubiks_cube solver)
            optimized_solution, moves_by_step = bridge.solve_with_rubiks_cube(original_state)
            
            # Store the bridge for later use in navigation
            self.solver = bridge
            
            # Display the formatted solution with current step info
            self.steps_text.delete(1.0, tk.END)
            
            # Display timing information
            timing_info = bridge.get_timing_info()
            if timing_info['solver_send_formatted'] and timing_info['solver_receive_formatted']:
                self.steps_text.insert(tk.END, "SOLVER TIMING:\n")
                self.steps_text.insert(tk.END, f"  Bridge → Solver: {timing_info['solver_send_formatted']}\n")
                self.steps_text.insert(tk.END, f"  Solver → Bridge: {timing_info['solver_receive_formatted']}\n")
                self.steps_text.insert(tk.END, f"  Duration: {timing_info['duration_formatted']}\n")
                
                # Check if the cube can be solved (verify solution correctness)
                self.steps_text.insert(tk.END, "  Solution Verification: ")
                try:
                    # Create a test cube with the original scrambled state
                    test_cube = original_state.copy()
                    
                    # Apply the solution moves
                    solution_moves = optimized_solution.split()
                    for move in solution_moves:
                        if move.strip():  # Skip empty moves
                            test_cube.move(move)
                    
                    # Check if the cube is now solved
                    if test_cube.is_solved():
                        self.steps_text.insert(tk.END, "CORRECT\n\n")
                    else:
                        self.steps_text.insert(tk.END, "INCORRECT\n\n")
                except Exception as e:
                    self.steps_text.insert(tk.END, f"ERROR: {str(e)}\n\n")
            else:
                self.steps_text.insert(tk.END, "\n")
            
            # Get current section and move (step 0)
            current_section, current_move = self._get_current_section_and_move(0)
            
            # Show the formatted display immediately
            self.steps_text.insert(tk.END, f"CURRENT STEP: {self.solution_step + 1} of {len(self.solver.solution_moves)}\n")
            self.steps_text.insert(tk.END, f"SECTION: {current_section}\n")
            self.steps_text.insert(tk.END, f"MOVE: {current_move}\n")
            
            # Display all sections with better formatting
            if hasattr(self.solver, 'moves_by_step'):
                self.steps_text.insert(tk.END, "SOLUTION BREAKDOWN:\n")
                
                for step_name, moves in self.solver.moves_by_step.items():
                    if isinstance(moves, str) and moves.strip():
                        # Check if this is the current section
                        if step_name == current_section:
                            self.steps_text.insert(tk.END, f">>  {step_name}: {moves}\n")
                        else:
                            self.steps_text.insert(tk.END, f"   {step_name}: {moves}\n")
            
            # Enable navigation buttons
            self.prev_button.configure(state=tk.NORMAL)
            self.next_button.configure(state=tk.NORMAL)
            self.solution_step = 0
            
            # Highlight the current move
            self._highlight_current_move_in_section(current_section, current_move)
            
            # Show success message
            if optimized_solution:
                messagebox.showinfo("Solution Found", f"Solution found using proven rubiks_cube solver!\n\nUse the Previous/Next Step buttons to navigate through the solution.")
            else:
                messagebox.showinfo("No Solution", "No solution found for this cube state.")
            
        except Exception as e:
            messagebox.showerror("Error", str(e))
        finally:
            self.solve_button.configure(state=tk.NORMAL)
            self.is_solving = False
            
    def _open_manual_solution(self):
        """Open dialog for entering a manual solution"""
        # Create the manual solution dialog and pass the callback
        ManualSolutionInput(self, self._process_manual_solution)
    
    def _process_manual_solution(self, moves):
        """Process manually entered solution moves"""
        if not moves:
            return
            
        try:
            # Disable buttons
            self.solve_button.configure(state=tk.DISABLED)
            self.manual_solve_button.configure(state=tk.DISABLED)
            self.is_solving = True
            
            # Create a custom solver just for these moves
            from cube.manual_solver import ManualCubeSolver
            self.solver = ManualCubeSolver(self.cube_state)
            
            # Set the solution steps directly
            self.solver.solution_steps = moves
            
            # Display solution steps
            self.steps_text.delete(1.0, tk.END)
            for i, move in enumerate(moves, 1):
                self.steps_text.insert(tk.END, f"{i}. {move}\n")
                
            # Enable navigation buttons
            self.prev_button.configure(state=tk.NORMAL)
            self.next_button.configure(state=tk.NORMAL)
            self.solution_step = 0
            self._update_display()
            
            # Show confirmation
            messagebox.showinfo("Manual Solution", f"Loaded {len(moves)} solution steps successfully. Use the Previous/Next Step buttons to navigate.")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error processing manual solution: {str(e)}")
        finally:
            self.solve_button.configure(state=tk.NORMAL)
            self.manual_solve_button.configure(state=tk.NORMAL)
            self.is_solving = False
            
    def _previous_step(self):
        """Show previous solution step"""
        if self.solver and self.solution_step > 0:
            self.solution_step -= 1
            state = self.solver.get_state_at_step(self.solution_step)
            self.cube_state = state
            self._update_display()
            
            # Show current section and move using moves_by_step (same as _next_step)
            if hasattr(self.solver, 'solution_moves'):
                # Bridge solution
                current_section, current_move = self._get_current_section_and_move(self.solution_step)
                
                # Update the textbox with better formatting
                self.steps_text.delete(1.0, tk.END)
                
                # Header with current progress
                self.steps_text.insert(tk.END, f"CURRENT STEP: {self.solution_step + 1} of {len(self.solver.solution_moves)}\n")
                self.steps_text.insert(tk.END, f"SECTION: {current_section}\n")
                self.steps_text.insert(tk.END, f"MOVE: {current_move}\n")
                
                # Display all sections with better formatting
                if hasattr(self.solver, 'moves_by_step'):
                    self.steps_text.insert(tk.END, "SOLUTION BREAKDOWN:\n")
                    
                    for step_name, moves in self.solver.moves_by_step.items():
                        if isinstance(moves, str) and moves.strip():
                            # Check if this is the current section
                            if step_name == current_section:
                                self.steps_text.insert(tk.END, f">>  {step_name}: {moves}\n")
                            else:
                                self.steps_text.insert(tk.END, f"   {step_name}: {moves}\n")
                
                self._highlight_current_move_in_section(current_section, current_move)
            else:
                # Working solver - highlight the step number
                self.steps_text.tag_remove("current", "1.0", tk.END)
                self.steps_text.tag_add("current", f"{self.solution_step + 1}.0",
                                      f"{self.solution_step + 1}.end")
                self.steps_text.tag_config("current", background="yellow")
            
    def _next_step(self):
        """Show next solution step"""
        if self.solver:
            if hasattr(self.solver, 'solution_moves'):
                # Bridge solution
                if self.solution_step < len(self.solver.solution_moves):
                    self.solution_step += 1
                    state = self.solver.get_state_at_step(self.solution_step)
                    self.cube_state = state
                    self._update_display()
                    
                    # Show current section and move using moves_by_step
                    if self.solution_step < len(self.solver.solution_moves):
                        current_section, current_move = self._get_current_section_and_move(self.solution_step)
                        
                        # Update the textbox with better formatting
                        self.steps_text.delete(1.0, tk.END)
                        
                        # Header with current progress
                        self.steps_text.insert(tk.END, f"CURRENT STEP: {self.solution_step + 1} of {len(self.solver.solution_moves)}\n")
                        self.steps_text.insert(tk.END, f"SECTION: {current_section}\n")
                        self.steps_text.insert(tk.END, f"MOVE: {current_move}\n")
                        
                        # Display all sections with better formatting
                        if hasattr(self.solver, 'moves_by_step'):
                            self.steps_text.insert(tk.END, "SOLUTION BREAKDOWN:\n")
                            
                            for step_name, moves in self.solver.moves_by_step.items():
                                if isinstance(moves, str) and moves.strip():
                                    # Check if this is the current section
                                    if step_name == current_section:
                                        self.steps_text.insert(tk.END, f">>  {step_name}: {moves}\n")
                                    else:
                                        self.steps_text.insert(tk.END, f"   {step_name}: {moves}\n")
                        
                        # Only highlight if we're still within bounds
                        self._highlight_current_move_in_section(current_section, current_move)
                    else:
                        # Reached the end - show completion message
                        self.steps_text.delete(1.0, tk.END)
                        self.steps_text.insert(tk.END, "SOLUTION COMPLETE!\n")
                        self.steps_text.insert(tk.END, f"All {len(self.solver.solution_moves)} steps have been executed.\n")
                        self.steps_text.insert(tk.END, "The cube should now be solved!")
            
            else:
                # Working solver
                if self.solution_step < len(self.solver.solution_steps):
                    self.solution_step += 1
                    state = self.solver.get_state_at_step(self.solution_step)
                    self.cube_state = state
                    self._update_display()
                    
                    # Highlight current step
                    self.steps_text.tag_remove("current", "1.0", tk.END)
                    self.steps_text.tag_add("current", f"{self.solution_step + 1}.0",
                                          f"{self.solution_step + 1}.end")
                    self.steps_text.tag_config("current", background="yellow")

    def _get_current_section_and_move(self, step):
        """Determine which solving section and move the current step belongs to"""
        if not hasattr(self.solver, 'moves_by_step'):
            return "Unknown", "Unknown"
        
        # Count moves to determine current section
        move_count = 0
        for section_name, moves in self.solver.moves_by_step.items():
            if isinstance(moves, str) and moves.strip():
                section_moves = moves.split()
                if step < move_count + len(section_moves):
                    # We're in this section
                    move_index_in_section = step - move_count
                    current_move = section_moves[move_index_in_section] if move_index_in_section < len(section_moves) else "Unknown"
                    return section_name, current_move
                move_count += len(section_moves)
        
        return "Complete", "Unknown"

    def _highlight_current_move_in_section(self, section_name, current_move):
        """Highlight the current move within its section"""
        self.steps_text.tag_remove("current", "1.0", tk.END)
        
        # Find the line with the current section (look for the arrow indicator)
        for line_num in range(1, int(self.steps_text.index(tk.END).split('.')[0])):
            line_text = self.steps_text.get(f"{line_num}.0", f"{line_num}.end")
            if line_text.startswith(f">>  {section_name}:"):
                # Found the current section line, now find the current move within it
                section_moves = line_text.replace(f">>  {section_name}: ", "").split()
                
                # Find which move within this section we're currently on
                move_count = 0
                for section in self.solver.moves_by_step.keys():
                    if section == section_name:
                        break
                    if isinstance(self.solver.moves_by_step[section], str) and self.solver.moves_by_step[section].strip():
                        move_count += len(self.solver.moves_by_step[section].split())
                
                # Calculate which move within this section we're on
                move_index_in_section = self.solution_step - move_count
                
                # Find the position of the specific move at this index
                char_position = len(f">>  {section_name}: ")
                for i, move in enumerate(section_moves):
                    if i == move_index_in_section:
                        # Found the correct move at the correct position
                        start_pos = f"{line_num}.{char_position}"
                        end_pos = f"{line_num}.{char_position + len(move)}"
                        self.steps_text.tag_add("current", start_pos, end_pos)
                        self.steps_text.tag_config("current", background="yellow")
                        return
                    char_position += len(move) + 1  # +1 for space
                break
            
    def _highlight_move_in_text(self, move: str):
        """Highlight the current move at its specific position in the solution"""
        self.steps_text.tag_remove("current", "1.0", tk.END)
        
        # Find the complete solution line
        solution_line = None
        for line_num in range(1, int(self.steps_text.index(tk.END).split('.')[0])):
            line_text = self.steps_text.get(f"{line_num}.0", f"{line_num}.end")
            if "Complete Solution:" in line_text:
                solution_line = line_num
                break
        
        if solution_line is None:
            return
        
        # Get the solution text
        solution_text = self.steps_text.get(f"{solution_line}.0", f"{solution_line}.end")
        
        # Find the position of the current move in the solution
        solution_moves = solution_text.replace("Complete Solution: ", "").split()
        
        # Find the current move position
        current_move_index = -1
        move_count = 0
        for i, solution_move in enumerate(solution_moves):
            if move_count == self.solution_step:
                current_move_index = i
                break
            move_count += 1
        
        if current_move_index == -1:
            return
        
        # Calculate the character position of the current move
        char_position = len("Complete Solution: ")
        for i in range(current_move_index):
            char_position += len(solution_moves[i]) + 1  # +1 for space
        
        # Highlight only this specific move
        start_pos = f"{solution_line}.{char_position}"
        end_pos = f"{solution_line}.{char_position + len(move)}"
        
        self.steps_text.tag_add("current", start_pos, end_pos)
        self.steps_text.tag_config("current", background="yellow")
            
    def on_closing(self):
        """Handle window closing"""
        self.camera.stop()
        self.destroy() 