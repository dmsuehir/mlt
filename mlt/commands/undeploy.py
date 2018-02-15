import os
import sys
import json

from mlt.utils import process_helpers


def undeploy(args):
    if not os.path.isfile('mlt.json'):
        print("run `mlt undeploy` within a project directory")
        sys.exit(1)

    with open('mlt.json') as f:
        config = json.load(f)
    namespace = config['namespace']
    process_helpers.run(
        ["kubectl", "--namespace", namespace, "delete", "-f", "k8s"])
