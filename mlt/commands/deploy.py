import os
import json
import time
import uuid
import sys
from string import Template
from subprocess import Popen, PIPE
from termcolor import colored

from mlt.commands import Build, Command
from mlt.utils import process_helpers, progress_bar, kubernetes_helpers


class Deploy(Command):
    def action(self, args):
        if not os.path.isfile('.build.json'):
            Build().do_build(args)

        self.push(args)

        with open('mlt.json') as f:
            config = json.load(f)
        app_name = config['name']
        namespace = config['namespace']

        with open('.push.json') as f:
            status = json.load(f)
        remote_container_name = status['last_remote_container']
        run_id = str(uuid.uuid4())

        print("Deploying {}".format(remote_container_name))

        # Write new container to deployment
        for filename in os.listdir("k8s-templates"):
            with open(os.path.join('k8s-templates', filename)) as f:
                deployment_template = f.read()
                template = Template(deployment_template)
                out = template.substitute(image=remote_container_name,
                                          app=app_name, run=run_id)

                with open(os.path.join('k8s', filename), 'w') as f:
                    f.write(out)

            kubernetes_helpers.ensure_namespace_exists(namespace)
            process_helpers.run(
                ["kubectl", "--namespace", namespace, "apply", "-R",
                 "-f", "k8s"])

            print("\nInspect created objects by running:\n"
                  "$ kubectl get --namespace={} all\n".format(namespace))

    def push(self, args):
        last_push_duration = None
        # TODO: better name for this file, and not local path-specific
        if os.path.isfile('.push.json'):
            with open('.push.json') as f:
                status = json.load(f)
            last_push_duration = status['last_push_duration']

        container_name = None
        # TODO: probably don't have to worry about this since `deploy` calls
        # build if there's no build step yet
        if os.path.isfile('.build.json'):
            with open('.build.json') as f:
                status = json.load(f)
            container_name = status['last_container']
        else:
            print("Need to run build before pushing")
            sys.exit(1)

        with open('mlt.json') as f:
            config = json.load(f)

        is_gke = 'gceProject' in config

        if is_gke:
            remote_container_name = "gcr.io/" + \
                config['gceProject'] + "/" + container_name
        else:
            remote_container_name = config['registry'] + "/" + container_name

        started_push_time = time.time()
        process_helpers.run(
            ["docker", "tag", container_name, remote_container_name])

        if is_gke:
            push_process = Popen(["gcloud", "docker", "--", "push",
                                  remote_container_name],
                                 stdout=PIPE, stderr=PIPE)
        else:
            push_process = Popen(
                ["docker", "push", remote_container_name],
                stdout=PIPE, stderr=PIPE)

        progress_bar.duration_progress(
            'Pushing ', last_push_duration,
            lambda: push_process.poll() is not None)
        if push_process.poll() != 0:
            print(colored(push_process.communicate()[0], 'red'))
            sys.exit(1)

        pushed_time = time.time()

        with open('.push.json', 'w') as f:
            f.write(json.dumps({
                "last_remote_container": remote_container_name,
                "last_push_duration": pushed_time - started_push_time
            }))

        print("Pushed to {}".format(remote_container_name))
