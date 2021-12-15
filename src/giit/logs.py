#!/usr/bin/env python
# encoding: utf-8

import os
import sys
import logging


def setup_logging(giit_path, verbose):

    logger = logging.getLogger("giit")
    logger.setLevel(logging.DEBUG)

    # Create file handler which logs even debug messages
    logfile = os.path.join(giit_path, "giit.log")
    fh = logging.FileHandler(logfile)
    fh.setLevel(logging.DEBUG)

    # Create console handler with a higher log level
    ch = logging.StreamHandler(stream=sys.stdout)
    ch.setLevel(logging.DEBUG if verbose else logging.INFO)

    # Create formatter and add it to the handlers
    fh_formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    fh.setFormatter(fh_formatter)

    ch_formatter = logging.Formatter("%(message)s")
    ch.setFormatter(ch_formatter)

    # Add the handlers to the logger
    logger.addHandler(fh)
    logger.addHandler(ch)
