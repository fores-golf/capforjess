import datetime
import requests
import json

def main():
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    api_url = f"https://entertainment-bff.capitalone.com/events?date_start={today}&tag_filter=C1_EXCLUSIVE+AND+NOT+COLLAPSED&page=1&per_page=1"

    headers = {
        "Accept": "application/json, text/plain, */*",
        "Accept-Language": "en-US,en;q=0.9",
        "Origin": "https://entertainment.capitalone.com",
        "Referer": "https://entertainment.capitalone.com/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
    }

    print("Fetching one event from Capital One API...")
    response = requests.get(api_url, headers=headers)
    
    if response.status_code == 200:
        data = response.json()
        events_list = data.get("events", []) # Assuming the key is 'events'
        
        if events_list:
            print("\n--- RAW EVENT BLUEPRINT ---")
            # This prints the first event beautifully formatted
            print(json.dumps(events_list[0], indent=4))
        else:
            print("The API returned data, but couldn't find the events list. Here is the raw response:")
            print(json.dumps(data, indent=4))
    else:
        print(f"Failed! Status Code: {response.status_code}")

if __name__ == "__main__":
    main()