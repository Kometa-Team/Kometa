import requests

def get_arr_version(url, api_key):
    """
    Connects to Radarr or Sonarr and reports the version.
    """
    # Standard endpoint for system status in Radarr/Sonarr v3+
    endpoint = f"{url}/api/v3/system/status"
    
    # Headers required for authentication
    headers = {
        'X-Api-Key': api_key,
        'Content-Type': 'application/json'
    }

    try:
        response = requests.get(endpoint, headers=headers)
        
        # Check if the connection was successful
        if response.status_code == 200:
            data = response.json()
            version = data.get("version")
            app_name = data.get("appName")
            print(f"Successfully connected to {app_name}!")
            print(f"Current Version: {version}")
        elif response.status_code == 401:
            print("Error: Invalid API Key.")
        else:
            print(f"Error: Received status code {response.status_code}")
            
    except requests.exceptions.RequestException as e:
        print(f"Connection Failed: {e}")

# --- CONFIGURATION ---
# Example for Radarr: "http://192.168.1.100:7878"
# Example for Sonarr: "http://192.168.1.100:8989"
BASE_URL = "http://192.168.1.11:8989" 
API_KEY = "SONARR KEY HERE"

get_arr_version(BASE_URL, API_KEY)

BASE_URL = "http://192.168.1.11:7878" 
API_KEY = "RaDARR KEY HERE"

get_arr_version(BASE_URL, API_KEY)

