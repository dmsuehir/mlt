#!/usr/bin/env python
"""mlt.
Usage:
  mlt (-h | --help)
  mlt --version
  mlt init [--template=<template>] [--registry=<registry>] <name>
  mlt build [--watch]
  mlt deploy
  mlt undeploy
  mlt (template | templates) list

Options:
  --template=<template> Template name for app
                        initialization [default: hello-world].
  --registry=<registry> Container registry to use.
                        If none is set, will attempt to use gcloud.
"""
import sys
import os

from docopt import docopt

from mlt.commands import Build, Command, Deploy, Init, Templates, Undeploy

# every available command and its corresponding action will go here
COMMAND_MAP = {
    'build': Build,
    'deploy': Deploy,
    'init': Init,
    'template': Templates,
    'templates': Templates,
    'undeploy': Undeploy
}


def run_command(args):
    """maps params from docopt into mlt commands"""
    # TODO: is there no better way to get what's passed other than
    # if statements or iterating over the dict?
    # for sure we'll have a valid arg here, otherwise docopt will complain
    for key, val in args.items():
        # need to ignore things like --template for now
        if val and not key.startswith('--'):
            desired_arg = key
            break
    # if command doesn't exist yet, fall back to default command handling
    COMMAND_MAP.get(desired_arg, Command)().action(args)


def main():
    args = docopt(__doc__, version="ML Container Templates v0.0.1")
    try:
        run_command(args)
    except:
        # ex: export MLT_DEBUG=1 will dump a traceback on fail
        if os.environ.get('MLT_DEBUG', '') != '':
            import traceback
            traceback.print_exc()
