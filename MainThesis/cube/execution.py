from .movements import rotate_face_counter_clockwise, rotate_face_clockwise
from .constants import Face

def apply_move(cube_state, move_str: str):
    """Apply a move to the cube state"""
    if not move_str:
        return
        
    # Parse the move
    face = move_str[0]
    if len(move_str) > 1:
        modifier = move_str[1]
    else:
        modifier = ''
        
    # Get the face to rotate
    if face == 'F':
        face_to_rotate = Face.FRONT
    elif face == 'R':
        face_to_rotate = Face.RIGHT
    elif face == 'U':
        face_to_rotate = Face.UP
    elif face == 'L':
        face_to_rotate = Face.LEFT
    elif face == 'D':
        face_to_rotate = Face.DOWN
    elif face == 'B':
        face_to_rotate = Face.BACK
    elif face == 'M':
        # Middle layer move (between L and R)
        apply_middle_layer_move(cube_state, 'M', modifier)
        return
    elif face == 'E':
        # Middle layer move (between U and D)
        apply_middle_layer_move(cube_state, 'E', modifier)
        return
    elif face == 'S':
        # Middle layer move (between F and B)
        apply_middle_layer_move(cube_state, 'S', modifier)
        return
    elif face == 'm':
        # Cube rotation moves (mR, mL)
        if len(move_str) >= 2:
            cube_rotation_face = move_str[1]
            apply_cube_rotation(cube_state, cube_rotation_face, modifier)
            return
        else:
            raise ValueError(f"Invalid cube rotation move: {move_str}")
    else:
        raise ValueError(f"Invalid face: {face}")
        
    # Apply the rotation
    if modifier == "'":
        # Counter-clockwise rotation
        cube_state.faces[face_to_rotate] = rotate_face_counter_clockwise(cube_state.faces[face_to_rotate])
        # Update adjacent faces
        update_adjacent_faces(cube_state, face_to_rotate, modifier)
        
    elif modifier == '2':
        # Double rotation - apply clockwise rotation twice
        cube_state.faces[face_to_rotate] = rotate_face_clockwise(cube_state.faces[face_to_rotate])
        # Update adjacent faces first time
        update_adjacent_faces(cube_state, face_to_rotate, '')
        
        # Apply second rotation
        cube_state.faces[face_to_rotate] = rotate_face_clockwise(cube_state.faces[face_to_rotate])
        # Update adjacent faces second time
        update_adjacent_faces(cube_state, face_to_rotate, '')
        
    else:
        # Clockwise rotation
        cube_state.faces[face_to_rotate] = rotate_face_clockwise(cube_state.faces[face_to_rotate])
        # Update adjacent faces
        update_adjacent_faces(cube_state, face_to_rotate, modifier) 

