import json
import os
import sys
import shutil
from subprocess import check_output

from mlt import TEMPLATES_DIR
from mlt.utils import process_helpers


# TODO: debated using `git` package instead of calling out to git, but
# git package takes a bit to import afair so didn't change it on first pass
def init(args):
    print(args)
    template_directory = os.path.join(TEMPLATES_DIR, args["--template"])
    app_name = args["<name>"]
    is_gke = args["--registry"] is None

    try:
        shutil.copytree(template_directory, app_name)

        data = {'name': app_name, 'namespace': app_name}
        if is_gke:
            raw_project_bytes = check_output(
                ["gcloud", "config", "list", "--format",
                 "value(core.project)"])
            project = raw_project_bytes.decode("utf-8").strip()
            data['gceProject'] = project
        else:
            data['registry'] = args["--registry"]

        with open(os.path.join(app_name, 'mlt.json'), 'w') as f:
            f.write(json.dumps(data, f, indent=2))

        # Initialize new git repo in the project dir and commit initial state.
        process_helpers.run(["git", "init", app_name])
        process_helpers.run(["git", "add", "."], cwd=app_name)
        print(process_helpers.run(
            ["git", "commit", "-m", "Initial commit."], cwd=app_name))

    except OSError as exc:
        if exc.errno == 17:
            print(
                "Directory '{}' already exists: delete before trying to "
                "initialize new application".format(app_name))
        else:
            print(exc)

        sys.exit(1)
