import json
import threading
from api_client import FoxholeAPI

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
    
    # Save reports to file
    try:
        with open("war_reports.json", "w") as f:
            json.dump({'reports': [current_reports]}, f)
        print("Successfully updated war_reports.json")
    except Exception as e:
        print(f"Error saving war reports: {e}")

def schedule_update():
    """Schedule the next update in 10 minutes"""
    threading.Timer(600, schedule_update).start()
    update_war_reports()

if __name__ == "__main__":
    print("Starting war reports updater. Updates will run every 10 minutes.")
    schedule_update()