# import necessary libraries
import pandas as pd
import matplotlib.pyplot as plt
import pytz



# function that takes in two american odds and returns decimal probability of winning for each team:
def convert_american_to_probability(odd_1, odd_2):
    def american_to_implied_prob(odd):
        if (odd > 0):
            return 1 - (100 / (odd + 100))
        else:
            return 1 - (abs(odd) / (abs(odd) + 100))
    prob_1 = american_to_implied_prob(odd_1)
    prob_2 = american_to_implied_prob(odd_2)
    
    # normalize probabilities to sum to 1:
    total_prob = prob_1 + prob_2
    return (prob_1 / total_prob, prob_2 / total_prob)
    
    

# function that converts .csv file into pandas df
def convert_csv_to_df(filename):
    df = pd.read_csv(filename)
    return df
    

# function to remove duplicate rows from a pandas df:
def remove_duplicate_rows(data):
    return data.drop_duplicates()


def assign_correct_probabilities(df):
    df["win_probability"] = df.apply(lambda row: row["prob_team_1"] if row["team_id"] == df.iloc[0]["team_id"] else row["prob_team_2"], axis=1)
    df = df.drop(columns=["prob_team_1", "prob_team_2"])
    return df



# function to process odds data and add a win probability column in the pandas df:
def process_odds_data(filename):
    df = pd.read_csv(filename)
    df = remove_duplicate_rows(df)
    
    # Pivot table to get odds for each timestamp
    pivot_df = df.pivot(index="timestamp", columns="team_id", values="price").dropna()
    
    # Extract team IDs
    team_1, team_2 = pivot_df.columns
    
    # Compute probabilities
    probabilities = pivot_df.apply(lambda row: convert_american_to_probability(row[team_1], row[team_2]), axis=1)
    
    # Assign probabilities to new columns
    pivot_df["prob_team_1"], pivot_df["prob_team_2"] = zip(*probabilities)
    
    # Reset index to merge back with original data
    return df.merge(pivot_df[["prob_team_1", "prob_team_2"]], on="timestamp", how="left")




# function to get win probability graph:
def get_timeseries_win_graph(filename, team_id):
    df = process_odds_data(filename)
    df = assign_correct_probabilities(df)
    
    # Ensure the timestamp column is in datetime format
    df["timestamp"] = pd.to_datetime(df["timestamp"], unit="s")
    
    # Localize the timestamp to UTC (if it's not already localized)
    if df["timestamp"].dt.tz is None:
        df["timestamp"] = df["timestamp"].dt.tz_localize('UTC')

    # Convert to Pacific Time (PST/PDT)
    pacific = pytz.timezone("America/Los_Angeles")
    df["timestamp"] = df["timestamp"].dt.tz_convert(pacific)
    
    # Filter for the given team_id
    team_df = df[df["team_id"] == team_id]
    
    if team_df.empty:
        print(f"No data found for team ID {team_id}.")
        return
    
    # Plot the win probability over time
    plt.figure(figsize=(12, 6))
    plt.plot(team_df["timestamp"], team_df["win_probability"], marker="o", linestyle="-", label=f"Team {team_id}")

    plt.xlabel("Timestamp")
    plt.ylabel("Win Probability")
    plt.title(f"Win Probability Over Time for Team {team_id}")
    plt.legend()
    plt.grid()
    plt.xticks(rotation=45)
    plt.show()
    



# MAIN:
# ENGLAND team ID: 624D16F40C2863F9
# SOUTH AFRICA team ID: 2EE145593BBBB158
get_timeseries_win_graph("2025030159F80420.csv", "2EE145593BBBB158")


