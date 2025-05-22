# import libraries
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import time
from datetime import datetime
import pytz









def main():
    # initialize url:
    url = "https://www.espncricinfo.com/series/ipl-2025-1449924/gujarat-titans-vs-lucknow-super-giants-64th-match-1473502/ball-by-ball-commentary"

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
    team_span = soup.find_all("span", class_="ds-text-tight-l ds-font-bold ds-text-typo hover:ds-text-typo-primary ds-block ds-truncate")
    for span in team_span:
        team_names.append(span.get_text(strip=True))
    
    team_name_1 = team_names[0]
    team_name_2 = team_names[1]

    # Combine into array and print
    result = [timestamp, ball_number, team_name_1, team_name_2]
    print(result)
        

    
    
    '''
    over_ball_spans = soup.find_all("span", class_="ds-text-tight-s ds-font-regular ds-mb-1 lg:ds-mb-0 lg:ds-mr-3 ds-block ds-text-center ds-text-typo-mid1")

    # Extract and print the text values
    for span in over_ball_spans:
        print(span.get_text(strip=True))
    '''

    # end session
    driver.quit()

if __name__ == "__main__":
    main()
 