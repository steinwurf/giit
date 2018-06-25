import click

import giit.build


@click.command()
@click.option('--source_branch')
@click.option('--build_path')
@click.option('--data_path')
@click.option('--json_config')
@click.argument('step')
@click.argument('repository')
def cli(step, repository, build_path, data_path, json_config,
        source_branch):

    build = giit.build.Build(
        step=step, repository=repository,
        build_path=build_path, data_path=data_path,
        json_config=json_config, source_branch=source_branch)

    build.run()


if __name__ == "__main__":
    cli()
