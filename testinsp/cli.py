import click
from pprint import pprint
from testinsp.main import RunChecks
from subprocess import check_output
from sys import stderr


def external_wrap(how):
    def shell_executor(command):
        splitted = how[1:].split(how[0])
        cmd_list = splitted + [command]
        stderr.write(f">> executed cmd: {cmd_list}\n")
        raw_out = check_output(cmd_list)
        return raw_out.decode() if hasattr(raw_out, "decode") else raw_out

    return shell_executor


@click.group()
@click.option(
    "--executor",
    default="",
    help="Use own shell command to execute shell commands (e.g. ' ssh user@server -i private/key/path'). First character is used as separator for command splitting. shell command is then pasted as one argument",
)
@click.pass_context
def cli(ctx, executor):
    external_executor = external_wrap(executor)
    ctx.ensure_object(dict)
    if executor:
        ctx.obj["check"] = RunChecks(external_executor=external_executor)
    else:
        ctx.obj["check"] = RunChecks()


@cli.command()
@click.pass_context
def init(ctx):
    checker = ctx.obj["check"]
    checker.init()
    checker.store()


@cli.command()
@click.pass_context
def check(ctx):
    checker = ctx.obj["check"]
    checker.load()
    out = checker.check()
    pprint(out)


if __name__ == "__main__":
    cli()
