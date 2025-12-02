#!/usr/bin/env python3
"""
Test script for user settings functionality.
"""

import requests
import json

API_URL = "http://localhost:5000"

def test_get_settings_schema():
    """Test getting settings schema."""
    print("\n=== Testing GET /settings/schema ===")
    response = requests.get(f"{API_URL}/settings/schema")
    data = response.json()
    
    if data['success']:
        print("✅ Settings schema retrieved successfully")
        print(f"   Available categories: {list(data['schema'].keys())}")
    else:
        print("❌ Failed to get settings schema")
    
    return data

def test_get_default_settings():
    """Test getting default settings."""
    print("\n=== Testing GET /settings (default user) ===")
    response = requests.get(f"{API_URL}/settings?user_id=default")
    data = response.json()
    
    if data['success']:
        print("✅ Default settings retrieved successfully")
        print(f"   Using defaults: {data['using_defaults']}")
        print(f"   Summary temperature: {data['settings']['summary_temperature']}")
        print(f"   Quiz num questions: {data['settings']['quiz_num_questions']}")
    else:
        print("❌ Failed to get default settings")
    
    return data

def test_update_settings():
    """Test updating user settings."""
    print("\n=== Testing POST /settings (update) ===")
    
    new_settings = {
        "summary_temperature": 0.3,
        "quiz_num_questions": 15,
        "chatbot_temperature": 0.8
    }
    
    response = requests.post(
        f"{API_URL}/settings",
        json={
            "user_id": "test_user",
            "settings": new_settings
        }
    )
    data = response.json()
    
    if data['success']:
        print("✅ Settings updated successfully")
        print(f"   Updated {data['message']}")
        print(f"   New summary temp: {data['settings']['summary_temperature']}")
        print(f"   New quiz questions: {data['settings']['quiz_num_questions']}")
    else:
        print("❌ Failed to update settings")
    
    return data

def test_get_custom_settings():
    """Test getting custom settings."""
    print("\n=== Testing GET /settings (custom user) ===")
    response = requests.get(f"{API_URL}/settings?user_id=test_user")
    data = response.json()
    
    if data['success']:
        print("✅ Custom settings retrieved successfully")
        print(f"   Has custom settings: {data['has_custom_settings']}")
        print(f"   Summary temperature: {data['settings']['summary_temperature']}")
        print(f"   Quiz num questions: {data['settings']['quiz_num_questions']}")
    else:
        print("❌ Failed to get custom settings")
    
    return data

def test_reset_settings():
    """Test resetting settings to defaults."""
    print("\n=== Testing POST /settings/reset ===")
    
    response = requests.post(
        f"{API_URL}/settings/reset",
        json={"user_id": "test_user"}
    )
    data = response.json()
    
    if data['success']:
        print("✅ Settings reset successfully")
        print(f"   Message: {data['message']}")
        print(f"   Summary temperature: {data['settings']['summary_temperature']}")
    else:
        print("❌ Failed to reset settings")
    
    return data

def main():
    """Run all tests."""
    print("=" * 60)
    print("USER SETTINGS API TESTS")
    print("=" * 60)
    
    try:
        # Test 1: Get schema
        test_get_settings_schema()
        
        # Test 2: Get default settings
        test_get_default_settings()
        
        # Test 3: Update settings
        test_update_settings()
        
        # Test 4: Get custom settings
        test_get_custom_settings()
        
        # Test 5: Reset settings
        test_reset_settings()
        
        # Test 6: Verify reset worked
        test_get_custom_settings()
        
        print("\n" + "=" * 60)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

