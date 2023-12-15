import click
from pprint import pprint
from testinsp.main import RunChecks

@click.command()
@click.option('--init', default=False, help='Gather data')
@click.option('--check', default=False, help='Check data and create new')
def cli(init, check):
    checker = RunChecks()
    if init:
        checker.init()
        checker.store()
    elif check:
        checker.load()
        out = checker.check()
        pprint(out)


if __name__ == '__main__':
    cli()
