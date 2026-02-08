import requests
import json

hosts = ["http://127.0.0.1:8089", "http://localhost:8089"]

def test_top_contributors():
    for host in hosts:
        print(f"\nTesting Top Contributors Endpoint on {host}...")
        try:
            response = requests.get(f"{host}/api/analytics/team/top_contributors?limit=5", timeout=2)
            if response.status_code == 200:
                print("✅ Success! Response:")
                print(json.dumps(response.json(), indent=2))
                return
            else:
                print(f"❌ Failed with status {response.status_code}")
                print(response.text)
        except Exception as e:
            print(f"❌ Error connecting to {host}: {e}")

if __name__ == "__main__":
    test_top_contributors()
