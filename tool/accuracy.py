import csv
from os.path import dirname
from pprint import pprint


def get_differences(analyzed_file: str, original_file: str, column_name: str):
  with open(analyzed_file) as analyzed, \
      open(original_file) as original, \
      open(f'{dirname(analyzed_file)}\\mismatches\\{column_name}_mismatches.json', 'w+') as mismatch_file:

    analyzed_csv = csv.DictReader(analyzed)
    original_csv = csv.DictReader(original)

    analyzed_col = {
      row['itemid']: {
        'title': row['title'],
        'column': row[column_name]
      }
      for row in analyzed_csv
    }
    original_col = {
      row['itemid']: {
        'title': row['title'],
        'column': row[column_name]
      }
      for row in original_csv
    }

    original_col_name = f'Original {column_name}'
    analyzed_col_name = f'Analyzed {column_name}'

    difference_col = {}
    bundle = zip(
      analyzed_col.keys(),
      [r['column'] for r in original_col.values()],
      [r['column'] for r in analyzed_col.values()]
    )
    for item_id, original_value, analyzed_value in bundle:
      difference_col[item_id] = {
        original_col_name: original_value,
        analyzed_col_name: analyzed_value
      }

    difference_count = 0
    checked_count = 0
    mismatches = []
    multi_values_count = 0
    for title, item_id, attribute in zip(
        [r['title'] for r in original_col.values()],
        difference_col.keys(),
        difference_col.values()
    ):
      original_col_data: str = attribute[original_col_name]
      analyzed_col_data: str = attribute[analyzed_col_name]
      if analyzed_col_data != '':
        checked_count += 1

        is_decimal = original_col_data.rfind('.')
        if is_decimal != -1:
          analyzed_col_data += '.0'

        if analyzed_col_data.rfind('|') != -1:
          multi_values_count += 1

        if original_col_data != analyzed_col_data:
          mismatch = f'"{title}": {attribute}'.replace('\'', '"')
          mismatches.append(mismatch)
          difference_count += 1

    new_line = ",\n"
    mismatch_file.write(f'{"{"}{new_line.join(mismatches)}{"}"}')
    total_data_size = len(analyzed_col)
    accuracy = ((total_data_size - difference_count) / total_data_size) * 100

    print(f'|{column_name}|{checked_count}|{total_data_size - checked_count}|{total_data_size}|{multi_values_count}|{accuracy}%|')

def get_differences_loop(analyzed_file: str, original_file: str, column_names: list):
  for column_name in column_names:
    get_differences(analyzed_file, original_file, column_name)

def generate_accuracy(differences_file: str, column_name: str):
  with open(differences_file) as file:
    differences = csv.DictReader(file)
    difference_count = 0
    for row in differences:
      if row[f'Analyzed {column_name}'] != '' and row[f'Original {column_name}'] != row[f'Analyzed {column_name}']:
        difference_count += 1

    total_data_size = differences.line_num
    accuracy = ((total_data_size - difference_count) / total_data_size) * 100
    return accuracy
