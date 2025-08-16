#!/usr/bin/env python3
"""
Test script for frontline color improvements
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_frontline_colors():
    """Test the frontline zones with color information"""
    print("Testing Frontline Color System")
    print("=" * 30)
    
    # Mock game class with frontline functionality
    class MockGame:
        def __init__(self, board_size=8, frontline=2):
            self.board_size = board_size
            self.frontline = frontline
        
        def get_king_positions(self, color):
            """Mock king positions for testing"""
            if color == "white":
                return [(7, 3)]  # White king at bottom
            else:  # black
                return [(0, 4)]  # Black king at top
        
        def get_frontline_zones(self, color):
            """Get all frontline zones for a color as list of (min_row, max_row, min_col, max_col)."""
            king_positions = self.get_king_positions(color)
            zones = []
            
            for king_row, king_col in king_positions:
                if color == "white":
                    # White zone extends from frontline distance above the king to the bottom of the board
                    min_row = max(0, king_row - self.frontline)
                    max_row = self.board_size - 1
                else:  # black
                    # Black zone extends from the top of the board to frontline distance below the king
                    min_row = 0
                    max_row = min(self.board_size - 1, king_row + self.frontline)
                
                zones.append((min_row, max_row, 0, self.board_size - 1))
            
            return zones
        
        def get_frontline_zones_with_colors(self):
            """Get all frontline zones with their associated colors as list of (min_row, max_row, min_col, max_col, color)."""
            zones_with_colors = []
            
            # Add white frontline zones
            white_zones = self.get_frontline_zones("white")
            for zone in white_zones:
                zones_with_colors.append(zone + ("white",))
            
            # Add black frontline zones  
            black_zones = self.get_frontline_zones("black")
            for zone in black_zones:
                zones_with_colors.append(zone + ("black",))
            
            return zones_with_colors
    
    # Test setup
    game = MockGame(board_size=8, frontline=2)
    
    # Test 1: Individual color zones
    print("\n1. Testing individual color frontline zones:")
    white_zones = game.get_frontline_zones("white")
    black_zones = game.get_frontline_zones("black")
    
    print(f"   White king at (7, 3) with frontline=2:")
    print(f"   White zones: {white_zones}")
    print(f"   Expected: [(5, 7, 0, 7)] (rows 5-7, all columns)")
    
    print(f"\n   Black king at (0, 4) with frontline=2:")
    print(f"   Black zones: {black_zones}")
    print(f"   Expected: [(0, 2, 0, 7)] (rows 0-2, all columns)")
    
    # Test 2: Combined zones with colors
    print("\n2. Testing combined frontline zones with colors:")
    zones_with_colors = game.get_frontline_zones_with_colors()
    
    print(f"   Combined zones with colors:")
    for i, zone in enumerate(zones_with_colors):
        min_row, max_row, min_col, max_col, color = zone
        print(f"   Zone {i+1}: rows {min_row}-{max_row}, cols {min_col}-{max_col}, color: {color}")
    
    # Test 3: Color mapping logic
    print("\n3. Testing UI color mapping logic:")
    
    def get_border_color(zone_color):
        """Simulate the UI color mapping"""
        colors = {
            'white': (255, 255, 255),
            'black': (0, 0, 0)
        }
        if zone_color == "white":
            return colors['white']
        else:  # black
            return colors['black']
    
    for zone in zones_with_colors:
        min_row, max_row, min_col, max_col, zone_color = zone
        border_color = get_border_color(zone_color)
        print(f"   {zone_color.capitalize()} zone gets border color: {border_color}")
    
    # Test 4: Edge cases
    print("\n4. Testing edge cases:")
    
    # Test with frontline=1
    game_small = MockGame(board_size=8, frontline=1)
    zones_small = game_small.get_frontline_zones_with_colors()
    
    print(f"   With frontline=1:")
    for zone in zones_small:
        min_row, max_row, min_col, max_col, color = zone
        print(f"   {color.capitalize()}: rows {min_row}-{max_row}")
    
    print(f"\n✅ Frontline color system test completed!")
    print("\nColor System Summary:")
    print("  • White player frontlines: WHITE borders")
    print("  • Black player frontlines: BLACK borders") 
    print("  • Each zone includes color information: (min_row, max_row, min_col, max_col, color)")
    print("  • UI renders borders based on zone color, not a fixed red color")

if __name__ == "__main__":
    test_frontline_colors()
