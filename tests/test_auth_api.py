#!/usr/bin/env python3
"""
Test script for IEEE Paper Generator Authentication API
Run this to test all authentication endpoints
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def print_response(title, response):
    print(f"\n{'='*60}")
    print(f"{title}")
    print(f"{'='*60}")
    print(f"Status Code: {response.status_code}")
    try:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Response: {response.text}")

def test_signup():
    print("\n" + "="*60)
    print("TEST 1: SIGN UP")
    print("="*60)
    
    data = {
        "email": "testuser@example.com",
        "password": "testpass123",
        "full_name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=data)
    print_response("Sign Up Response", response)
    
    if response.status_code == 200:
        token = response.json().get("token")
        return token
    return None

def test_login(email="testuser@example.com", password="testpass123"):
    print("\n" + "="*60)
    print("TEST 2: LOGIN")
    print("="*60)
    
    data = {
        "email": email,
        "password": password
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response("Login Response", response)
    
    if response.status_code == 200:
        token = response.json().get("token")
        return token
    return None

def test_verify(token):
    print("\n" + "="*60)
    print("TEST 3: VERIFY TOKEN")
    print("="*60)
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    response = requests.get(f"{BASE_URL}/auth/verify", headers=headers)
    print_response("Verify Token Response", response)

def test_invalid_login():
    print("\n" + "="*60)
    print("TEST 4: INVALID LOGIN")
    print("="*60)
    
    data = {
        "email": "testuser@example.com",
        "password": "wrongpassword"
    }
    
    response = requests.post(f"{BASE_URL}/auth/login", json=data)
    print_response("Invalid Login Response", response)

def test_signup_duplicate():
    print("\n" + "="*60)
    print("TEST 5: DUPLICATE EMAIL")
    print("="*60)
    
    data = {
        "email": "testuser@example.com",
        "password": "anotherpass123",
        "full_name": "Another User"
    }
    
    response = requests.post(f"{BASE_URL}/auth/signup", json=data)
    print_response("Duplicate Signup Response", response)

if __name__ == "__main__":
    print("\n" + "#"*60)
    print("# IEEE Paper Generator - Authentication API Tests")
    print("#"*60)
    
    # Test 1: Sign Up
    token = test_signup()
    
    # Test 2: Login
    if token:
        test_login()
    else:
        print("\nSkipping login test (signup failed)")
    
    # Test 3: Verify Token
    if token:
        test_verify(token)
    else:
        print("\nSkipping verify test (no token)")
    
    # Test 4: Invalid Login
    test_invalid_login()
    
    # Test 5: Duplicate Signup
    test_signup_duplicate()
    
    print("\n" + "#"*60)
    print("# Test Complete")
    print("#"*60 + "\n")
