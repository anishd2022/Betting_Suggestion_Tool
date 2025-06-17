# Betting Suggestion Tool

**Goal**: Collect cricket odds data from sportsbooks, specifically moneylines and over under on total runs scored in an inning, and compare it with a prediction tool to validate the accuracy of the prediction tool and see if it beats the accuracy of the sportsbooks odds. If it does, the final goal would be to develop a suggestion tool, similar to [Oddsjam](https://oddsjam.com/), specifically for cricket, which would help bettors make long term profits.  

**Note**: the current program only collects live game data and live game odds, the prediction tool is yet to be integrated. Once it is, we can compare its predictions to the data we have been collecting.

- Live game data is web scraped from [CricInfo](https://www.espncricinfo.com/)
- Live odds data is collected through [OpticOdds API](https://developer.opticodds.com/)

- `MoneylineTimeSeriesReport.pdf` gives a quick overview of my initial exploratory data analysis and plan for this project

## Setup:

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/anishd2022/CricketBetting.git
    cd bisv-senior-project/CricketBetting
    ```
2.  **Set up a virtual environment** (recommended):
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: .\venv\Scripts\activate
    ```
3.  **Install Python dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Optic Odds API Key:

- To run the program successfully by gathering real-time odds data, you will need access to an OpticOdds API trial key, and you will have to [contact](https://opticodds.com/contact) them first in order to recieve one.
- Once you have this trial key, set up your .env file accordingly
    ```
    API_KEY={your_api_key}
    ```

## Code Files: 

Run `getrequests.py` with appropriate parameters during a match to produce three .csv files for the current game_id, which will track verious market odds and match status at regular intervals over the course of the game. The files will be stored in the `Data/` folder. 

Run `winprobability.py` with appropriate parameters for the `get_timeseries_win_graph_overlay()` function to generate a graph of win probability over time for CricInfo and 1xbet sportsbook for the same game. 
  
## Data Files:

- The data files are named with the convention {game_id}.csv (the game_id comes from OpticOdds). Files with `{game_id}.csv` give various market odds (ex: moneyline, team_total, first_xx_overs_team_total) for sportsbooks like Fanduel, 1xbet, bet365, etc.
- Files with `{game_id}cricinfo.csv` give live scores on regular time intervals throughout the course of that game
- Files with `{game_id}final.csv` combines the `{game_id}.csv` and `{game_id}cricinfo.csv` table by joining the tables on timestamp. This is the final file which would eventually be used to compare with the prediction tool.

- **Note**: I have included a sample of the data for a given game in `Data_Samples/`



