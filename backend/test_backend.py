#!/usr/bin/env python
"""
Simple test script to verify backend is running
"""
import requests
import json

BASE_URL = 'http://localhost:8000/api'

print("=" * 60)
print("Testing FasalMitra Backend")
print("=" * 60)

# Test 1: Health check
print("\n[1] Testing health endpoint...")
try:
    response = requests.get('http://localhost:8000/health')
    print(f"✅ Health check: {response.status_code}")
except Exception as e:
    print(f"❌ Health check failed: {e}")

# Test 2: Register user
print("\n[2] Testing user registration...")
try:
    payload = {
        "name": "Test User",
        "email": f"test_{__import__('time').time_ns()}@example.com",
        "password": "test123"
    }
    response = requests.post(f'{BASE_URL}/auth/register', json=payload)
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    
    if response.status_code == 200:
        test_email = payload['email']
        test_password = payload['password']
        print(f"✅ Registration successful")
        print(f"  Email: {test_email}")
        print(f"  Password: {test_password}")
    else:
        print(f"❌ Registration failed: {response.text}")
except Exception as e:
    print(f"❌ Registration test failed: {e}")

print("\n" + "=" * 60)
