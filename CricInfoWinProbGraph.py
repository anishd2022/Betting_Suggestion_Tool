import matplotlib.pyplot as plt
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


# get the CricInfo URL
url = "https://www.espncricinfo.com/series/icc-champions-trophy-2024-25-1459031/india-vs-new-zealand-final-1466428/full-scorecard"  

driver = webdriver.Chrome()
driver.get(url)

time.sleep(5)

# extract polyline data
polyline = driver.find_element(By.TAG_NAME, "polyline")  # Find the polyline element
print("FOUND POLYLINE ELEMENT!!!")
points_str = polyline.get_attribute("points")  # Extract the points attribute
print(points_str)


# Parse the data
points = np.array([list(map(float, p.split(','))) for p in points_str.split()])

# Extract x and y values
x_values = points[:, 0] / 3
y_values = points[:, 1]


# Normalize y-values (assuming max pixel height of ~200 for win probability)
y_values = 1 - (y_values / max(y_values))  # Invert and scale to range [0,1]


# Plot the graph
plt.figure(figsize=(10, 5))
plt.plot(x_values, y_values, label="CricInfo Win Probability", color="orange")
plt.xlabel("Overs")
plt.ylabel("Win Probability")
plt.title("Win Probability Graph from CricInfo")
plt.ylim(0, 1)
plt.axhline(y=0.5, color='red', linestyle='--', linewidth=2)
plt.legend()
plt.show()

