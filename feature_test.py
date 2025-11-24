#!/usr/bin/env python3
"""
Comprehensive Feature Test - Check all critical features
"""

import requests
import time
import json

BASE_URL = "http://localhost:8001/api"

def test_feature(name, func):
    """Test a feature and report results"""
    print(f"\n🧪 Testing: {name}")
    try:
        start = time.time()
        result = func()
        elapsed = time.time() - start
        
        if result:
            print(f"✅ PASS ({elapsed:.3f}s)")
            return True
        else:
            print(f"❌ FAIL ({elapsed:.3f}s)")
            return False
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return False

def test_models():
    """Test models endpoint"""
    response = requests.get(f"{BASE_URL}/models", timeout=5)
    models = response.json().get('models', [])
    return response.status_code == 200 and len(models) > 0

def test_session_create():
    """Test session creation"""
    response = requests.post(
        f"{BASE_URL}/session/create",
        json={"project_name": "Feature Test"},
        timeout=5
    )
    data = response.json()
    global test_session_id
    test_session_id = data.get('session_id')
    return response.status_code == 200 and test_session_id is not None

def test_session_get():
    """Test getting session details"""
    response = requests.get(f"{BASE_URL}/session/{test_session_id}", timeout=5)
    return response.status_code == 200

def test_messages_get():
    """Test getting messages for session"""
    response = requests.get(f"{BASE_URL}/session/{test_session_id}/messages", timeout=5)
    return response.status_code == 200

def test_chat_message():
    """Test chat message endpoint"""
    response = requests.post(
        f"{BASE_URL}/chat/message",
        json={
            "session_id": test_session_id,
            "content": "Hello",
            "model": "gpt-5"
        },
        timeout=10
    )
    return response.status_code == 200

def test_session_create_speed():
    """Test session creation speed (should be < 1 second)"""
    start = time.time()
    response = requests.post(
        f"{BASE_URL}/session/create",
        json={"project_name": "Speed Test"},
        timeout=5
    )
    elapsed = time.time() - start
    return response.status_code == 200 and elapsed < 1.0

def test_netlify_project_get():
    """Test netlify session latest endpoint"""
    response = requests.get(f"{BASE_URL}/netlify/session/{test_session_id}/latest", timeout=5)
    # This should return 404 for new session with no projects, which is correct
    return response.status_code in [200, 404]

def main():
    print("=" * 60)
    print("🚀 CODE WEAVER - COMPREHENSIVE FEATURE TEST")
    print("=" * 60)
    
    tests = [
        ("Models Endpoint", test_models),
        ("Session Creation", test_session_create),
        ("Session Retrieval", test_session_get),
        ("Messages Retrieval", test_messages_get),
        ("Message Saving", test_message_save),
        ("Session Creation Speed (<1s)", test_session_create_speed),
        ("Netlify Models Endpoint", test_netlify_models),
    ]
    
    results = []
    for name, func in tests:
        results.append(test_feature(name, func))
    
    print("\n" + "=" * 60)
    print(f"📊 RESULTS: {sum(results)}/{len(results)} tests passed")
    print("=" * 60)
    
    if sum(results) == len(results):
        print("✅ ALL FEATURES WORKING!")
        return 0
    else:
        print("❌ SOME FEATURES BROKEN!")
        return 1

if __name__ == "__main__":
    test_session_id = None
    exit(main())
