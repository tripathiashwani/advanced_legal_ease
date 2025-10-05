#!/usr/bin/env python3

"""
Test script to verify Kafka event flow for user signup
"""

import requests
import json
import time
import sys
import subprocess

def test_kafka_flow():
    print("=== Testing Legal Ease Kafka Event Flow ===\n")
    
    # Test data
    test_user = {
        "username": "testuser",
        "email": "test@example.com", 
        "password": "TestPassword123!",
        "user_type": "PETITIONER",
        "bar_number": "TEST123",
        "license_number": "LIC123"
    }
    
    print("1. Testing User Signup with Kafka Event...")
    
    try:
        # Sign up user
        signup_response = requests.post(
            "http://localhost:8000/accounts/signup/",
            json=test_user,
            headers={'Content-Type': 'application/json'}
        )
        
        print(f"   Signup Status: {signup_response.status_code}")
        
        if signup_response.status_code == 201:
            response_data = signup_response.json()
            print(f"   User Created: {response_data.get('message', 'Success')}")
            print(f"   User ID: {response_data.get('user', {}).get('id', 'N/A')}")
            
            # Check if Kafka event was sent (check Django logs)
            print("\n2. Checking if Kafka event was published...")
            print("   Check the Django server logs for:")
            print("   - 'User signup event published for user test@example.com'")
            print("   - Or 'Kafka disabled. Would send to user_signed_up: ...'")
            
        else:
            print(f"   Signup failed: {signup_response.text}")
            
    except requests.exceptions.ConnectionError:
        print("   ❌ Cannot connect to auth service at localhost:8000")
        print("   Make sure the Django auth service is running:")
        print("   cd services/auth_service && python manage.py runserver 8000")
        return False
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False
    
    print("\n3. Testing Kafka Consumer...")
    print("   To test the notification service consumer:")
    print("   cd services/notification_service")
    print("   python manage.py consume_notifications")
    
    print("\n4. Verifying Kafka Topics...")
    try:
        # List Kafka topics
        result = subprocess.run([
            "docker", "exec", "-it", "kafka", 
            "kafka-topics", "--list", "--bootstrap-server", "localhost:9092"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            topics = result.stdout.strip().split('\n')
            print(f"   Available topics: {topics}")
            
            if 'user_signed_up' in topics or 'notification-events' in topics:
                print("   ✅ Kafka topics are available")
            else:
                print("   ⚠️  Expected topics not found")
        else:
            print(f"   ⚠️  Could not list topics: {result.stderr}")
            
    except subprocess.TimeoutExpired:
        print("   ⚠️  Timeout listing Kafka topics")
    except FileNotFoundError:
        print("   ⚠️  Docker not found - cannot check Kafka topics")
    except Exception as e:
        print(f"   ⚠️  Error checking topics: {e}")
    
    print("\n=== Manual Testing Instructions ===")
    print("1. Start the notification consumer:")
    print("   cd services/notification_service")
    print("   python manage.py consume_notifications")
    print()
    print("2. In another terminal, test signup:")
    print("   curl -X POST http://localhost:8000/accounts/signup/ \\")
    print("        -H 'Content-Type: application/json' \\")
    print("        -d '{")
    print('            "username": "testuser2",')
    print('            "email": "test2@example.com",')
    print('            "password": "TestPassword123!",')
    print('            "user_type": "PETITIONER"')
    print("        }'")
    print()
    print("3. Check logs in both terminals for Kafka events")
    
    return True

if __name__ == "__main__":
    test_kafka_flow()