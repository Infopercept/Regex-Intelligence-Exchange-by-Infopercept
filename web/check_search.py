import requests
import json

# Check what the search endpoint returns
url = "http://localhost:5000/api/patterns/search?q=Apache"
response = requests.get(url)
data = response.json()

print(f"Status Code: {response.status_code}")
print(f"Number of results: {len(data)}")
print(f"First result: {json.dumps(data[0] if data else None, indent=2)}")