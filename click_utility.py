import click

LOG_WARNING = 'WARNING'
LOG_LOGGING = 'LOG'
LOG_ERROR = 'ERROR'

def click_log(status: str = LOG_LOGGING, title: str = None, description: str = '', is_error: bool = False):
  message = f'[{status}] {description}' if title is None else f'[{status}] {title} :: {description}'
  click.echo(message, err=is_error)