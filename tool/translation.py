import json
from os import makedirs
from os.path import basename, exists

# from googletrans import Translator
from translate import Translator


def create_translation(json_file: str) -> dict:
  translator = Translator('ms')

  print(f'Translating {json_file} ...')

  with open(json_file, 'r') as file:
    data: dict = json.load(file)

  print(data)

  translation = {}

  for category_name, category_values in data.items():
    translation[category_name] = {}
    for category_value, category_value_index in category_values.items():
      translated = translator.translate(category_value)
      print(translated)
      translation[category_name][category_value] = category_value_index
      translation[category_name][translated] = category_value_index

  print(translation)

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
