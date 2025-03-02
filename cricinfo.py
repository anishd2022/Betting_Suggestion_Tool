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




m = Match('1466423')
data = m.innings_list

# Pretty-printing the JSON data
print(json.dumps(data, indent=4))