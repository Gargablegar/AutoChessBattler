#!/usr/bin/env python3
"""
Test script for AutoTurns input message functionality
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

class MockUI:
    """Mock UI class to test AutoTurns input message logic"""
    def __init__(self):
        self.auto_turns_input_active = False
    
    def activate_auto_turns_input(self):
        self.auto_turns_input_active = True
        print("AutoTurns input activated")
    
    def deactivate_auto_turns_input(self):
        self.auto_turns_input_active = False
        print("AutoTurns input deactivated")

def test_autoturns_message_logic():
    """Test the AutoTurns input message display logic"""
    print("Testing AutoTurns Input Message Logic")
    print("=" * 40)
    
    # Mock game state
    ui = MockUI()
    error_message = ""
    winner = ""
    game_over = False
    
    def get_display_message():
        """Simulate the game's display message logic"""
        display_message = winner if game_over else error_message
        
        # Show AutoTurns input instruction when the field is active
        if ui.auto_turns_input_active and not display_message:
            display_message = "Type a number and press Enter."
        
        return display_message
    
    # Test 1: Normal state - no message
    print("\n1. Normal state (no messages):")
    message = get_display_message()
    print(f"   Display message: '{message}'")
    print(f"   Expected: '' (empty)")
    print(f"   ✓ Correct" if message == "" else f"   ✗ Wrong")
    
    # Test 2: AutoTurns input activated - should show instruction
    print("\n2. AutoTurns input activated:")
    ui.activate_auto_turns_input()
    message = get_display_message()
    expected = "Type a number and press Enter."
    print(f"   Display message: '{message}'")
    print(f"   Expected: '{expected}'")
    print(f"   ✓ Correct" if message == expected else f"   ✗ Wrong")
    
    # Test 3: AutoTurns input active but error message present - error takes priority
    print("\n3. AutoTurns input active + error message:")
    error_message = "Invalid position!"
    message = get_display_message()
    print(f"   Display message: '{message}'")
    print(f"   Expected: '{error_message}' (error takes priority)")
    print(f"   ✓ Correct" if message == error_message else f"   ✗ Wrong")
    
    # Test 4: AutoTurns input active but game over - winner takes priority
    print("\n4. AutoTurns input active + game over:")
    error_message = ""  # Clear error
    game_over = True
    winner = "White wins!"
    message = get_display_message()
    print(f"   Display message: '{message}'")
    print(f"   Expected: '{winner}' (winner takes priority)")
    print(f"   ✓ Correct" if message == winner else f"   ✗ Wrong")
    
    # Test 5: AutoTurns input deactivated - back to normal
    print("\n5. AutoTurns input deactivated:")
    ui.deactivate_auto_turns_input()
    game_over = False
    winner = ""
    message = get_display_message()
    print(f"   Display message: '{message}'")
    print(f"   Expected: '' (empty)")
    print(f"   ✓ Correct" if message == "" else f"   ✗ Wrong")
    
    print(f"\n✅ AutoTurns input message logic test completed!")
    print("\nMessage Priority Order:")
    print("  1. Winner message (if game over)")
    print("  2. Error message (if present)")
    print("  3. AutoTurns input instruction (if input active)")
    print("  4. No message (default)")

if __name__ == "__main__":
    test_autoturns_message_logic()
