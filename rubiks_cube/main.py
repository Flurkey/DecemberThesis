#!/usr/bin/env python3
"""
Test script for the rubiks_cube solver with a specific cube state.
This will help debug issues with M moves in the solution.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from Cube.cube import Cube
from Cube.Solver.beginners.solver import solve_3x3

def test_solver_with_specific_state():
    """Test the solver with the specific cube state provided."""
    
    # The specific cube state provided
    cube_state = "ywwrwwyygryroowoggggwogbwbyorrrrwoobbbbgbboowrygrygbyy"
    
    print("Rubik's Cube Solver Test")
    print("=" * 50)
    print(f"Testing with cube state: {cube_state}")
    print(f"Length: {len(cube_state)} characters")
    print()
    
    # Create a new cube
    cube = Cube()
    
    # Load the specific cube state
    print("Loading cube state...")
    try:
        cube.load_cube(cube_state)
        print("✓ Cube state loaded successfully")
    except Exception as e:
        print(f"✗ Error loading cube state: {e}")
        return
    
    # Display the initial cube state
    print("\nInitial Cube State:")
    print(cube)
    
    # Check if cube is valid
    print("\nChecking cube validity...")
    try:
        # Count colors
        from collections import Counter
        color_counts = Counter(cube_state)
        print("Color counts:")
        for color, count in sorted(color_counts.items()):
            print(f"  {color}: {count}")
        
        # Check if we have the right number of each color
        expected_colors = {'w': 9, 'y': 9, 'r': 9, 'o': 9, 'g': 9, 'b': 9}
        is_valid = True
        for color, expected_count in expected_colors.items():
            actual_count = color_counts.get(color, 0)
            if actual_count != expected_count:
                print(f"  ✗ {color}: {actual_count} (expected {expected_count})")
                is_valid = False
            else:
                print(f"  ✓ {color}: {actual_count}")
        
        if is_valid:
            print("✓ Cube state is valid (9 of each color)")
        else:
            print("✗ Cube state is invalid (wrong color counts)")
            
    except Exception as e:
        print(f"Error checking validity: {e}")
    
    # Try to solve the cube with step-by-step visualization
    print("\n" + "=" * 50)
    print("STARTING SOLVER WITH STEP-BY-STEP VISUALIZATION...")
    print("=" * 50)
    
    try:
        # Call the solver
        solution, moves_by_step = solve_3x3(cube)
        
        print("\n" + "=" * 50)
        print("SOLVER COMPLETED SUCCESSFULLY!")
        print("=" * 50)
        
        print(f"\nFinal Solution: {solution}")
        print(f"Number of moves: {len(solution.split())}")
        
        # Now apply the solution step by step to show the cube state after each move
        print("\n" + "=" * 50)
        print("APPLYING SOLUTION STEP BY STEP...")
        print("=" * 50)
        
        # Reset cube to original state
        cube.load_cube(cube_state)
        
        # Split solution into individual moves
        moves = solution.split()
        
        print(f"\nApplying {len(moves)} moves step by step...")
        print("Press Enter after each move to continue, or 'q' to quit...")
        
        for i, move in enumerate(moves):
            print(f"\n--- MOVE {i+1}/{len(moves)}: {move} ---")
            
            # Apply the move using the cube's sequence method
            cube.sequence(move)
            
            # Show cube state after this move
            print("Cube state after this move:")
            print(cube)
            
            # Check if this is an M move
            if 'M' in move:
                print(f"⚠️  This is an M move: {move}")
            
            # Ask user if they want to continue
            try:
                user_input = input("Press Enter to continue, 'q' to quit: ").strip().lower()
                if user_input == 'q':
                    print("Stopped by user.")
                    break
            except KeyboardInterrupt:
                print("\nStopped by user.")
                break
        
        print("\nSolution by steps:")
        for step_name, moves in moves_by_step.items():
            if isinstance(moves, str) and moves.strip():
                print(f"  {step_name}: {moves}")
        
        # Check for M moves in the solution
        if 'M' in solution:
            print(f"\n⚠️  Solution contains M moves!")
            m_moves = [move for move in solution.split() if 'M' in move]
            print(f"M moves found: {m_moves}")
        else:
            print(f"\n✓ No M moves in solution")
            
    except Exception as e:
        print(f"\n" + "=" * 50)
        print("SOLVER FAILED!")
        print("=" * 50)
        print(f"Error: {e}")
        print(f"Error type: {type(e).__name__}")
        
        import traceback
        print("\nFull traceback:")
        traceback.print_exc()

def test_m_moves_specifically():
    """Test M moves specifically to see what happens."""
    print("\n" + "=" * 50)
    print("TESTING M MOVES SPECIFICALLY")
    print("=" * 50)
    
    cube = Cube()
    cube.load_cube("ywwrwwyygryroowoggggwogbwbyorrrrwoobbbbgbboowrygrygbyy")
    
    print("Testing M move...")
    print("Before M move:")
    print(cube)
    
    try:
        cube.turn('M', 'r')
        print("\nAfter M move:")
        print(cube)
        print("✓ M move executed successfully")
    except Exception as e:
        print(f"✗ M move failed: {e}")
        import traceback
        traceback.print_exc()
    
    print("\nTesting M' move...")
    try:
        cube.turn('M', 'l')
        print("After M' move:")
        print(cube)
        print("✓ M' move executed successfully")
    except Exception as e:
        print(f"✗ M' move failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Test the solver with the specific state
    test_solver_with_specific_state()
    
    # Test M moves specifically
    test_m_moves_specifically()
    
    print("\n" + "=" * 50)
    print("TEST COMPLETE")
    print("=" * 50)
