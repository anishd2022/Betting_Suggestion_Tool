# import libraries
import requests  # For making HTTP requests
import json  # For handling JSON responses
import time
import pandas as pd
from datetime import datetime
import pytz
import os


# save API key:
API_Key = "752f772f-7a59-4f14-b066-d1921a4f2c64"  # this is a one week trial key


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
def get_live_odds_for_specific_game(game_ID, sportsbook, odds_format="AMERICAN", market="moneyline"):
    url = f"https://api.opticodds.com/api/v3/fixtures/odds?key={API_Key}&fixture_id={game_ID}&odds_format={odds_format}&sportsbook={sportsbook}&market={market}"
    return make_request_and_return_response(url)

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






# Define the target time (10 AM PST, Mar 20, 2025)
target_time = datetime(2025, 3, 20, 10, 0, 0, 0)  # 10 AM PST
pst = pytz.timezone('US/Pacific')
target_time = pst.localize(target_time)

fixture_id = "20250309E1880B18"


while datetime.now(pytz.timezone('US/Pacific')) < target_time:
    # Save inside 'Data' folder  
    file_path = os.path.join("Data", f"{fixture_id}.csv")
    
    with open(file_path, "a") as file:
        data = get_live_odds_for_specific_game(game_ID=fixture_id, sportsbook="1xbet")
        if data is None or data == 'null' or "data" not in data or not data["data"]:
            print("No data received. Stopping the loop...")
            break  
        # Extract the odds data
        odds_data = data["data"][0]["odds"]
        
        # Create a DataFrame with selected fields
        df = pd.DataFrame([
            {
                "market_id": odd["market_id"],
                "team_id": odd["team_id"],
                "price": odd["price"],
                "timestamp": float(odd["timestamp"])
            }
            for odd in odds_data
        ])
        print(df)
        
        # Append the DataFrame to a CSV file without writing the header again
        df.to_csv(file, index=False, header=file.tell() == 0)
        
        time.sleep(120)  # Pause execution for 2 minutes (120 seconds)
        print("End after 2 minutes")
 

 
      