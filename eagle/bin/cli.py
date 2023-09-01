from typing import Optional
import click
import os
# from easy_tester.core.runner import Runner


@click.group()
def runner_cli():
    pass


@runner_cli.command()
@click.option('--dir', '-d', help='Test directory')
@click.option('--exclude', '-e', help='Exclude test directory')
@click.option('--prifx', '-p', help='Test case prefix')
def run(
    dir: Optional[str] = None,
    exclude: Optional[str] = None,
    prifx: Optional[str] = None,
):  # sourcery skip: avoid-builtin-shadow
    if dir is None:
        dir = os.getcwd()
    ...
    from eagle.logger import logger
    
    logger.debug(f"{dir}")
    logger.info(f"{dir}")
    logger.warning(f"{dir}")
    logger.error(f"{dir}")
    logger.critical(f"{dir}")