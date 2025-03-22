# CricketBetting

**Goal**: Collect cricket odds data from sportsbooks, specifically moneylines and total runs scored, and compare it with a prediction tool to validate the accuracy of the prediction tool and see if it beats the accuracy of the sportsbooks odds. 

## Files: 

Run `getrequests.py` with appropriate `fixture_id` and `target_time` during a match to get a .csv file with moneyline odds for both teams over the course of the game. The .csv file will be stored in the `Data` folder.

Run `winprobability.py` with appropriate parameters for the `get_timeseries_win_graph_overlay()` function to generate a graph of win probability over time for CricInfo and 1xbet sportsbook for the same game. 

## Graphs:

Graphs are stored in the `Images` folder

