import os
import sys
import json

from mlt.commands import Command
from mlt.utils import process_helpers


class Undeploy(Command):
    def action(self, args):
        """deletes current kubernetes namespace"""
        if not os.path.isfile('mlt.json'):
            print("run `mlt undeploy` within a project directory")
            sys.exit(1)

        with open('mlt.json') as f:
            config = json.load(f)
        namespace = config['namespace']
        process_helpers.run(
            ["kubectl", "--namespace", namespace, "delete", "-f", "k8s"])
