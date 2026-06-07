import os
import datetime
import requests
from supabase import create_client, Client

# --- CONFIGURATION ---
SUPABASE_URL = "YOUR_SUPABASE_PROJECT_URL"
SUPABASE_KEY = "YOUR_SUPABASE_ANON_KEY"
WEBHOOK_URL = "YOUR_DISCORD_OR_SLACK_WEBHOOK_URL"

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_alert(event_name, event_url):
    """Sends a notification to your webhook."""
    payload = {
        "content": f"🚨 **New Capital One Exclusive:** {event_name}\nCheck it out: {event_url}"
    }
    requests.post(WEBHOOK_URL, json=payload)

def main():
    # 1. Fetch events from Capital One API
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    api_url = f"https://entertainment-bff.capitalone.com/events?date_start={today}&tag_filter=C1_EXCLUSIVE+AND+NOT+COLLAPSED&page=1&per_page=100"
    
    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://entertainment.capitalone.com",
        "Referer": "https://entertainment.capitalone.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    }

    print("Fetching events from Capital One...")
    response = requests.get(api_url, headers=headers)
    if response.status_code != 200:
        print(f"Failed to fetch data! Status Code: {response.status_code}")
        return

    # Look through the API response (Adjust 'events' if we find the key name is different)
    data = response.json()
    api_events = data.get("events", []) # Or data.get("data", []) depending on debugging
    
    if not api_events:
        print("No events found in the API response. Double check the JSON key structure.")
        return

    # 2. Track new events
    for event in api_events:
        event_id = str(event.get("id"))
        event_name = event.get("name")
        event_url = f"https://entertainment.capitalone.com/events/{event_id}"

        # 3. Query Supabase to see if this ID already exists
        # .execute() returns data; if the list is empty, it's a brand new event
        check_db = supabase.table("exclusive_events").select("id").eq("id", event_id).execute()
        
        if len(check_db.data) == 0:
            print(f"✨ New event detected: {event_name}")
            
            # 4. Insert the new event into Supabase so we don't alert again next time
            supabase.table("exclusive_events").insert({
                "id": event_id,
                "name": event_name,
                "url": event_url
            }).execute()
            
            # 5. Send the notification
            send_alert(event_name, event_url)
            
    print("Check complete. Database updated.")

if __name__ == "__main__":
    main()