def update_adjacent_faces(cube_state, face: Face, modifier: str):
    """Update the adjacent faces after a rotation"""
    # Get the current state of the faces
    front = cube_state.faces[Face.FRONT]
    right = cube_state.faces[Face.RIGHT]
    up = cube_state.faces[Face.UP]
    left = cube_state.faces[Face.LEFT]
    down = cube_state.faces[Face.DOWN]
    back = cube_state.faces[Face.BACK]
    
    if face == Face.FRONT:
        if modifier == "'":
            # Counter-clockwise rotation (F')
            temp = up[2].copy()
            for i in range(3):
                up[2][i] = right[i][0]
                right[i][0] = down[0][2-i]
                down[0][2-i] = left[2-i][2]
                left[2-i][2] = temp[i]
        else:
            # Clockwise rotation (F)
            temp = up[2].copy()
            for i in range(3):
                up[2][i] = left[2-i][2]
                left[2-i][2] = down[0][2-i]
                down[0][2-i] = right[i][0]
                right[i][0] = temp[i]
    elif face == Face.RIGHT:
        if modifier == "'":
            # Counter-clockwise rotation - right side of front goes DOWN
            # UP → BACK → DOWN → FRONT → UP
            temp = [up[i][2] for i in range(3)]
            for i in range(3):
                up[i][2] = back[2-i][0]
                back[2-i][0] = down[i][2]
                down[i][2] = front[i][2]
                front[i][2] = temp[i]
        else:
            # Clockwise rotation - right side of front goes UP
            # UP → FRONT → DOWN → BACK → UP
            temp = [up[i][2] for i in range(3)]
            for i in range(3):
                up[i][2] = front[i][2]
                front[i][2] = down[i][2]
                down[i][2] = back[2-i][0]
                back[2-i][0] = temp[i]
    elif face == Face.UP:
        if modifier == "'":
            # Counter-clockwise rotation (viewed from above)
            # Front → Left → Back → Right → Front
            temp = front[0]
            front[0] = left[0]
            left[0] = back[0]
            back[0] = right[0]
            right[0] = temp
        else:
            # Clockwise rotation (viewed from above)
            # Front → Right → Back → Left → Front
            temp = front[0]
            front[0] = right[0]
            right[0] = back[0]
            back[0] = left[0]
            left[0] = temp
    elif face == Face.LEFT:
        if modifier == "'":
            # Counter-clockwise rotation - left side of front goes UP
            # UP → FRONT → DOWN → BACK → UP
            temp = [up[i][0] for i in range(3)]
            for i in range(3):
                up[i][0] = front[i][0]
                front[i][0] = down[i][0]
                down[i][0] = back[2-i][2]
                back[2-i][2] = temp[i]
        else:
            # Clockwise rotation - left side of front goes DOWN
            # UP → BACK → DOWN → FRONT → UP
            temp = [up[i][0] for i in range(3)]
            for i in range(3):
                up[i][0] = back[2-i][2]
                back[2-i][2] = down[i][0]
                down[i][0] = front[i][0]
                front[i][0] = temp[i]
    elif face == Face.DOWN:
        if modifier == "'":
            # Counter-clockwise rotation - bottom layer of front goes left
            # Front → Right → Back → Left → Front
            temp = front[2]
            front[2] = right[2]
            right[2] = back[2]
            back[2] = left[2]
            left[2] = temp
        else:
            # Clockwise rotation - bottom layer of front goes right
            # Front → Left → Back → Right → Front
            temp = front[2]
            front[2] = left[2]
            left[2] = back[2]
            back[2] = right[2]
            right[2] = temp
    elif face == Face.BACK:
        if modifier == "'":
            # Counter-clockwise rotation - B'
            # Top row of Up → left column of Left (inverted)
            # Left column of Left → bottom row of Down (inverted)
            # Bottom row of Down → right column of Right
            # Right column of Right → top row of Up
            temp = up[0].copy()
            for i in range(3):
                up[0][i] = left[2-i][0]
                left[2-i][0] = down[2][2-i]
                down[2][2-i] = right[i][2]
                right[i][2] = temp[i]
        else:
            # Clockwise rotation - B
            # Top row of Up → right column of Right
            # Right column of Right → bottom row of Down (inverted)
            # Bottom row of Down → left column of Left (inverted)
            # Left column of Left → top row of Up
            temp = up[0].copy()
            for i in range(3):
                up[0][i] = right[i][2]
                right[i][2] = down[2][2-i]
                down[2][2-i] = left[2-i][0]
                left[2-i][0] = temp[i]
    
    # Update the cube state
    cube_state.faces[Face.FRONT] = front
    cube_state.faces[Face.RIGHT] = right
    cube_state.faces[Face.UP] = up
    cube_state.faces[Face.LEFT] = left
    cube_state.faces[Face.DOWN] = down
    cube_state.faces[Face.BACK] = back 

def _apply_middle_row_move(cube_state, counterclockwise: bool = False):
    """Apply middle row move (M move) - moves the middle row between L and R faces"""
    from cube.constants import Face
    
    # Get the middle row from each face (row index 1)
    front_middle = cube_state.faces[Face.FRONT][1].copy()
    left_middle = cube_state.faces[Face.LEFT][1].copy()
    back_middle = cube_state.faces[Face.BACK][1].copy()
    right_middle = cube_state.faces[Face.RIGHT][1].copy()
    
    if counterclockwise:
        # M' (counter-clockwise): F -> L -> B -> R -> F
        cube_state.faces[Face.FRONT][1] = left_middle
        cube_state.faces[Face.LEFT][1] = back_middle
        cube_state.faces[Face.BACK][1] = right_middle
        cube_state.faces[Face.RIGHT][1] = front_middle
    else:
        # M (clockwise): F -> R -> B -> L -> F
        cube_state.faces[Face.FRONT][1] = right_middle
        cube_state.faces[Face.RIGHT][1] = back_middle
        cube_state.faces[Face.BACK][1] = left_middle
        cube_state.faces[Face.LEFT][1] = front_middle

