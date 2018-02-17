import os
import sys
import json

from mlt.commands import NeedsInitCommand
from mlt.utils import process_helpers


class Undeploy(NeedsInitCommand):
    def action(self, args):
        """deletes current kubernetes namespace"""
        namespace = self.config['namespace']
        process_helpers.run(
            ["kubectl", "--namespace", namespace, "delete", "-f", "k8s"])
