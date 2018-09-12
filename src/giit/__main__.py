import sys
import click
import colorama

import giit.build


@click.command()
#@click.option('--remote_branch')
@click.option('--build_path')
@click.option('--giit_path')
@click.option('--json_config')
@click.option('-v', '--verbose', is_flag=True)
@click.argument('step')
@click.argument('repository')
def cli(step, repository, build_path, giit_path, json_config,
        verbose):
    #        remote_branch, verbose):

    build = giit.build.Build(
        step=step,
        repository=repository,
        build_path=build_path,
        giit_path=giit_path,
        json_config=json_config,
        # remote_branch=remote_branch,
        verbose=verbose)

    try:
        build.run()
    except Exception as e:

        if verbose:
            # We just propagate the exception out
            raise

        colorama.init()
        print(colorama.Fore.RED + str(e))
        sys.exit(1)


if __name__ == "__main__":
    cli()
