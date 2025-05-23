# import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pytz
import csv


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
    runs_wickets = [score.split("/") if "/" in score else ("N/A", "N/A") for score in scores]
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


def track_live_score(url, time_between_requests, end_time):
    # Output CSV file
    csv_filename = "Data/LiveScoreTesting.csv"
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

    # Set PST timezone
    pst = pytz.timezone("America/Los_Angeles")

    while True:
        current_time = datetime.now(pst)
        if current_time >= end_time:
            print("✅ Reached end time. Stopping...")
            break

        try:
            row = get_live_score(url)
            with open(csv_filename, mode="a", newline="") as file:
                writer = csv.writer(file)
                writer.writerow(row)
            print(f"🟢 Row added at {row[0]}")
        except Exception as e:
            print(f"❌ Error during fetch: {e}")

        time.sleep(time_between_requests)









def main():
    # initialize url:
    url = "https://www.espncricinfo.com/series/ipl-2025-1449924/royal-challengers-bengaluru-vs-sunrisers-hyderabad-65th-match-1473503/ball-by-ball-commentary"
    interval_time = 30
    pst = pytz.timezone("America/Los_Angeles")
    end_time = pst.localize(datetime(2025, 5, 23, 11, 20, 0))   # 11:20am PST

    '''
    live_score = get_live_score(url)
    print(live_score)
    '''
    
    track_live_score(url, interval_time, end_time)

if __name__ == "__main__":
    main()
