import json
import time
from api_client import FoxholeAPI

# Define the absolute path to the war_reports.json file
WAR_REPORTS_PATH = "/home/ShaneeexD/FoxholeMapViewerAPI/war_reports.json"

AVAILABLE_MAPS = [
    "Acrithia", "AllodsBight", "AshFields", "BasinSionnach", "CallahansPassage",
    "CallumsCape", "Clahstra", "ClansheadValley", "DeadLands", "DrownedVale",
    "EndlessShore", "FarranacCoast", "FishermansRow", "Godcrofts", "GreatMarch",
    "Heartlands", "HowlCounty", "Kalokai", "KingsCage", "LinnMercy", "LochMor",
    "MarbanHollow", "MooringCounty", "MorgensCrossing", "NevishLine", "Oarbreaker",
    "Origin", "ReachingTrail", "ReaversPass", "RedRiver", "Sableport",
    "ShackledChasm", "SpeakingWoods", "StemaLanding", "StlicanShelf", "Stonecradle",
    "TempestIsland", "Terminus", "TheFingers", "UmbralWildwood", "ViperPit",
    "WeatheredExpanse", "Westgate"
]

def get_api_map_name(map_name):
    """Convert map name to API format"""
    if map_name == "MarbanHollow":
        return map_name
    return f"{map_name}Hex"

def update_war_reports():
    """Fetch war reports for all maps and save to war_reports.json"""
    api = FoxholeAPI()
    current_reports = {}
    
    # Fetch current war reports for all maps
    for map_name in AVAILABLE_MAPS:
        try:
            report = api.get_war_report(get_api_map_name(map_name))
            if report:
                current_reports[map_name] = report
        except Exception as e:
            print(f"Error fetching war report for {map_name}: {e}")
    
    # Load existing reports
    reports = []
    try:
        with open(WAR_REPORTS_PATH, "r") as f:
            existing_data = json.load(f)
            reports = existing_data.get('reports', [])
            print(f"Loaded {len(reports)} existing reports")
    except FileNotFoundError:
        print("No existing war_reports.json found, starting fresh")
    except json.JSONDecodeError as e:
        print(f"Error decoding war_reports.json: {e}. Starting fresh")
    except Exception as e:
        print(f"Unexpected error loading war_reports.json: {e}. Starting fresh")
    
    # Add new report and maintain only last 6 reports
    reports.append(current_reports)
    reports = reports[-6:]
    print(f"Storing {len(reports)} reports")
    
    # Save updated reports to file
    try:
        with open(WAR_REPORTS_PATH, "w") as f:
            json.dump({'reports': reports}, f)
        print("Successfully updated war_reports.json")
    except Exception as e:
        print(f"Error saving war reports: {e}")

if __name__ == "__main__":
    print("Starting war reports updater. Updates will run every 10 minutes.")
    while True:
        update_war_reports()
        print("Waiting for 10 minutes before the next update...")
        time.sleep(600)  # Wait for 10 minutes (600 seconds)
