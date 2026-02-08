
import requests
import json
import sys

API_URL = "http://localhost:8000/api/users"

def verify_user_update():
    # 1. Get all users
    response = requests.get(API_URL)
    if response.status_code != 200:
        print(f"❌ Failed to list users: {response.status_code}")
        return
    
    users = response.json()
    if not users:
        print("ℹ️ No users found to test update.")
        return
    
    test_user = users[0]
    user_id = test_user["id"]
    original_email = test_user.get("email", "")
    new_email = f"updated_{original_email}" if "@" in original_email else "updated@example.com"
    new_name = f"{test_user.get('name', 'User')} Updated"
    
    print(f"Testing update for user {user_id}...")
    
    # 2. Update user using PATCH
    update_payload = {
        "name": new_name,
        "email": new_email,
        "hourly_rate": 75.0
    }
    
    print(f"📤 Sending PATCH request with email: {new_email}")
    patch_response = requests.patch(f"{API_URL}/{user_id}", json=update_payload)
    
    if patch_response.status_code != 200:
        print(f"❌ PATCH failed: {patch_response.status_code}")
        print(patch_response.text)
        return
    
    print("✅ PATCH request successful.")
    
    # 3. Verify changes
    get_response = requests.get(f"{API_URL}/{user_id}")
    updated_user = get_response.json()
    
    if updated_user.get("email") == new_email and updated_user.get("name") == new_name:
        print("✅ SUCCESS: User name and email updated correctly.")
        print(f"   Name: {updated_user.get('name')}")
        print(f"   Email: {updated_user.get('email')}")
    else:
        print("❌ FAILED: User details did not match update payload.")
        print(f"   Expected Email: {new_email}, Got: {updated_user.get('email')}")
        print(f"   Expected Name: {new_name}, Got: {updated_user.get('name')}")

if __name__ == "__main__":
    verify_user_update()
