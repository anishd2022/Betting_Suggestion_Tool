# import libraries
import requests  # For making HTTP requests
import json  # For handling JSON responses
import time
import pandas as pd
from datetime import datetime
import pytz
import os
from urllib.parse import urlencode


# save API key:
API_Key = "3d23e92b-6924-4ca7-a68a-5ccef6dc29bf"  # this is a one week trial key


# function to make get requests and return JSON response:
def make_request_and_return_response(url):
    response = requests.get(url)  # Make the GET request
    if response.status_code == 200:  # Check if the request was successful
        return response.json()  # Return the JSON response
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return json.dumps(None) # Return an error message


# Function to get the list of sports names
def list_all_sports():
    url = f"https://api.opticodds.com/api/v3/sports?key={API_Key}"
    data = make_request_and_return_response(url)
    if (data == 'null'):
        print("No sports found, returned empty list")
        return []
    # Extract sport IDs
    sport_ids = [sport["id"] for sport in data["data"]]
    return sport_ids

# sports = list_all_sports()
# print(sports)


# Function to get list of sports books:
def list_all_sportsbooks():
    url = f"https://api.opticodds.com/api/v3/sportsbooks?key={API_Key}"
    data = make_request_and_return_response(url)
    if (data == 'null'):
        print("No sportsbooks found, returned empty list")
        return []
    # extract sportsbook ids:
    sportsbook_ids = [sportsbook["id"] for sportsbook in data["data"]]
    return sportsbook_ids

# sportsbooks = list_all_sportsbooks()
# print(sportsbooks)


# Function to get all live fixtures for a given sport:
def list_live_fixtures(sport_name):
    url = f"https://api.opticodds.com/api/v3/fixtures/active?key={API_Key}&sport={sport_name}"
    return make_request_and_return_response(url)

# fixtures = list_live_fixtures("cricket")
# print(json.dumps(fixtures, indent=2))
        
        
# Function to get live odds for a given fixture / game:
    # ODDS_FORMAT: Needs to be one of the following (AMERICAN, DECIMAL, PROBABILITY, MALAY, HONG_KONG, INDONESIAN). This defaults to AMERICAN.
    # sportsbooks that cover cricket are typically "1xbet" and "bet365"
def get_live_odds_for_specific_game(game_ID, sportsbook, odds_format="AMERICAN", market=None):
    base_url = "https://api.opticodds.com/api/v3/fixtures/odds"
    
    # Start with required params
    query_params = [
        ("key", API_Key),
        ("fixture_id", game_ID),
        ("odds_format", odds_format),
    ]

    # Add sportsbook(s)
    if isinstance(sportsbook, list):
        query_params.extend([("sportsbook", sb) for sb in sportsbook])
    else:
        query_params.append(("sportsbook", sportsbook))

    # Add market(s) ONLY if provided
    if market is not None:
        if isinstance(market, list):
            query_params.extend([("market", m) for m in market])
        else:
            query_params.append(("market", market))

    # Build query string
    query_string = urlencode(query_params, doseq=True)
    full_url = f"{base_url}?{query_string}"

    return make_request_and_return_response(full_url)

# live_odds = get_live_odds_for_specific_game("2025022818E291B5", "bet365")
# print(json.dumps(live_odds, indent=2))


# Function to get historical odds for a given fixture / game:
def get_historical_odds_for_specific_game(game_ID, sportsbook="1xbet", odds_format="AMERICAN"):
    url = f"https://api.opticodds.com/api/v3/fixtures/odds/historical?key={API_Key}&fixture_id={game_ID}&sportsbook={sportsbook}&odds_format={odds_format}"
    return make_request_and_return_response(url)

# historical_odds = get_historical_odds_for_specific_game("2025022662FAA85C")
# print(json.dumps(historical_odds, indent=2))


# Function to get all historical fixtures for a specific sport within a given time frame:
    #  Start and end time follow ISO 8601 convention: ex: 2025-02-23T00:00:00Z
def list_historical_fixtures_within_given_time_frame(sport_name, start_time, end_time):
    url = f"https://api.opticodds.com/api/v3/fixtures?key={API_Key}&sport={sport_name}&start_date_after={start_time}&start_date_before={end_time}"
    return make_request_and_return_response(url)

# historical_fixtures = list_historical_fixtures_within_given_time_frame("cricket", "2025-02-23T00:00:00Z", "2025-02-27T00:00:00Z")
# print(json.dumps(historical_fixtures, indent=2))


# Function to get time_series historical odds for a specific fixture / game:
# this function returns null because they may not have timeseries data for cricket (check with OpticOdds people)
def get_timeseries_historical_odds_for_specific_game(game_ID, sportsbook="1xbet"):
    url = f"https://api.opticodds.com/api/v3/fixtures/odds/historical?key={API_Key}&sportsbook={sportsbook}&fixture_id={game_ID}&include_timeseries=True"
    return make_request_and_return_response(url)


