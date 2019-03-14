from collections import OrderedDict
from json import load

import pandas
from pandas import DataFrame

from click_utility import click_log, LOG_WARNING


class Analyser:
  def __init__(self, base_path: str, category: str, json_path: str, csv_path: str, out_path: str, filename: str,
               accuracies: list, mismatches: str):
    self.__base_path__ = base_path
    self.__category__ = category
    self.__json_path__ = json_path
    self.__csv_path__ = csv_path
    self.__out_path__ = out_path
    self.__accuracies__ = accuracies
    self.__mismatches__ = mismatches
    self.__target_file_name__ = filename
    self.__ANALYSING_TITLE__ = 'Analysing'

    self.__original_data__, self.__merged_data__, self.__json_data__ = \
      self.__extract_data__(
        self.__csv_path__,
        self.__json_path__
      )
    self.__item_ids__ = list(self.__merged_data__.keys())
    self.__titles__ = [bundle['title'] for bundle in self.__merged_data__.values()]
    self.__classifiers__ = self.__json_data__.keys()

    if 'all' in self.__accuracies__:
      click_log(title='Accuracies', description='all was found, displaying accuracies for all classifiers')
      self.__accuracies__ = [i for i in self.__classifiers__]

    for accuracy in self.__accuracies__:
      if accuracy not in self.__classifiers__ or accuracy not in self.__original_data__.columns.values:
        click_log(
          LOG_WARNING,
          'Accuracy issue',
          f'Accuracy found ({accuracy}) that isn\'t within available classifier set, removing accuracy'
        )
        self.__accuracies__.remove(accuracy)

    self.__analysed_data__ = None

  def analyse(self):
    self.__analysing_status__('Beginning Analysis')
    self.__analyse_file__()
    if len(self.__accuracies__) != 0:
      self.__analysing_status__('Calculating Accuracies')
      calculated_accuracies = [self.__calculate_accuracy__(accuracy) for accuracy in self.__accuracies__]
      self.__analysing_status__('Accuracy calculated, results below')
      print('|Attribute|Counted|Not Counted|Total|Multi-values|Accuracy|')
      print('|---|---|---|---|---|---|')
      print('\n'.join(calculated_accuracies))

  def __analysing_status__(self, message: str):
    click_log(title=self.__ANALYSING_TITLE__, description=message)

  @staticmethod
  def __extract_data__(csv_file: str, json_file: str) -> (DataFrame, dict, dict):
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

    csv_data = csv_data.set_index('itemid')

    return csv_data, merged, json_data

  @staticmethod
  def __compress_matches__(match_data: dict) -> dict:
    return {
      key: '|'.join([str(value) for value in value['values']])
      for key, value in match_data.items()
    }

  @staticmethod
  def __scan_titles__(item_ids: list, titles: list, category: str, json: dict) -> dict:
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

  def __analyse_file__(self):
    self.__analysing_status__('Scanning titles')
    data = {
      classifier: self.__compress_matches__(
        self.__scan_titles__(
          self.__item_ids__,
          self.__titles__,
          classifier,
          self.__json_data__
        )
      )
      for classifier in self.__classifiers__
    }

    self.__analysing_status__("Sorting data")
    sorted_data = {
      item_id: OrderedDict()
      for item_id in self.__item_ids__
    }
    for classifier in self.__classifiers__:
      for item_id, bundle in self.__merged_data__.items():
        sorted_data[item_id]['itemid'] = item_id
        sorted_data[item_id]['title'] = bundle['title']
        sorted_data[item_id]['image_path'] = bundle['image_path']
        sorted_data[item_id][classifier] = data[classifier][item_id]

    self.__analysing_status__("Creating CSV")
    analyzed_data = '\n'.join(
      [','.join(['itemid', 'title', 'image_path'] + list(self.__classifiers__))] +
      [','.join([str(attribute) for attribute in attributes.values()]) for attributes in sorted_data.values()]
    )

    with open(self.__target_file_name__, 'w+') as target_file:
      target_file.write(analyzed_data)

    with open(self.__target_file_name__, 'r') as target_file:
      self.__analysed_data__ = pandas.read_csv(target_file).set_index('itemid')

  def __calculate_accuracy__(self, classifier: str) -> str:
    self.__analysing_status__(f'Calculating accuracy of {classifier}')
    ORIGINAL_COL_NAME = f'Original {classifier}'
    ANALYSED_COL_NAME = f'Analyzed {classifier}'

    analysed_col = self.__analysed_data__[['title', classifier]] \
      .rename(columns={classifier: ANALYSED_COL_NAME}) \
      .sort_index()
    analysed_col[ANALYSED_COL_NAME] = analysed_col[ANALYSED_COL_NAME].astype(str)
    analysed_col[ANALYSED_COL_NAME] = analysed_col[ANALYSED_COL_NAME].replace('nan', '')
    float_cols = analysed_col[ANALYSED_COL_NAME].str.endswith('.0')
    analysed_col[ANALYSED_COL_NAME][float_cols] = analysed_col[ANALYSED_COL_NAME][float_cols].str.replace('.0', '')

    original_col = self.__original_data__[['title', classifier]] \
      .rename(columns={classifier: ORIGINAL_COL_NAME}) \
      .sort_index()
    original_col[ORIGINAL_COL_NAME] = original_col[ORIGINAL_COL_NAME].fillna(-1)
    original_col[ORIGINAL_COL_NAME] = original_col[ORIGINAL_COL_NAME].astype(int)
    original_col[ORIGINAL_COL_NAME] = original_col[ORIGINAL_COL_NAME].astype(str)

    joined_col = original_col.join(analysed_col[ANALYSED_COL_NAME])
    non_empty_col = joined_col[ANALYSED_COL_NAME] != ''
    joined_col = joined_col[non_empty_col]

    total = analysed_col.shape[0]
    counted = joined_col.shape[0]
    not_counted = total - counted
    multi_value_count = joined_col[joined_col[ANALYSED_COL_NAME].str.contains('\\|')].shape[0]

    is_matching = joined_col[ORIGINAL_COL_NAME] == joined_col[ANALYSED_COL_NAME]
    matched = joined_col[is_matching]
    matched_count = matched.shape[0]
    accuracy = (matched_count / counted) * 100
    return f'|{classifier}|{counted}|{not_counted}|{total}|{multi_value_count}|{accuracy}%|'

    # difference_count = 0
    # checked_count = 0
    # mismatches = []
    # multi_values_count = 0
    # for title, item_id, attribute in zip(
    #     [r['title'] for r in original_col.values()],
    #     difference_col.keys(),
    #     difference_col.values()
    # ):
    #   original_col_data: str = attribute[ORIGINAL_COL_NAME]
    #   analyzed_col_data: str = attribute[ANALYSED_COL_NAME]
    #   if analyzed_col_data != '':
    #     checked_count += 1
    #
    #     is_decimal = original_col_data.rfind('.')
    #     if is_decimal != -1:
    #       analyzed_col_data += '.0'
    #
    #     if analyzed_col_data.rfind('|') != -1:
    #       multi_values_count += 1
    #
    #     if original_col_data != analyzed_col_data:
    #       mismatch = f'"{title}": {attribute}'.replace('\'', '"')
    #       mismatches.append(mismatch)
    #       difference_count += 1
    #
    # new_line = ",\n"
    # # mismatch_file.write(f'{"{"}{new_line.join(mismatches)}{"}"}')
    # total_data_size = len(analysed_col)
    # accuracy = ((total_data_size - difference_count) / total_data_size) * 100
    #
