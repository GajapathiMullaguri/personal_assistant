#!/usr/bin/env python3
"""
Launcher script for the Streamlit AI Personal Assistant.
This script ensures proper Python path setup for imports.
"""

import sys
import os
import subprocess
from pathlib import Path

def main():
    # Get the project root directory
    project_root = Path(__file__).parent.absolute()
    
    # Change to project root directory
    os.chdir(project_root)
    
    # Add project root to Python path
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    
    print(f"Project root: {project_root}")
    print(f"Working directory: {os.getcwd()}")
    print(f"Python path includes project root: {str(project_root) in sys.path}")
    
    # Set environment variable to help with imports
    os.environ['PYTHONPATH'] = str(project_root)
    
    # Run Streamlit with the app
    streamlit_app_path = project_root / "src" / "ui" / "streamlit_app.py"
    
    if not streamlit_app_path.exists():
        print(f"Error: Streamlit app not found at {streamlit_app_path}")
        return 1
    
    print(f"Running Streamlit app: {streamlit_app_path}")
    
    # Use subprocess to run streamlit
    try:
        result = subprocess.run([
            sys.executable, "-m", "streamlit", "run", 
            str(streamlit_app_path)
        ], cwd=project_root)
        return result.returncode
    except KeyboardInterrupt:
        print("\nStreamlit app stopped by user")
        return 0
    except Exception as e:
        print(f"Error running Streamlit: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
