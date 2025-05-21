import sys
import os
import json

# Get the path to the python-espncricinfo directory
module_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "python-espncricinfo"))

# Add it to sys.path if it's not already there
if module_path not in sys.path:
    sys.path.insert(0, module_path)

# import necessary libraries
from espncricinfo.match import Match
from espncricinfo.summary import Summary
from espncricinfo.player import Player
import requests
from getrequests import make_request_and_return_response



# this section used to work, but doesn't work anymore for some reason. 
'''
match_id = '1466426'
m = Match(match_id)
data = m.match_json

# Pretty-printing the JSON data
print(json.dumps(data, indent=4))
'''

match_id = '1466426'
json_url = f'https://www.espncricinfo.com/matches/engine/match/{match_id}.json'
print(json_url)

# pretty printing the json data:
match_data = make_request_and_return_response(json_url)
print(json.dumps(match_data, indent=4))
