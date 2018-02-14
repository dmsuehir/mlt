import os
import time
import json
import uuid
import sys

from watchdog.observers import Observer
from termcolor import colored

from mlt.utils import progress_bar
from mlt.event_handler import EventHandler
from mlt.utils.process_helpers import run_popen


def build(args):
    if args['--watch']:
        event_handler = EventHandler(do_build, args)
        observer = Observer()
        # TODO: what dir was this?
        observer.schedule(event_handler, './', recursive=True)
        observer.start()
        try:
            while True:
                time.sleep(1)

        except KeyboardInterrupt:
            observer.stop()
        observer.join()

    else:
        do_build(args)


def do_build(args):
    last_build_duration = None
    if os.path.isfile('.build.json'):
        with open('.build.json') as f:
            status = json.load(f)
        last_build_duration = status['last_build_duration']

    started_build_time = time.time()

    with open('mlt.json') as f:
        config = json.load(f)
    app_name = config['name']

    container_name = "{}:{}".format(app_name, uuid.uuid4())

    print("Starting build {}".format(container_name))

    # Add bar
    build_process = run_popen(["docker", "build", "-t", container_name, "."])

    progress_bar.duration_progress(
        'Building', last_build_duration,
        lambda: build_process.poll() is not None)
    if build_process.poll() != 0:
        print(colored(build_process.communicate()[0], 'red'))
        sys.exit(1)

    built_time = time.time()

    # Write last container to file
    with open('.build.json', 'w') as f:
        f.write(json.dumps({
            "last_container": container_name,
            "last_build_duration": built_time - started_build_time
        }))

    print("Built {}".format(container_name))
