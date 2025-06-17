# import libraries
import requests  # For making HTTP requests
import json  # For handling JSON responses
import time
import pandas as pd
from datetime import datetime
import pytz
import os
from urllib.parse import urlencode
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import csv
from dotenv import load_dotenv


# save API key:
API_Key = "3d23e92b-6924-4ca7-a68a-5ccef6dc29bf"  # this is a one week trial key


# function to make get requests and return JSON response:
def make_request_and_return_response(url):
    try:
        response = requests.get(url, timeout=10)  # Safely timeout after 10 seconds
        response.raise_for_status()  # Raises exception for bad responses (e.g., 404)
        return response.json()
    except requests.exceptions.Timeout:
        print(f"⚠️ Timeout occurred for URL: {url}")
        return None  # So your main loop knows to skip this iteration
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return None


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


def get_live_score(url):
    # Set up headless Chrome
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

    # Initialize the driver
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)

    # Wait for JavaScript to load content (optional)
    # time.sleep(5)

    # Grab the page source and parse it
    soup = BeautifulSoup(driver.page_source, "html.parser")
    # print(soup.prettify())
    
    # Get ball number
    ball_span = soup.find("span", class_="ds-text-tight-s ds-font-regular ds-mb-1 lg:ds-mb-0 lg:ds-mr-3 ds-block ds-text-center ds-text-typo-mid1")
    ball_number = ball_span.get_text(strip=True) if ball_span else "N/A"
    # Get current timestamp in PST
    pst = pytz.timezone("America/Los_Angeles")
    timestamp = datetime.now(pst).strftime("%Y-%m-%d %H:%M:%S")

    # Get team names
    team_names = []
    team_spans = soup.select("span.ds-text-tight-l.ds-font-bold.ds-text-typo.ds-block.ds-truncate")
    for span in team_spans:
        team_names.append(span.get_text(strip=True))
    team_name_1 = team_names[0]
    team_name_2 = team_names[1]

    # get team scores:
    score_divs = soup.find_all("div", class_="ds-text-compact-m ds-text-typo ds-text-right ds-whitespace-nowrap")
    scores = []
    for div in score_divs:
        strong_tag = div.find("strong")
        if strong_tag:
            score_text = strong_tag.get_text(strip=True)
            scores.append(score_text)
    runs_wickets = [score.split("/") if "/" in score else (score, 10) for score in scores]
    team1_runs, team1_wkts = runs_wickets[0]
    if len(runs_wickets) > 1:
        team2_runs, team2_wkts = runs_wickets[1]
    else:
        team2_runs, team2_wkts = "N/A", "N/A"
    
    # Combine into array and print
    result = [timestamp, ball_number, 
              team_name_1, team1_runs, team1_wkts, 
              team_name_2, team2_runs, team2_wkts]

    # end session
    driver.quit()
    
    # return result:
    return(result)



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
                team_name = odd.get("selection")
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
                    "team_name": team_name,
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



