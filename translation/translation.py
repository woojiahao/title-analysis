import json
from os import makedirs
from os.path import basename, exists

from translate import Translator


def create_translation(json_file: str) -> dict:
  english_translator = Translator('en', 'ms', email='woojiahao1234@gmail.com')
  malay_translator = Translator('ms', 'en', email='woojiahao1234@gmail.com')

  print(f'Translating {json_file} ...')

  with open(json_file, 'r') as file:
    data: dict = json.load(file)

  translation = {}

  for category_name, category_values in data.items():
    print(f'Category: {category_name}')
    translation[category_name] = {}

    for category_value, category_value_index in category_values.items():
      english_translation = english_translator.translate(category_value)
      malay_translation = malay_translator.translate(category_value)

      print(f'\tEnglish translation: {english_translation} - {category_value_index}')
      print(f'\tMalay translation: {malay_translation} - {category_value_index}')

      translation[category_name][english_translation] = category_value_index
      translation[category_name][malay_translation] = category_value_index

  print('Translations completed!')

  return translation


def create_translation_file(json_file: str, output_location: str) -> str:
  print('Creating translations file...')

  json_file_name = basename(json_file[:json_file.rindex(".")])
  translated_file_name = f'{json_file_name}_translated.json'

  translation_file_location = f'{output_location}\\{translated_file_name}'

  if not exists(output_location):
    makedirs(output_location)

  translated_json: dict = create_translation(json_file)
  with open(translation_file_location, 'w+') as translated_json_file:
    json.dump(translated_json, translated_json_file)

  print('Translation file created...')
  print(f'Translation file location: {translation_file_location}')

  return translation_file_location