def apply_middle_layer_move(cube_state, move_type: str, modifier: str):
    """Apply middle layer moves (M, E, S)"""
    if move_type == 'M':
        # M move: middle layer between L and R (middle row)
        # M = middle row moves clockwise, M' = middle row moves counter-clockwise
        if modifier == "'":
            # M' (counter-clockwise) - middle row moves counter-clockwise
            _apply_middle_row_move(cube_state, counterclockwise=True)
        elif modifier == '2':
            # M2 = middle row moves twice
            _apply_middle_row_move(cube_state, counterclockwise=False)
            _apply_middle_row_move(cube_state, counterclockwise=False)
        else:
            # M (clockwise) - middle row moves clockwise
            _apply_middle_row_move(cube_state, counterclockwise=False)
            
    elif move_type == 'E':
        # E move: middle layer between U and D
        # E = D U' (clockwise), E' = D' U (counter-clockwise)
        if modifier == "'":
            # E' (counter-clockwise) = D' U
            apply_move(cube_state, "D'")
            apply_move(cube_state, "U")
        elif modifier == '2':
            # E2 = D2 U2
            apply_move(cube_state, "D2")
            apply_move(cube_state, "U2")
        else:
            # E (clockwise) = D U'
            apply_move(cube_state, "D")
            apply_move(cube_state, "U'")
            
    elif move_type == 'S':
        # S move: middle layer between F and B
        # S = F B' (clockwise), S' = F' B (counter-clockwise)
        if modifier == "'":
            # S' (counter-clockwise) = F' B
            apply_move(cube_state, "F'")
            apply_move(cube_state, "B")
        elif modifier == '2':
            # S2 = F2 B2
            apply_move(cube_state, "F2")
            apply_move(cube_state, "B2")
        else:
            # S (clockwise) = F B'
            apply_move(cube_state, "F")
            apply_move(cube_state, "B'") 

def apply_cube_rotation(cube_state, rotation_face: str, modifier: str):
    """Apply cube rotation moves (mR, mL) - rotates the entire cube"""
    from .constants import Face
    
    if rotation_face == 'R':
        # mR: Rotate entire cube right (clockwise when viewed from top)
        if modifier == "'":
            # mR' (counter-clockwise) = rotate cube left
            rotate_cube_around_vertical_axis(cube_state, clockwise=False)
        elif modifier == '2':
            # mR2 = rotate cube 180 degrees around vertical axis
            rotate_cube_around_vertical_axis(cube_state, clockwise=False)
            rotate_cube_around_vertical_axis(cube_state, clockwise=False)
        else:
            # mR (clockwise) = rotate cube right
            rotate_cube_around_vertical_axis(cube_state, clockwise=True)
            
    elif rotation_face == 'L':
        # mL: Rotate entire cube left (counter-clockwise when viewed from top)
        if modifier == "'":
            # mL' (counter-clockwise) = rotate cube right
            rotate_cube_around_vertical_axis(cube_state, clockwise=True)
        elif modifier == '2':
            # mL2 = rotate cube 180 degrees around vertical axis
            rotate_cube_around_vertical_axis(cube_state, clockwise=True)
            rotate_cube_around_vertical_axis(cube_state, clockwise=True)
        else:
            # mL (clockwise) = rotate cube left
            rotate_cube_around_vertical_axis(cube_state, clockwise=False)
    else:
        raise ValueError(f"Invalid cube rotation face: {rotation_face}")

def rotate_cube_around_vertical_axis(cube_state, clockwise: bool = True):
    """Rotate the entire cube around the vertical axis (Y-axis)"""
    from .constants import Face
    
    # Store current face data
    up = cube_state.faces[Face.UP].copy()
    front = cube_state.faces[Face.FRONT].copy()
    down = cube_state.faces[Face.DOWN].copy()
    back = cube_state.faces[Face.BACK].copy()
    left = cube_state.faces[Face.LEFT].copy()
    right = cube_state.faces[Face.RIGHT].copy()
    
    if not clockwise:
        # mR (rotate cube right): FRONT→LEFT, LEFT→BACK, BACK→RIGHT, RIGHT→FRONT
        # UP and DOWN faces rotate 90 degrees clockwise
        cube_state.faces[Face.FRONT] = left
        cube_state.faces[Face.LEFT] = back
        cube_state.faces[Face.BACK] = right
        cube_state.faces[Face.RIGHT] = front
        
        # Rotate UP and DOWN faces 90 degrees clockwise
        cube_state.faces[Face.UP] = rotate_face_counter_clockwise(up)
        cube_state.faces[Face.DOWN] = rotate_face_clockwise(down)
    else:
        # mL (rotate cube left): FRONT→RIGHT, RIGHT→BACK, BACK→LEFT, LEFT→FRONT
        # UP and DOWN faces rotate 90 degrees counter-clockwise
        cube_state.faces[Face.FRONT] = right
        cube_state.faces[Face.RIGHT] = back
        cube_state.faces[Face.BACK] = left
        cube_state.faces[Face.LEFT] = front
        
        # Rotate UP and DOWN faces 90 degrees counter-clockwise
        cube_state.faces[Face.UP] = rotate_face_clockwise(up)
        cube_state.faces[Face.DOWN] = rotate_face_counter_clockwise(down) 