def record_odds_data_and_live_score_for_game(cricinfo_url, optic_odds_game_ID, program_end_time, 
                                             seconds_between_requests, sportsbooks):
    # config:
    fixture_id = optic_odds_game_ID
    target_time = pytz.timezone('US/Pacific').localize(program_end_time)
    # Output CSV file
    csv_filename = f"Data/{optic_odds_game_ID}cricinfo.csv"
    headers = [
        "timestamp", "ball_number", 
        "team_1_name", "team_1_runs", "team_1_wickets", 
        "team_2_name", "team_2_runs", "team_2_wickets"
    ]
    
    # Create and write headers if file is new
    try:
        with open(csv_filename, mode="x", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(headers)
    except FileExistsError:
        pass  # File already exists; skip writing headers
    
    # FILE SETUP
    os.makedirs("Data", exist_ok=True)
    file_path = os.path.join("Data", f"{fixture_id}.csv")
    
    # LOOP
    while datetime.now(pytz.timezone('US/Pacific')) < target_time:
        collection_time = datetime.now(pytz.timezone("US/Pacific")).strftime("%Y-%m-%d %H:%M:%S")
        all_odds_rows = []
        
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
                team_name = odd.get("selection")
                price = odd.get("price")
                points = odd.get("points") if market_id != "moneyline" else ""
                
                # Determine over_under
                if name == "moneyline":
                    over_under = "over"
                elif odd.get("selection_line") in ["over", "under"]:
                    over_under = odd["selection_line"]
                else:
                    over_under = ""
                    
                all_odds_rows.append({
                    "timestamp": collection_time,
                    "sportsbook": book,
                    "market_id": market_id,
                    "team_id": team_id,
                    "team_name": team_name,
                    "over_under": over_under,
                    "price": price,
                    "points": points
                })
    
        # Save to CSV
        if all_odds_rows:
            df = pd.DataFrame(all_odds_rows)
            print(df)

            file_exists = os.path.isfile(file_path)
            df.to_csv(file_path, mode="a", index=False, header=not file_exists)
        
        try:
            cricinfo_row = get_live_score(cricinfo_url)
            with open(csv_filename, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(cricinfo_row)
            print(f"🟢 Row added at {cricinfo_row[0]}")
        except Exception as e:
            print(f"❌ Error during fetch: {e}")
        
        # Wait 30 seconds
        print(f"✅ Logged odds at {collection_time}, waiting {seconds_between_requests} seconds...")
        time.sleep(seconds_between_requests)
    


def join_game_tables(game_csv_path, cricinfo_csv_path):
    # Read both CSVs with timestamps parsed as datetime
    game_df = pd.read_csv(game_csv_path, parse_dates=["timestamp"])
    cricinfo_df = pd.read_csv(cricinfo_csv_path, parse_dates=["timestamp"])

    # Sort by timestamp (required for merge_asof)
    game_df.sort_values("timestamp", inplace=True)
    cricinfo_df.sort_values("timestamp", inplace=True)

    # Perform as-of merge: join on nearest earlier or equal timestamp
    merged_df = pd.merge_asof(
        game_df,
        cricinfo_df,
        on="timestamp",
        direction="backward"
    )

    # Drop rows that didn't match a cricinfo row (i.e., no prior timestamp found)
    merged_df = merged_df.dropna(subset=["ball_number"])

    # Construct the output file name with 'Final.csv' suffix
    base_filename = os.path.basename(game_csv_path).replace(".csv", "Final.csv")
    output_path = os.path.join("Data", base_filename)

    # Save to new CSV file
    merged_df.to_csv(output_path, index=False)

    print(f"✅ Final joined file written to {output_path}")
    return merged_df


 

 

























def main():
    load_dotenv()  # load variables from .env into environment
    
    # save API key:
    API_Key = os.getenv("API_KEY")  # this is a one week trial key
    
    # CONFIG
    fixture_id = "20250529A0F6AFE9"
    sportsbooks = ["bet365", "1xbet", "draftkings"]  # Add as many as you want
    target_time = datetime(2025, 5, 29, 11, 30, 0)  # 11:30 AM PST
    interval = 20
    cricinfo_url = "https://www.espncricinfo.com/series/ipl-2025-1449924/punjab-kings-vs-royal-challengers-bengaluru-qualifier-1-1473508/ball-by-ball-commentary"
    odds_filepath = f"Data/{fixture_id}.csv"
    game_filepath = f"Data/{fixture_id}cricinfo.csv"
    
    
    record_odds_data_and_live_score_for_game(cricinfo_url, fixture_id, target_time, 
                                             interval, sportsbooks)
    
    join_game_tables(odds_filepath, game_filepath)



if __name__ == "__main__":
    main()  
    


# we want to get historical data on first innings runs scored and moneyline (as well as live data) 
# "market_id": "1st_inning_total_runs"
# fixture ID for CSK vs RR game on 2025-05-20T14:00:00Z:  20250520BA6B20DC
# fixture ID for GT vs DC game on 2025-05-18T14:00:00Z:   20250518C03F595A
# fixture ID for MI vs DC game on 2025-05-21T14:00:00Z:   2025052186F36D55
# fixture ID for GT vs LSG game on 2025-05-22T14:00:00Z:  2025052256402ED0
# fixture ID for RCB vs SRH game on 2025-05-23T14:00:00Z: 20250523A8163F7D  (very little data collected for this game)
# fixture ID for PBKS vs DC game on 2025-05-24T14:00:00Z: 20250524DBD36DBB  
# fixture ID for CSK vs GT game on 2025-05-25T10:00:00Z:  20250525E889FEB3  (data until 12.1 overs of first innings)
# fixture ID for LSG vs RCB game on 2025-05-27T14:00:00Z: 202505278A99102C  (only first innings data is accurate)
# fixture ID for PBKS vs RCB game on 2025-05-29T14:00:00Z: 20250529A0F6AFE9  (most likely didn't run this because I didn't want wifi to disconnect before my meeting w/ Vishal and Venkat)



