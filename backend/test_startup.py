"""
Quick startup test - verifies FastAPI app can be imported and basic structure works.
Run this before full pip install to verify basic setup.
"""

import sys
import os

# Add app directory to path
sys.path.insert(0, os.path.dirname(__file__))

try:
    from app.main import app
    print("✅ FastAPI app imported successfully")
    print(f"✅ App title: {app.title}")
    print(f"✅ App version: {app.version}")
    print("✅ Story 1.1 - Backend structure verified!")
except Exception as e:
    print(f"❌ Error importing app: {e}")
    sys.exit(1)
