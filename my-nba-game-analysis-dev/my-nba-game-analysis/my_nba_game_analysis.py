import csv
import pandas as pd
import re

# Define regular expressions to match the desired patterns
FG_pattern = r"(\w+\.?\s\w+) makes 2-pt"
FGA_pattern = r"(\w+\.?\s\w+) misses 2-pt"
threeP_pattern = r"(\w+\.?\s\w+) makes 3-pt"
threePA_pattern = r"(\w+\.?\s\w+) misses 3-pt"
FT_pattern = r"(\w+\.?\s\w+) makes free throw"
FTA_pattern = r"(\w+\.?\s\w+) misses free throw"
ORB_pattern = r"Offensive rebound by (\w+\.?\s\w+)"
DRB_pattern = r"Defensive rebound by (\w+\.?\s\w+)"
AST_pattern = r"assist by (\w+\.?\s\w+)"
STL_pattern = r"steal by (\w+\.?\s\w+)"
BLK_pattern = r"block by (\w+\.?\s\w+)"
TOV_pattern = r"Turnover by (\w+\.?\s\w+)"
PF_pattern = r"Personal foul by (\w+\.?\s\w+)"
MCPFT_pattern = r"(\w+\.?\s\w+) makes clear path free throw"
MICPFT_pattern = r"(\w+\.?\s\w+) misses clear path free throw"

    
def load_data(filename):
    # Define column names for DataFrame
    columns = ["PERIOD", "REMAINING_SEC", "RELEVANT_TEAM", "AWAY_TEAM", "HOME_TEAM", "AWAY_SCORE", "HOME_SCORE", "DESCRIPTION"]
    df = pd.read_csv(filename, delimiter="|", header=None, names=columns)
    return df

# Function to analyse NBA game data and create a dictionary of player statistics
def analyse_nba_game(play_by_play_moves):
    # Create a dictionary to hold home team and away team data
    out_dict = {
         "home_team": {
              "name": play_by_play_moves.loc[0, "HOME_TEAM"],
              "players_data": {}
                 },
          "away_team": {
              "name": play_by_play_moves.loc[0, "AWAY_TEAM"],
              "players_data": {}
          }
     }

    player_data = {
      "FG": 0,
      "FGA": 0,
      "FG%": 0.0,
      "3P": 0,
      "3PM": 0,
      "3PA": 0,
      "3P%": 0.0,
      "2P": 0,
      "2PM": 0,
      "FT": 0,
      "FTM": 0,
      "FTA": 0,
      "FT%": 0.0,
      "ORB": 0,
      "DRB": 0,
      "TRB": 0,
      "AST": 0,
      "STL": 0,
      "BLK": 0,
      "TOV": 0,
      "PF": 0,
      "PTS": 0,
      "MCPFT": 0,
      "MICPFT": 0
}
    # Iterate through each row in the DataFrame
    for _, row in play_by_play_moves.iterrows():
        relevant_team = "home_team" if row["RELEVANT_TEAM"] == out_dict["home_team"]["name"] else "away_team"
        description = row["DESCRIPTION"]
        split_description = description.split(". ")
        if len(split_description) > 1:
            patterns = [
              {"text":FG_pattern, "key": "2P"}, {"text": FGA_pattern, "key": "2PM"}, 
              {"text": threeP_pattern, "key": "3P"}, {"text": threePA_pattern, "key": "3PM"}, 
              {"text": FT_pattern, "key": "FT"}, {"text": FTA_pattern, "key": "FTM"}, 
              {"text": ORB_pattern, "key": "ORB"}, {"text": DRB_pattern, "key": "DRB"}, 
              {"text": AST_pattern, "key": "AST"}, {"text": STL_pattern, "key": "STL"}, 
              {"text": BLK_pattern, "key": "BLK"}, {"text": TOV_pattern, "key": "TOV"}, 
              {"text": PF_pattern, "key": "PF"}, {"text": MCPFT_pattern, "key": "MCPFT"},
              {"text": MICPFT_pattern, "key": "MICPFT"}
            ]
            for pattern in patterns:
                match = re.search(pattern.get('text'), description)
                if match:
                    player_name = match.group(1)
                    
                    if player_name not in out_dict[relevant_team]["players_data"]:
                        out_dict[relevant_team]["players_data"][player_name] = player_data.copy()
                    out_dict[relevant_team]["players_data"][player_name][pattern.get('key')] += 1
          
    for team_name, team in out_dict.items():
      for player_name, player in team["players_data"].items():
        player["FG"] = player["3P"] + player["2P"]
        player["FGA"] = player["3P"] + player["2P"] + player["3PM"] + player["2PM"]
        player["3PA"] = player["3P"] + player["3PM"]
        player["FT"] = player["FT"] * 1 + player["MCPFT"] + player["MICPFT"]
        player["FTA"] = player["FT"] + player["FTM"]
        # Calculate field goal percentage
        if player.get('FGA', 0) > 0:
          player['FG%'] = round(player.get('FG', 0) / player['FGA'], 3)
        # Calculate 3-point percentage
        if player.get("3PA") > 0:
          player['3P%'] = round(player.get('3P', 0) / player['3PA'], 3)
        # Calculate free throw percentage
        if player.get("FTA") > 0:
          player['FT%'] = round(player.get('FT', 0) / player['FTA'], 3)
        # Calculate total points scored
        player['PTS'] = player.get('3P') * 3 + player.get("2P") * 2 + player.get('FT')
        # Calculate total rebounds
        player['TRB'] = player.get('ORB') + player.get('DRB')
        
    for team_name, team in out_dict.items():
      for player_name, player in team["players_data"].items():
        del player["MCPFT"]
        del player["MICPFT"]

    return out_dict

