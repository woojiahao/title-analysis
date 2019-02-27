import click


@click.command()
@click.option('--csv', help='.csv file to merge')
@click.option('--json', help='.json file to merge')
@click.option('--output', help='Analyzed file output location')
def analyze(csv, json, output):
  print(csv)
  print(json)
  print(output)


if __name__ == '__main__':
  analyze()
