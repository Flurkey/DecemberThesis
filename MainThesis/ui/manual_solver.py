import tkinter as tk
from tkinter import ttk, Text, WORD, END, messagebox, StringVar

class ManualSolutionInput:
    """Dialog for manually entering a sequence of Rubik's Cube moves"""
    def __init__(self, parent, callback):
        self.parent = parent
        self.callback = callback
        self.result = None
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Manual Solution Input")
        self.dialog.geometry("600x500")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Create widgets
        self._create_widgets()
        
        # Make modal
        self.dialog.protocol("WM_DELETE_WINDOW", self._on_cancel)
        self.dialog.wait_window()
    
    def _create_widgets(self):
        """Create the dialog widgets"""
        # Instructions
        instructions = """
Enter your solution sequence below. Use standard Rubik's Cube notation:
R, L, U, D, F, B for clockwise turns
R', L', U', D', F', B' for counter-clockwise turns
R2, L2, U2, D2, F2, B2 for 180° turns
M, E, S for middle layer moves
mR, mL for cube rotations (rotate entire cube)

Example: R U R' U' F' U F mR mL
        """
        ttk.Label(self.dialog, text=instructions, justify=tk.LEFT, wraplength=580).pack(padx=10, pady=10)
        
        # Text input
        self.text_input = Text(self.dialog, wrap=WORD, height=10, width=70)
        self.text_input.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Example sequences dropdown
        ttk.Label(self.dialog, text="Or select a common algorithm:").pack(padx=10, anchor=tk.W)
        
        examples = {
            "Select an example": "",
            "Sexy Move (R U R' U')": "R U R' U'",
            "Reverse Sexy (U R U' R')": "U R U' R'",
            "Sledgehammer (R' F R F')": "R' F R F'",
            "Sune (R U R' U R U2 R')": "R U R' U R U2 R'",
            "Anti-Sune (R U2 R' U' R U' R')": "R U2 R' U' R U' R'",
            "PLL T Perm": "R U R' U' R' F R2 U' R' U' R U R' F'",
            "PLL Y Perm": "F R U' R' U' R U R' F' R U R' U' R' F R F'"
        }
        
        self.example_var = StringVar()
        self.example_var.set("Select an example")
        
        example_dropdown = ttk.Combobox(self.dialog, textvariable=self.example_var, values=list(examples.keys()), width=30)
        example_dropdown.pack(padx=10, pady=5, anchor=tk.W)
        
        def on_example_selected(*args):
            selected = self.example_var.get()
            if selected in examples and examples[selected]:
                self.text_input.delete(1.0, END)
                self.text_input.insert(END, examples[selected])
        
        self.example_var.trace("w", on_example_selected)
        
        # Buttons
        button_frame = ttk.Frame(self.dialog)
        button_frame.pack(padx=10, pady=10, fill=tk.X)
        
        ttk.Button(button_frame, text="Parse & Execute", command=self._on_submit).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=self._on_cancel).pack(side=tk.LEFT, padx=5)
        
    def _on_submit(self):
        """Handle the submit button click"""
        solution_text = self.text_input.get(1.0, END).strip()
        
        if not solution_text:
            messagebox.showerror("Error", "Please enter a solution sequence.")
            return
        
        # Parse the solution
        moves = self._parse_solution(solution_text)
        
        if not moves:
            messagebox.showerror("Error", "Could not parse any valid moves. Please check your input.")
            return
        
        self.result = moves
        self.dialog.destroy()
        
        # Call the callback with the result
        if self.callback:
            self.callback(self.result)
    
    def _on_cancel(self):
        """Handle the cancel button click"""
        self.dialog.destroy()
    
    def _parse_solution(self, solution_text):
        """Parse the solution text into a list of moves"""
        # Remove commas, normalize spacing
        solution_text = solution_text.replace(',', ' ')
        
        # Match valid move patterns including cube rotations and middle layer moves
        import re
        # Updated pattern to include cube rotations (mR, mL) and middle layer moves (M, E, S)
        move_pattern = r'(?:m[RL]|[RUFLBDMES])[\'2]?'
        return re.findall(move_pattern, solution_text)
