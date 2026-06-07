import os
import datetime
import requests
from supabase import create_client, Client

# --- CONFIGURATION ---
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_KEY = os.environ.get("SUPABASE_KEY")
WEBHOOK_URL = os.environ.get("WEBHOOK_URL")

# Initialize Supabase Client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def send_alert(event_data):
    """Sends a beautifully formatted notification to your webhook."""
    # Format the local date for readability (e.g., 2026-06-07T15:00:00 -> 2026-06-07 at 15:00:00)
    raw_date = event_data.get("local_date", "TBD")
    formatted_date = raw_date.replace("TBD", "").replace("T", " at ")

    venue_info = event_data.get("venue", {})
    venue_name = venue_info.get("name", "Unknown Venue")
    city = venue_info.get("city", "")
    state = venue_info.get("state_code", "")
    location = f"{venue_name} ({city}, {state})" if city else venue_name

    event_id = event_data.get("id")
    event_url = f"https://entertainment.capitalone.com/events/{event_id}"
    
    # Check if the event is marked as SOLD_OUT in its tags
    tags = event_data.get("tags", [])
    is_sold_out = "SOLD_OUT" in tags
    status_emoji = "❌ SOLD OUT" if is_sold_out else "✅ TICKETS AVAILABLE"

    # Construct a clean, structured text alert
    message = (
        f"🚨 **New Capital One Exclusive Event Detected!**\n"
        f"--------------------------------------------\n"
        f"🎫 **Event Name:** {event_data.get('name')}\n"
        f"📅 **Date/Time:** {formatted_date}\n"
        f"📍 **Location:** {location}\n"
        f"📊 **Status:** {status_emoji}\n"
        f"🔗 **Link:** <{event_url}>\n"
        f"--------------------------------------------"
    )

    payload = {"content": message}
    requests.post(WEBHOOK_URL, json=payload)

def main():
    # 1. Fetch events from Capital One API
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    api_url = f"https://entertainment-bff.capitalone.com/events?date_start={today}&tag_filter=C1_EXCLUSIVE+AND+NOT+COLLAPSED&page=1&per_page=200"
    
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

    data = response.json()
    api_events = data.get("items", []) # Updated from 'events' to 'items'
    
    if not api_events:
        print("No events found in the API response.")
        return

    print(f"Found {len(api_events)} total events. Checking against database...")

    # 2. Track new events
    for event in api_events:
        event_id = str(event.get("id"))
        event_name = event.get("name")
        event_url = f"https://entertainment.capitalone.com/events/{event_id}"

        # 3. Query Supabase to see if this ID already exists
        check_db = supabase.table("exclusive_events").select("id").eq("id", event_id).execute()
        
        if len(check_db.data) == 0:
            print(f"✨ New event detected: {event_name}")
            
            # 4. Insert the new event into Supabase so we don't alert again
            supabase.table("exclusive_events").insert({
                "id": event_id,
                "name": event_name,
                "url": event_url
            }).execute()
            
            # 5. Send the rich notification
            send_alert(event)

            print("🚨 DEBUG - RAW API PAYLOAD RECEIVED:")
            print(data)
            
    print("Check complete. Database updated.")

if __name__ == "__main__":
    main()