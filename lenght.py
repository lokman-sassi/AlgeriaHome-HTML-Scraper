import json

# Load the data from the JSON file
with open('AlgeriaHome.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Get the length of the scraped data
length = len(data)

print("Scraped items:", length)