# params:
#   game_ID: string corresponding to game_ID as seen in OpticOdds API
#   program_end_time: when you want the script to automatically stop running (in pacific standard time)
#       Ex: datetime(2025, 5, 22, 11, 20, 0), corresponds to May 22nd, 2025, at 11:20am PST
#   seconds_between_requests: numeric --> how many seconds between requests to capture new data
#   sportsbooks: array of strings --> ex: ["bet365", "1xbet", "bet365"] --> data will only be collected from these 3 books
# Output:
#   A .csv file with market odds for moneyline and and total_runs markets for various sportsbooks, 
#       recording timestamps as well. The .csv file is saved in the Data folder with naming convention {game_ID}.csv

def record_odds_data_for_game(game_ID, program_end_time, seconds_between_requests, sportsbooks):
    # CONFIG
    fixture_id = game_ID
    sportsbooks = sportsbooks  # Add as many as you want
    target_time = program_end_time  # 11:20 AM PST
    target_time = pytz.timezone('US/Pacific').localize(target_time)

    # FILE SETUP
    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{fixture_id}.csv")

    # LOOP
    while datetime.now(pytz.timezone('US/Pacific')) < target_time:
        collection_time = datetime.now(pytz.timezone("US/Pacific")).strftime("%Y-%m-%d %H:%M:%S")
        all_rows = []

        for book in sportsbooks:
            data = get_live_odds_for_specific_game(game_ID=fixture_id, sportsbook=book)

            if not data or "data" not in data or not data["data"]:
                print(f"No data received for {book}. Skipping...")
                continue

            odds_data = data["data"][0].get("odds", [])

            for odd in odds_data:
                name = odd.get("market", "").lower()
                market_id = odd.get("market_id", "").lower()

                # 🔍 FILTER markets: only include "moneyline" or anything with "team_total" in market_id
                if not (
                    market_id == "moneyline" or
                    market_id == "team_total" or
                    (market_id.startswith("1st_") and market_id.endswith("_overs_team_total"))
                ):
                    continue

                team_id = odd.get("team_id")
                price = odd.get("price")
                points = odd.get("points") if market_id != "moneyline" else ""

                # Determine over_under
                if name == "moneyline":
                    over_under = "over"
                elif odd.get("selection_line") in ["over", "under"]:
                    over_under = odd["selection_line"]
                else:
                    over_under = ""

                all_rows.append({
                    "timestamp": collection_time,
                    "sportsbook": book,
                    "market_id": market_id,
                    "team_id": team_id,
                    "over_under": over_under,
                    "price": price,
                    "points": points
                })

        # Save to CSV
        if all_rows:
            df = pd.DataFrame(all_rows)
            print(df)

            file_exists = os.path.isfile(file_path)
            df.to_csv(file_path, mode="a", index=False, header=not file_exists)

        # Wait 30 seconds
        print(f"✅ Logged odds at {collection_time}, waiting {seconds_between_requests} seconds...")
        time.sleep(seconds_between_requests)





 

 














# MAIN:
#   When running this file, first adjust the target time to be the time when you want your program to stop running,
#   typically when the game finishes.
#   Next, adjust the fixture_id to be the fixture_id for your game of interest, as recorded on OpticOdds API
# Output:
#   .csv file --> columns titled market_id, team_id, price, and timestamp. The file is saved in the data folder
#                 and is given the same name as the fixture_id parameter. 


# Define the target time (10 AM PST, May 21, 2025)
def main():
    # save API key:
    API_Key = "3d23e92b-6924-4ca7-a68a-5ccef6dc29bf"  # this is a one week trial key
    
    # CONFIG
    fixture_id = "2025052256402ED0"
    sportsbooks = ["bet365", "1xbet", "draftkings"]  # Add as many as you want
    target_time = datetime(2025, 5, 22, 11, 20, 0)  # 11:20 AM PST
    interval = 30
    
    '''
    record_odds_data_for_game(fixture_id, program_end_time=target_time, 
                              seconds_between_requests=interval, sportsbooks=sportsbooks)
    '''
    
    



if __name__ == "__main__":
    main()  
    


# we want to get historical data on first innings runs scored and moneyline (as well as live data) 
# "market_id": "1st_inning_total_runs"
# fixture ID for CSK vs RR game on 2025-05-20T14:00:00Z:  20250520BA6B20DC
# fixture ID for GT vs DC game on 2025-05-18T14:00:00Z:   20250518C03F595A
# fixture ID for MI vs DC game on 2025-05-21T14:00:00Z:   2025052186F36D55
# fixture ID for GT vs LSG game on 2025-05-22T14:00:00Z:  2025052256402ED0

