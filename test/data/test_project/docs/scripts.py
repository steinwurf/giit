#!/usr/bin/env python
# encoding: utf-8

import click
import os


@click.command()
@click.option('--out')
def run(out):

    if not os.path.isdir(out):
        os.makedirs(out)

    filename = os.path.join(out, 'docs.txt')
    with open(filename, "w") as f:
        f.write("Hello World")


if __name__ == "__main__":
    run()