def print_nba_game_stats(team_dict):
  # Header
  print("Players\tFG\tFGA\tFG%\t3P\t3PA\t3P%\tFT\tFTA\tFT%\tORB\tDRB\tTRB\tAST\tSTL\tBLK\tTOV\tPF\tPTS")
  total_stats = {}
  for team in team_dict.items():
    for player, player_data in team[1]['players_data'].items():
        print(f'{player}\t{player_data["FG"]}\t{player_data["FGA"]}\t{player_data["FG%"]}\t{player_data["3P"]}\t{player_data["3PA"]}\t{player_data["3P%"]}\t{player_data["FT"]}\t{player_data["FTA"]}\t{player_data["FT%"]}\t{player_data["ORB"]}\t{player_data["DRB"]}\t{player_data["TRB"]}\t{player_data["AST"]}\t{player_data["STL"]}\t{player_data["BLK"]}\t{player_data["TOV"]}\t{player_data["PF"]}\t{player_data["PTS"]}')
        for stat_name, stat_value in player_data.items():
          if stat_name not in total_stats:
            total_stats[stat_name] = stat_value
          else:
            total_stats[stat_name] += stat_value

  # Print out the Total row
  print(f'Team Total\t{total_stats["FG"]}\t{total_stats["FGA"]}\t{total_stats["FG%"]}\t{total_stats["3P"]}\t{total_stats["3PA"]}\t{total_stats["3P%"]}\t{total_stats["FT"]}\t{total_stats["FTA"]}\t{total_stats["FT%"]}\t{total_stats["ORB"]}\t{total_stats["DRB"]}\t{total_stats["TRB"]}\t{total_stats["AST"]}\t{total_stats["STL"]}\t{total_stats["BLK"]}\t{total_stats["TOV"]}\t{total_stats["PF"]}\t{total_stats["PTS"]}')
            
def _main():
    play_by_play_moves = load_data("nba_game_warriors_thunder_20181016.txt")
    team_dict = analyse_nba_game(play_by_play_moves)
    
    
    #for index, row in play_by_play_moves.iterrows():
        #print("{}|{}|{}|{}|{}|{}|{}|{}".format(
         #   row["PERIOD"], 
         #   row["REMAINING_SEC"], 
         #   row["RELEVANT_TEAM"], 
         #   row["AWAY_TEAM"], 
         #   row["HOME_TEAM"], 
         #   row["AWAY_SCORE"], 
         #   row["HOME_SCORE"], 
         #   row["DESCRIPTION"]
        #))

    print_nba_game_stats(team_dict)

_main()