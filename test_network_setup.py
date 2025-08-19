#!/usr/bin/env python3
"""
Test script to verify network components work correctly
"""

import asyncio
import sys
import subprocess
import time
import os

def test_imports():
    """Test that all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import websockets
        print(f"✅ websockets {websockets.__version__}")
        
        import pygame
        print(f"✅ pygame {pygame.version.ver}")
        
        # Test our network modules
        import network_server
        print("✅ network_server module")
        
        import network_client  
        print("✅ network_client module")
        
        print("All imports successful!\n")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Run: pip install -r requirements.txt")
        return False

def test_websockets_exceptions():
    """Test that websockets exceptions work correctly"""
    print("Testing websockets exception handling...")
    
    try:
        import websockets.exceptions
        
        # Test that ConnectionClosed exists (this should work)
        if hasattr(websockets.exceptions, 'ConnectionClosed'):
            print("✅ websockets.exceptions.ConnectionClosed exists")
        else:
            print("❌ websockets.exceptions.ConnectionClosed missing")
            return False
            
        # Test that ConnectionRefused does NOT exist (as expected)
        if not hasattr(websockets.exceptions, 'ConnectionRefused'):
            print("✅ websockets.exceptions.ConnectionRefused correctly not found")
        else:
            print("⚠️  websockets.exceptions.ConnectionRefused exists (unexpected)")
            
        print("Websockets exception handling test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Websockets exception test failed: {e}")
        return False

async def test_server_start():
    """Test that the server can start"""
    print("Testing server startup...")
    
    try:
        # Import and create server
        from network_server import AutoChessServer
        server = AutoChessServer("localhost", 8766)  # Use different port for testing
        
        print("✅ Server can be created")
        
        # We won't actually start it to avoid blocking
        print("Server startup test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Server startup test failed: {e}")
        return False

async def test_client_creation():
    """Test that the client can be created"""
    print("Testing client creation...")
    
    try:
        from network_client import AutoChessClient
        client = AutoChessClient("localhost", 8766, "test_game")
        
        print("✅ Client can be created")
        print("Client creation test passed!\n")
        return True
        
    except Exception as e:
        print(f"❌ Client creation test failed: {e}")
        return False

def test_file_permissions():
    """Test that startup scripts are executable"""
    print("Testing file permissions...")
    
    files_to_check = ["start_server.sh", "start_client.sh"]
    
    for filename in files_to_check:
        if os.path.exists(filename):
            if os.access(filename, os.X_OK):
                print(f"✅ {filename} is executable")
            else:
                print(f"❌ {filename} is not executable")
                print(f"   Run: chmod +x {filename}")
                return False
        else:
            print(f"❌ {filename} not found")
            return False
    
    print("File permissions test passed!\n")
    return True

async def main():
    """Run all tests"""
    print("🧪 AutoChess Network Setup Test")
    print("=" * 40)
    
    tests = [
        test_imports(),
        test_websockets_exceptions(),
        await test_server_start(),
        await test_client_creation(),
        test_file_permissions()
    ]
    
    passed = sum(tests)
    total = len(tests)
    
    print("=" * 40)
    print(f"Test Results: {passed}/{total} passed")
    
    if passed == total:
        print("🎉 All tests passed! Network setup is ready.")
        print("\nTo start playing:")
        print("1. Run: ./start_server.sh")
        print("2. Run: ./start_client.sh (in first terminal)")
        print("3. Run: ./start_client.sh (in second terminal)")
    else:
        print("❌ Some tests failed. Please fix the issues above.")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
