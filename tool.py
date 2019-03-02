from os.path import isfile, exists

import click

import tool


@click.command()
@click.option('--csv', help='.csv file to merge')
@click.option('--json', help='.json file to merge')
@click.option('--output', help='Output folder location')
def analyze(csv: str, json: str, output: str):
  if exists(output) and isfile(output):
    print(f'ERROR: Output location {output} cannot be a file')
    return

  if not isfile(csv) or not csv.endswith('.csv'):
    print(f'ERROR: csv location {csv} must point to a valid csv file')
    return

  if not isfile(json) or not json.endswith('.json'):
    print(f'ERROR: json location {json} must point to a valid json file')
    return

  print('Analyzing...')
  tool.extract_data(csv, json, output)

if __name__ == '__main__':
  analyze()
