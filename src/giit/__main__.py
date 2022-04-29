#!/usr/bin/env python
# encoding: utf-8

import sys
import click
import colorama

import giit.build
import giit.logs
import giit.factory


@click.command()
@click.option("--build_path")
@click.option("--giit_path")
@click.option("--config_branch")
@click.option("--config_path")
@click.option("task_filters", "--task_filter", multiple=True)
@click.option(
    "variables", "--variable", nargs=2, type=click.Tuple([str, str]), multiple=True
)
@click.option("-v", "--verbose", is_flag=True)
@click.argument("step")
@click.argument("repository")
def cli(
    step,
    repository,
    build_path,
    giit_path,
    config_branch,
    config_path,
    task_filters,
    variables,
    verbose,
):

    build = giit.build.Build(
        step=step,
        repository=repository,
        factory=giit.factory,
        build_path=build_path,
        giit_path=giit_path,
        config_branch=config_branch,
        config_path=config_path,
        task_filters=task_filters,
        variables=variables,
        verbose=verbose,
    )

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
