#!/usr/bin/env python3
"""
Test script to check imports and environment
"""

import sys
print(f"Python version: {sys.version}")
print(f"Python executable: {sys.executable}")
print(f"Python path: {sys.path}")

print("\nTesting imports...")

try:
    import boto3
    print("✅ boto3 imported successfully")
except ImportError as e:
    print(f"❌ boto3 import failed: {e}")

try:
    import ddgs
    print("✅ ddgs imported successfully")
except ImportError as e:
    print(f"❌ ddgs import failed: {e}")

try:
    import crewai
    print("✅ crewai imported successfully")
except ImportError as e:
    print(f"❌ crewai import failed: {e}")

try:
    from crewai.tools import tool
    print("✅ crewai.tools imported successfully")
except ImportError as e:
    print(f"❌ crewai.tools import failed: {e}")

print("\nDone!")
