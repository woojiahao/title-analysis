import time
from os import mkdir
from os.path import exists, isdir, isfile

import click

from click_utility import click_log, LOG_ERROR
from tool.analyser import Analyser

REASON_KEY = 'reason'


@click.command()
@click.option('--base', '-b', help='Compulsory base directory path storing all the files required')
@click.option('--category', '-ca', help='Compulsory name of category being analyzed')
@click.option('--json', '-j', help='Optional location for .json file, defaults to {base}/{category}.json')
@click.option('--csv', '-c', help='Optional location for .csv file, defaults to {base}/{category}.csv')
@click.option('--out', '-o', help='Optional output file location, defaults to {base}/out/')
@click.option('--filename', '-fn', default='analysed.csv',
              help='Optional file name for analyzed data, defaults to analysed.csv')
@click.option('--accuracy', '-a',
              help='Optional comma-separated list of columns to output the accuracy for, defaults output nothing')
@click.option('--mismatches', '-m', help='Optional path parameter to store mismatch data')
def execute(base: str, category: str, json: str, csv: str, out: str, filename: str, accuracy: str, mismatches: str):
  base = base.replace('\\', '/') if base is not None else base
  json = json.replace('\\', '/') if json is not None else json
  csv = csv.replace('\\', '/') if csv is not None else csv

  # Validate base path
  is_base_path_valid = validate_base_path(base)
  if not is_base_path_valid[STATUS_KEY]:
    click_log(LOG_ERROR, description=is_base_path_valid[REASON_KEY], is_error=True)
    return

  # Validate category
  is_category_valid = validate_category(category)
  if not is_category_valid[STATUS_KEY]:
    click_log(LOG_ERROR, description=is_category_valid[REASON_KEY], is_error=True)
    return

  # Validate json path
  json_path = f'{base}/{category}.json' if json is None else f'{base}/{json}'
  is_json_path_valid = validate_json_path(json_path)
  if not is_json_path_valid[STATUS_KEY]:
    click_log(LOG_ERROR, description=is_json_path_valid[REASON_KEY], is_error=True)
    return

  # Validate csv path
  csv_path = f'{base}/{category}.csv' if csv is None else f'{base}/{csv}'
  is_csv_path_valid = validate_csv_path(csv_path)
  if not is_csv_path_valid[STATUS_KEY]:
    click_log(LOG_ERROR, description=is_csv_path_valid[REASON_KEY], is_error=True)
    return

  # Validate out path
  if out is None:
    out_path = f'{base}/out/'
    is_out_path_valid = validate_file_path(out_path, 'Out', ('--out', '-o'), False, False, does_exist=False)
  else:
    out_path = f'{base}/{out}'
    is_out_path_valid = validate_file_path(out_path, 'Out', ('--out', '-o'), False, does_exist=True)

  if not is_out_path_valid[STATUS_KEY]:
    click_log(LOG_ERROR, description=is_out_path_valid[REASON_KEY], is_error=True)
    return

  if not exists(out_path):
    mkdir(out_path)

  # Validate filename
  analysed_file_path = f'{out_path}{filename}'
  is_filename_path_valid = validate_file_path(
    analysed_file_path,
    'Filename',
    ('--filename', '-fn'),
    False,
    False,
    'csv',
    False
  )

  if not is_filename_path_valid[STATUS_KEY]:
    click_log(LOG_ERROR, description=is_filename_path_valid[REASON_KEY], is_error=True)
    return

  # Validate accuracies
  accuracies = [] if accuracy is None else accuracy.split(',')

  # Validate mismatches
  if mismatches is not None:
    mismatches_path = f'{base}/{mismatches}'
    is_mismatches_path_valid = validate_file_path(
      mismatches_path,
      'mismatches',
      ('--mismatches', '-m'),
      False,
      does_exist=True
    )

    if not is_mismatches_path_valid[STATUS_KEY]:
      click_log(LOG_ERROR, description=is_mismatches_path_valid[REASON_KEY], is_error=True)
      return
  else:
    mismatches_path = None

  click_log(title='Base path', description=base)
  click_log(title='Category', description=category)
  click_log(title='JSON path', description=json_path)
  click_log(title='CSV path', description=csv_path)
  click_log(title='Out path', description=out_path)
  click_log(title='Analysed file path', description=analysed_file_path)
  click_log(title='Accuracies', description=str(accuracies))
  click_log(title='Mismatches path', description=mismatches_path)

  before_time = time.time()
  Analyser(base, category, json_path, csv_path, out_path, analysed_file_path, accuracies, mismatches_path).analyse()
  after_time = time.time()
  click_log(title='Time taken', description=f'{(after_time - before_time)}s')


STATUS_KEY = 'status'


# TODO: Add options for output name and redundant generation


def validate_category(category: str) -> dict:
  if category is None:
    return build_operation_result(False, 'Category must be supplied using --category or -ca')

  return build_operation_result()


def validate_file_path(
    file_path: str,
    file_path_name: str,
    supply_option: tuple = (),
    is_file: bool = True,
    is_folder: bool = True,
    ends_with: str = None,
    does_exist: bool = True
) -> dict:
  if file_path is None:
    return build_operation_result(False, f'{file_path_name} path must be supplied using {" or ".join(supply_option)}')

  if does_exist:
    if not exists(file_path):
      return build_operation_result(False,
                                    f'{file_path_name} path ({file_path}) must be an existing path in your file system')

  if is_file and not isfile(file_path):
    return build_operation_result(False,
                                  f'{file_path_name} path ({file_path}) must refer to an existing file in your file system')

  if is_folder and not isdir(file_path):
    return build_operation_result(False,
                                  f'{file_path_name} path ({file_path}) must refer to an existing folder in your file system')

  if ends_with is not None and not file_path.endswith(f'.{ends_with}'):
    return build_operation_result(False, f'{file_path} does not end with .{ends_with}')

  return build_operation_result()


def validate_json_path(json_path: str) -> dict:
  return validate_file_path(json_path, 'JSON', ('--json', '-j'), is_folder=False, ends_with='json')


def validate_csv_path(csv_path: str) -> dict:
  return validate_file_path(csv_path, 'CSV', ('--csv', '-c'), is_folder=False, ends_with='csv')


def validate_base_path(base_path: str) -> dict:
  return validate_file_path(base_path, 'Base', ('--base', '-b'), False)


def build_operation_result(status: bool = True, reason: str = None) -> dict:
  operation_result = {STATUS_KEY: status}
  if reason is not None:
    operation_result[REASON_KEY] = reason
  return operation_result


if __name__ == '__main__':
  execute()
