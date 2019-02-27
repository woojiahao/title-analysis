""""
TODO: Add description
"""

import json

from tool.translation import create_translation, create_translation_file


def analyze(csv_file: str, json_file: str, output_location: str):
  print(f'CSV File: {csv_file}')
  print(f'JSON File: {json_file}')
  print(f'Output Location: {output_location}')

  translation_json_file = create_translation_file(json_file, output_location)
