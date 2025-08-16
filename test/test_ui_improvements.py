#!/usr/bin/env python3
"""
Test script for piece deselection and AutoTurns input improvements
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from autochess_pieces import King, Queen, Pawn

class MockUI:
    """Mock UI class to test AutoTurns input behavior"""
    def __init__(self):
        self.auto_turns_input_active = False
        self.auto_turns_text = ""
    
    def activate_auto_turns_input(self):
        self.auto_turns_input_active = True
    
    def deactivate_auto_turns_input(self):
        self.auto_turns_input_active = False

def test_piece_deselection_logic():
    """Test the piece deselection logic"""
    print("Testing Piece Deselection Logic")
    print("=" * 35)
    
    # Mock pieces
    white_king = King("white")
    white_queen = Queen("white") 
    black_pawn = Pawn("black")
    
    selected_piece = None
    
    def select_piece_for_placement(piece):
        nonlocal selected_piece
        selected_piece = piece
        print(f"  Selected: {piece.color} {piece.__class__.__name__}")
    
    def deselect_piece():
        nonlocal selected_piece
        if selected_piece:
            print(f"  Deselected: {selected_piece.color} {selected_piece.__class__.__name__}")
        selected_piece = None
    
    def handle_piece_click(clicked_piece):
        """Simulate the improved piece selection logic"""
        # If clicking the same piece that's already selected, deselect it
        if (selected_piece and 
            selected_piece.color == clicked_piece.color and 
            selected_piece.__class__.__name__ == clicked_piece.__class__.__name__):
            deselect_piece()
        else:
            select_piece_for_placement(clicked_piece)
    
    # Test 1: Select a piece
    print("\n1. Selecting white king:")
    handle_piece_click(white_king)
    print(f"   Currently selected: {selected_piece.__class__.__name__ if selected_piece else 'None'}")
    
    # Test 2: Click same piece again - should deselect
    print("\n2. Clicking white king again (should deselect):")
    handle_piece_click(white_king)
    print(f"   Currently selected: {selected_piece.__class__.__name__ if selected_piece else 'None'}")
    
    # Test 3: Select different piece
    print("\n3. Selecting white queen:")
    handle_piece_click(white_queen)
    print(f"   Currently selected: {selected_piece.__class__.__name__ if selected_piece else 'None'}")
    
    # Test 4: Click different piece - should switch selection
    print("\n4. Clicking black pawn (should switch selection):")
    handle_piece_click(black_pawn)
    print(f"   Currently selected: {selected_piece.__class__.__name__ if selected_piece else 'None'}")
    
    # Test 5: Click same piece again - should deselect
    print("\n5. Clicking black pawn again (should deselect):")
    handle_piece_click(black_pawn)
    print(f"   Currently selected: {selected_piece.__class__.__name__ if selected_piece else 'None'}")
    
    print(f"\n✅ Piece deselection logic test completed!")

def test_autoturns_input_logic():
    """Test the AutoTurns input logic"""
    print("\n\nTesting AutoTurns Input Logic")
    print("=" * 30)
    
    ui = MockUI()
    auto_turns = 1  # Default value
    
    def activate_input():
        """Simulate clicking the AutoTurns field"""
        ui.auto_turns_text = ""  # Clear field when activating
        ui.activate_auto_turns_input()
        print("  AutoTurns field activated (cleared)")
    
    def handle_digit_input(digit_char):
        """Simulate typing a digit"""
        nonlocal auto_turns
        if ui.auto_turns_input_active and digit_char.isdigit() and len(ui.auto_turns_text) < 3:
            ui.auto_turns_text += digit_char
            # Auto-apply the new value immediately
            try:
                new_value = max(1, int(ui.auto_turns_text))
                auto_turns = new_value
                print(f"  Typed '{digit_char}' → Field: '{ui.auto_turns_text}' → AutoTurns: {auto_turns}")
            except ValueError:
                pass
    
    def handle_backspace():
        """Simulate backspace"""
        nonlocal auto_turns
        if ui.auto_turns_input_active:
            ui.auto_turns_text = ui.auto_turns_text[:-1]
            if not ui.auto_turns_text:
                print(f"  Backspace → Field cleared → AutoTurns remains: {auto_turns}")
            else:
                try:
                    new_value = max(1, int(ui.auto_turns_text))
                    auto_turns = new_value
                    print(f"  Backspace → Field: '{ui.auto_turns_text}' → AutoTurns: {auto_turns}")
                except ValueError:
                    pass
    
    def handle_enter():
        """Simulate pressing Enter"""
        ui.deactivate_auto_turns_input()
        print(f"  Enter pressed → Input deactivated → Final AutoTurns: {auto_turns}")
    
    # Test 1: Activate input field
    print("\n1. Activating AutoTurns input (current value: 1):")
    activate_input()
    print(f"   Field text: '{ui.auto_turns_text}'")
    print(f"   Input active: {ui.auto_turns_input_active}")
    
    # Test 2: Type digit
    print("\n2. Typing '5':")
    handle_digit_input('5')
    
    # Test 3: Type another digit
    print("\n3. Typing '0' (should become 50):")
    handle_digit_input('0')
    
    # Test 4: Backspace
    print("\n4. Pressing backspace:")
    handle_backspace()
    
    # Test 5: Backspace again (clear field)
    print("\n5. Pressing backspace again (clear field):")
    handle_backspace()
    
    # Test 6: Type new number
    print("\n6. Typing '3':")
    handle_digit_input('3')
    
    # Test 7: Press Enter to finish
    print("\n7. Pressing Enter to finish:")
    handle_enter()
    
    print(f"\n✅ AutoTurns input logic test completed!")
    print("\nNew Behavior Summary:")
    print("  • Field clears when activated (no pre-filled value)")
    print("  • Values auto-apply as you type (no need to press Enter)")
    print("  • Enter key deactivates input mode")
    print("  • Backspace works normally, field clearing keeps current value")

if __name__ == "__main__":
    test_piece_deselection_logic()
    test_autoturns_input_logic()
