from typing import Optional
import click
import os
from eagle.runner import Runner


@click.group()
def runner_cli():
    pass


@runner_cli.command()
@click.option('--root_path', '-d', help='Test root directory')
@click.option('--exclude', '-e', help='Exclude test directory')
@click.option('--prefix', '-p', help='Test case prefix')
def run(
    root_path: Optional[str] = None,
    exclude: Optional[str] = None,
    prefix: Optional[str] = None,
):  # sourcery skip: avoid-builtin-shadow
    if root_path is None:
        root_path = os.getcwd()
    Runner(root_path=root_path, prefix=prefix).run()
