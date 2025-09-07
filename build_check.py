#!/usr/bin/env python3
"""
Build validation script for PromptBin package

This script validates that the package can be built and installed correctly.
Run this before publishing to PyPI.
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

def run_command(cmd, cwd=None):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, shell=True, cwd=cwd, capture_output=True, text=True)
        if result.returncode != 0:
            print(f"❌ Command failed: {cmd}")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        else:
            print(f"✅ {cmd}")
            return True
    except Exception as e:
        print(f"❌ Error running {cmd}: {e}")
        return False

def main():
    """Main build validation"""
    print("🔍 PromptBin Package Build Validation")
    print("=" * 50)
    
    # Get the project root
    project_root = Path(__file__).parent
    
    # Step 1: Build the package
    print("\n1. Building package...")
    if not run_command("uv build", cwd=project_root):
        return 1
    
    # Step 2: Check that dist files were created
    dist_dir = project_root / "dist"
    if not dist_dir.exists():
        print("❌ dist/ directory not created")
        return 1
    
    wheel_files = list(dist_dir.glob("*.whl"))
    tar_files = list(dist_dir.glob("*.tar.gz"))
    
    if not wheel_files:
        print("❌ No wheel file created")
        return 1
    
    if not tar_files:
        print("❌ No source tarball created")
        return 1
    
    print(f"✅ Created wheel: {wheel_files[0].name}")
    print(f"✅ Created tarball: {tar_files[0].name}")
    
    # Step 3: Test installation in a temporary environment
    print("\n2. Testing installation...")
    with tempfile.TemporaryDirectory() as temp_dir:
        # Install the wheel file
        wheel_path = wheel_files[0]
        if not run_command(f"pip install {wheel_path}", cwd=temp_dir):
            return 1
        
        # Test that entry points work
        print("\n3. Testing entry points...")
        if not run_command("promptbin --help"):
            print("❌ promptbin entry point failed")
            return 1
            
        if not run_command("promptbin-mcp --help"):
            print("❌ promptbin-mcp entry point failed")
            return 1
            
        if not run_command("promptbin-setup --help"):
            print("❌ promptbin-setup entry point failed")
            return 1
    
    print("\n🎉 All validation checks passed!")
    print("\nNext steps:")
    print("1. Test manually: uv run promptbin-mcp")
    print("2. Publish to PyPI: uv publish")
    print("3. Test installation: uv add promptbin")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())