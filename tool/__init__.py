""""
TODO: Add description
"""
from collections import OrderedDict
from json import load
from pprint import pprint

import pandas


def extract_data(csv_file: str, json_file: str) -> (dict, dict):
  with open(csv_file, 'r') as csv, open(json_file, 'r') as json:
    csv_data = pandas.read_csv(csv)
    json_data = load(json)

  merged = {
    item_id: {
      'title': title,
      'image_path': image_path
    }
    for item_id, title, image_path
    in zip(list(csv_data['itemid']), list(csv_data['title']), list(csv_data['image_path']))
  }

  return merged, json_data


def compress_matches(match_data: dict) -> dict:
  return {
    key: '|'.join([str(value) for value in value['values']])
    for key, value in match_data.items()
  }


def scan_titles(item_ids: list, titles: list, category: str, json: dict) -> dict:
  category_data: dict = json[category]

  matched_data = {
    item_id: {
      'matches': [],
      'values': []
    } for item_id in item_ids
  }
  for item_id, title in zip(item_ids, titles):
    for term, key in category_data.items():
      term_to_search = f' {term} '

      if term_to_search in title and term_to_search not in matched_data[item_id]['matches']:
        matched_data[item_id]['matches'].append(term)
        matched_data[item_id]['values'].append(key)

  return matched_data


def analyze(csv_file: str, json_file: str, output_location: str):
  merged_data, json_data = extract_data(csv_file, json_file)
  item_ids = list(merged_data.keys())
  titles = [bundle['title'] for bundle in merged_data.values()]
  image_paths = [bundle['image_path'] for bundle in merged_data.values()]
  classifiers = json_data.keys()

  target_file_location = f'{output_location}/analyzed_data.csv'

  # Retrieving the analyzed weights of the titles
  print("Weighting data")
  data = {
    classifier: compress_matches(scan_titles(item_ids, titles, classifier, json_data))
    for classifier in classifiers
  }

  print("Sorting data")
  sorted_data = {
    item_id: OrderedDict()
    for item_id in item_ids
  }
  for classifier in classifiers:
    for item_id, bundle in merged_data.items():
      sorted_data[item_id]['itemid'] = item_id
      sorted_data[item_id]['title'] = bundle['title']
      sorted_data[item_id]['image_path'] = bundle['image_path']
      sorted_data[item_id][classifier] = data[classifier][item_id]

  print("Creating CSV")
  analyzed_data = '\n'.join(
    [','.join(['itemid', 'title', 'image_path'] + list(classifiers))] +
    [','.join([str(attribute) for attribute in attributes.values()]) for attributes in sorted_data.values()]
  )

  with open(target_file_location, 'w+') as target_file:
    target_file.write(analyzed_data)
