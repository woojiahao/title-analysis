import json
from collections import OrderedDict

import pandas
from pandas import DataFrame

from click_utility import click_log, LOG_WARNING


class Analyser:
  def __init__(self, base_path: str, category: str, json_path: str, csv_path: str, out_path: str, filename: str,
               accuracies: list, mismatches: bool):
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

    available_classifiers = list(self.__original_data__.columns.values)
    available_classifiers.remove('title')
    available_classifiers.remove('image_path')

    if 'all' in self.__accuracies__:
      click_log(title='Accuracies', description='all was found, displaying accuracies for all classifiers')
      self.__accuracies__ = [i for i in self.__classifiers__]

    to_remove = []
    for accuracy in self.__accuracies__:
      if accuracy not in available_classifiers:
        click_log(
          LOG_WARNING,
          'Accuracy issue',
          f'Accuracy found ({accuracy}) that isn\'t within available classifier set, removing accuracy'
        )
        to_remove.append(accuracy)

    for remove in to_remove:
      self.__accuracies__.remove(remove)

    self.__analysed_data__ = None

  def analyse(self):
    self.__analysing_status__('Beginning Analysis')
    self.__analyse_file__()
    if len(self.__accuracies__) != 0:
      self.__analysing_status__('Calculating Accuracies')
      calculated_accuracies = []
      for accuracy in self.__accuracies__:
        mismatch, calculated_accuracy = self.__calculate_accuracy__(accuracy)
        if self.__mismatches__:
          self.__analysing_status__('Creating mismatch file')
          mismatch_file_path = f'{self.__out_path__}{accuracy}_mismatches.json'
          with open(mismatch_file_path, 'w+') as mismatch_file:
            json.dump(mismatch, mismatch_file)
        calculated_accuracies.append(calculated_accuracy)

      self.__analysing_status__('Accuracy calculated, results below')
      print('|Attribute|Counted|Not Counted|Total|Multi-values|Accuracy|')
      print('|---|---|---|---|---|---|')
      print('\n'.join(calculated_accuracies))

  def __analysing_status__(self, message: str):
    click_log(title=self.__ANALYSING_TITLE__, description=message)

  def __extract_data__(self, csv_file: str, json_file: str) -> (DataFrame, dict, dict):
    with open(csv_file, 'r') as csv, open(json_file, 'r') as json_file:
      csv_data = pandas.read_csv(csv)
      json_data = json.load(json_file)

    merged = {
      item_id: {
        'title': title,
        'image_path': image_path
      }
      for item_id, title, image_path
      in zip(list(csv_data['itemid']), list(csv_data['title']), list(csv_data['image_path']))
    }

    self.__analysing_status__(f'CSV shape -> {csv_data.shape}')
    self.__analysing_status__(f'Classifiers -> {list(json_data.keys())}')

    csv_data = csv_data.set_index('itemid')

    return csv_data, merged, json_data

  @staticmethod
  def __compress_matches__(match_data: dict) -> dict:
    return {
      key: '|'.join([str(value) for value in value['values']])
      for key, value in match_data.items()
    }

  def __scan_titles__(self, item_ids: list, titles: list, category: str, json_data: dict) -> dict:
    self.__analysing_status__(f'Scanning titles for {category}')
    category_data = json_data[category]

    matched_data = {
      item_id: {
        'matches': [],
        'values': []
      } for item_id in item_ids
    }
    for item_id, title in zip(item_ids, titles):
      for term, key in category_data.items():
        term_to_search = f' {term} '

        is_matching_term = term_to_search in title and term_to_search not in matched_data[item_id]['matches']

        if is_matching_term:
          matched_data[item_id]['matches'].append(term)
          matched_data[item_id]['values'].append(key)

    return self.__compress_matches__(matched_data)

  def __analyse_file__(self):
    self.__analysing_status__('Scanning titles')
    data = {
      classifier: self.__scan_titles__(
        self.__item_ids__,
        self.__titles__,
        classifier,
        self.__json_data__
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
      data = pandas.read_csv(self.__target_file_name__)
      self.__analysed_data__ = data.set_index('itemid')

  def __calculate_accuracy__(self, classifier: str) -> (dict, str):
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
    original_col[ORIGINAL_COL_NAME] = original_col[ORIGINAL_COL_NAME].astype(str)
    original_col[ORIGINAL_COL_NAME] = original_col[ORIGINAL_COL_NAME].replace('nan', '')
    float_cols = original_col[ORIGINAL_COL_NAME].str.endswith('.0')
    original_col[ORIGINAL_COL_NAME][float_cols] = original_col[ORIGINAL_COL_NAME][float_cols].str.replace('.0', '')

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
    accuracy = (matched_count / counted) * 100 if counted != 0 else 100

    is_not_matching = joined_col[ORIGINAL_COL_NAME] != joined_col[ANALYSED_COL_NAME]
    non_matching = joined_col[is_not_matching]

    non_matching_json = {
      data['title']: {
        ORIGINAL_COL_NAME: data[ORIGINAL_COL_NAME],
        ANALYSED_COL_NAME: data[ANALYSED_COL_NAME]
      }
      for item_id, data in non_matching.iterrows()
    }

    return non_matching_json, f'|{classifier}|{counted}|{not_counted}|{total}|{multi_value_count}|{accuracy}%|'
