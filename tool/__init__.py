""""
TODO: Add description
"""
from collections import OrderedDict
from json import load

import pandas


def analyze(csv_file: str, json_file: str, output_location: str):
  titles, json_data = extract_data(csv_file, json_file)

  target_file_location = f'{output_location}/analyzed_data.csv'

  data = {classifier: compress_matches(scan_titles(titles, classifier, json_data)) for classifier in json_data.keys()}

  sorted_data = {title: OrderedDict() for title in titles}
  for category in json_data.keys():
    for title in titles:
      sorted_data[title][category] = data[category][title]

  analyzed_data = '\n'.join(
    [','.join(['titles'] + titles)] +
    [','.join([title] + list(attributes.values())) for title, attributes in sorted_data.items()]
  )

  with open(target_file_location, 'w+') as target_file:
    target_file.write(analyzed_data)


def compress_matches(match_data: dict) -> dict:
  return {key: '|'.join([str(value) for value in value['values']]) for key, value in match_data.items()}


def extract_data(csv_file: str, json_file: str) -> (list, dict):
  with open(csv_file, 'r') as csv, open(json_file, 'r') as json:
    csv_data = pandas.read_csv(csv)
    json_data = load(json)

  return list(csv_data['title']), json_data


def scan_titles(titles: list, category: str, json: dict) -> dict:
  category_data: dict = json[category]

  matched_data = {}
  for title in titles:
    matched_data[title] = {
      'matches': [],
      'values': []
    }

    for term, key in category_data.items():
      if f' {term} ' in title:
        matched_data[title]['matches'].append(term)
        matched_data[title]['values'].append(key)

  return matched_data
