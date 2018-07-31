import click

import giit.build


@click.command()
@click.option('--remote_branch')
@click.option('--build_path')
@click.option('--data_path')
@click.option('--json_config')
@click.option('-v', '--verbose', is_flag=True)
@click.argument('step')
@click.argument('repository')
def cli(step, repository, build_path, data_path, json_config,
        remote_branch, verbose):

    build = giit.build.Build(
        step=step,
        repository=repository,
        build_path=build_path,
        data_path=data_path,
        json_config=json_config,
        remote_branch=remote_branch,
        verbose=verbose)

    build.run()


if __name__ == "__main__":
    cli()
