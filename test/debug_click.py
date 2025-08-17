#!/usr/bin/env python3

# Debug script to test click detection with small board
def test_click_detection():
    # Simulate the UI calculations for board_size = 8
    board_size = 8
    square_size = min(600 // board_size, 30)  # 30
    board_width = square_size * board_size  # 240
    board_height = square_size * board_size  # 240
    
    # Side panel dimensions
    side_panel_width = 200
    top_panel_height = 80
    message_area_height = 60
    
    # Calculate minimum height needed for piece selections
    pieces_per_player = 6
    piece_height = 35
    piece_area_height = pieces_per_player * piece_height  # 210
    side_panel_padding = 60
    min_side_panel_height = piece_area_height + side_panel_padding  # 270
    
    # Total window dimensions
    base_window_width = board_width + 2 * side_panel_width  # 640
    min_window_height = top_panel_height + min_side_panel_height  # 350
    board_window_height = board_height + top_panel_height + message_area_height  # 380
    base_window_height = max(min_window_height, board_window_height)  # 380
    
    # Increase window size by 10%
    window_width = int(base_window_width * 1.1)  # 704
    window_height = int(base_window_height * 1.1)  # 418
    
    # Recalculate side panel width with the extra space
    extra_width = window_width - base_window_width  # 64
    side_panel_width += extra_width // 4  # 200 + 16 = 216
    
    print(f"Final dimensions:")
    print(f"  Window: {window_width} x {window_height}")
    print(f"  Side panel width: {side_panel_width}")
    print(f"  Board width: {board_width}")
    print(f"  Top panel height: {top_panel_height}")
    print()
    
    # Test the click detection logic
    def get_clicked_position(mouse_pos):
        x, y = mouse_pos
        board_start_x = side_panel_width
        board_start_y = top_panel_height
        
        print(f"Testing click at ({x}, {y})")
        print(f"  Board starts at ({board_start_x}, {board_start_y})")
        print(f"  Board area: {board_start_x} <= x < {board_start_x + board_width} and {board_start_y} <= y < {board_start_y + board_height}")
        
        # Check if click is on board
        if (board_start_x <= x < board_start_x + board_width and 
            board_start_y <= y < board_start_y + board_height):
            col = (x - board_start_x) // square_size
            row = (y - board_start_y) // square_size
            if 0 <= row < board_size and 0 <= col < board_size:
                print(f"  -> Board click at ({row}, {col})")
                return ((row, col), None, -1)
        
        # Check if click is on left side panel (white pieces)
        pieces_start_y = top_panel_height + 60
        pieces_per_player = 6
        piece_height = 35
        pieces_end_y = pieces_start_y + pieces_per_player * piece_height
        
        print(f"  Left panel area: 0 <= x < {side_panel_width} and {pieces_start_y} <= y < {pieces_end_y}")
        if (0 <= x < side_panel_width and 
            pieces_start_y <= y < pieces_end_y):
            piece_index = (y - pieces_start_y) // piece_height
            print(f"  -> Left panel click, piece index: {piece_index}")
            return (None, 'white', piece_index)
        
        # Check if click is on right side panel (black pieces)
        right_panel_x = side_panel_width + board_width
        print(f"  Right panel area: {right_panel_x} <= x < {window_width} and {pieces_start_y} <= y < {pieces_end_y}")
        if (right_panel_x <= x < window_width and 
            pieces_start_y <= y < pieces_end_y):
            piece_index = (y - pieces_start_y) // piece_height
            print(f"  -> Right panel click, piece index: {piece_index}")
            return (None, 'black', piece_index)
        
        print(f"  -> Click outside recognized areas")
        return None
    
    # Test the problematic clicks
    test_clicks = [(57, 327), (56, 321)]
    
    for click in test_clicks:
        result = get_clicked_position(click)
        print(f"Result: {result}")
        print()

if __name__ == "__main__":
    test_click_detection()
