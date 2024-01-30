import json


def load_riddles():
    with open('data.json', 'r', encoding='utf-8') as file:
        riddles = json.load(file)
    return riddles
