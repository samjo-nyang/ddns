import traceback

import click


class DDNSError(RuntimeError):
    pass


def is_str(x):
    return isinstance(x, str)


def is_list_str(x):
    return isinstance(x, list) and all(is_str(e) for e in x)


def print_error(e: Exception):
    click.secho(f'[ERROR] {e}', fg='red')
    click.secho(traceback.format_exc(), fg='red')


def print_warn(msg: str):
    click.secho(f'[WARN]  {msg}', fg='yellow')


def print_ok(msg: str):
    click.secho(f'[OK]    {msg}', fg='green')


def print_info(msg: str):
    click.echo(f'[INFO]  {msg}')
