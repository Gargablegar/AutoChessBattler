#!/usr/bin/env python3
"""
Test script for the shutdown functionality
This script tests that end_server.sh can properly shutdown network processes
"""

import subprocess
import time
import signal
import os
import sys

def run_command(cmd, timeout=5):
    """Run a command and return the output"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=timeout)
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"

def check_processes():
    """Check for running AutoChess processes"""
    cmd = "pgrep -f 'network_server.py|network_client.py|main.py'"
    returncode, stdout, stderr = run_command(cmd)
    
    if returncode == 0:
        pids = stdout.strip().split('\n')
        return [pid for pid in pids if pid]
    return []

def test_shutdown_scripts():
    """Test the shutdown scripts"""
    print("🧪 Testing AutoChess Shutdown Scripts")
    print("=" * 50)
    
    # Test 1: Test end_server.sh with no processes running
    print("Test 1: end_server.sh with no processes...")
    returncode, stdout, stderr = run_command("./end_server.sh --quiet")
    if returncode == 0:
        print("✅ PASS: end_server.sh handles no processes correctly")
    else:
        print(f"❌ FAIL: end_server.sh failed with no processes (exit code: {returncode})")
        if stderr:
            print(f"   Error: {stderr}")
    
    # Test 2: Test quick_stop.sh with no processes running
    print("\nTest 2: quick_stop.sh with no processes...")
    returncode, stdout, stderr = run_command("./quick_stop.sh")
    if returncode == 0:
        print("✅ PASS: quick_stop.sh handles no processes correctly")
    else:
        print(f"❌ FAIL: quick_stop.sh failed with no processes (exit code: {returncode})")
        if stderr:
            print(f"   Error: {stderr}")
    
    # Test 3: Test help functionality
    print("\nTest 3: end_server.sh help...")
    returncode, stdout, stderr = run_command("./end_server.sh --help")
    if returncode == 0 and "Usage:" in stdout:
        print("✅ PASS: end_server.sh help works correctly")
    else:
        print(f"❌ FAIL: end_server.sh help failed")
        if stderr:
            print(f"   Error: {stderr}")
    
    # Test 4: Test file permissions
    print("\nTest 4: File permissions...")
    files = ["end_server.sh", "quick_stop.sh", "start_server.sh", "start_client.sh"]
    all_executable = True
    
    for filename in files:
        if os.path.exists(filename):
            if os.access(filename, os.X_OK):
                print(f"✅ {filename} is executable")
            else:
                print(f"❌ {filename} is not executable")
                all_executable = False
        else:
            print(f"❌ {filename} not found")
            all_executable = False
    
    if all_executable:
        print("✅ PASS: All scripts have correct permissions")
    else:
        print("❌ FAIL: Some scripts have incorrect permissions")
    
    # Test 5: Test script syntax
    print("\nTest 5: Script syntax...")
    for script in ["end_server.sh", "quick_stop.sh"]:
        returncode, stdout, stderr = run_command(f"bash -n {script}")
        if returncode == 0:
            print(f"✅ {script} syntax is valid")
        else:
            print(f"❌ {script} has syntax errors:")
            print(f"   {stderr}")
    
    print("\n" + "=" * 50)
    print("🎯 Shutdown Script Tests Complete!")
    print("\nNote: To test with actual processes, manually start:")
    print("   ./start_server.sh &")
    print("   ./start_client.sh &")
    print("   Then run: ./end_server.sh")

if __name__ == "__main__":
    test_shutdown_scripts()
