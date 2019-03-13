import json


def add_redundant_json(original_json_path: str):
  with open(original_json_path, 'r') as json_file:
    json_data = json.load(json_file)

  for category, values in json_data.items():
    value_highest = max([value for value in values.values()]) + 1
    values['redundant'] = value_highest

  return json_data


def create_redundant_json(original_json_path: str, new_file_path: str):
  redundant_json = add_redundant_json(original_json_path)
  with open(f'{new_file_path}\\redundant.json', 'w+') as file:
    json.dump(redundant_json, file)


base_path = 'C:\\Users\\Chill\\Jia Hao\\Data Science Challenge\\updated-datasets'

# Mobile
mobile_path = f'{base_path}\\mobile'
create_redundant_json(f'{mobile_path}\\mobile.json', mobile_path)

# Beauty
beauty_path = f'{base_path}\\beauty'
create_redundant_json(f'{beauty_path}\\beauty.json', beauty_path)

# Fashion
fashion_path = f'{base_path}\\fashion'
create_redundant_json(f'{fashion_path}\\fashion.json', fashion_path)
