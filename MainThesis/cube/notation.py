def parse_move(move_str: str):
    """Parse a move string and return the face and modifier"""
    if not move_str:
        return None, None
        
    face = move_str[0]
    modifier = move_str[1] if len(move_str) > 1 else ''
    
    return face, modifier
