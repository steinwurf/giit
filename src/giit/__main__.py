import click

import giit.build


@click.command()
@click.option('--remote_branch')
@click.option('--build_path')
@click.option('--data_path')
@click.option('--json_config')
@click.argument('step')
@click.argument('repository')
def cli(step, repository, build_path, data_path, json_config,
        remote_branch):

    build = giit.build.Build(
        step=step,
        repository=repository,
        build_path=build_path,
        data_path=data_path,
        json_config=json_config,
        remote_branch=remote_branch)

    build.run()


if __name__ == "__main__":
    cli()
