import json
import os
import sys


class Command(object):
    def __init__(self):
        # will store the build and push file json
        self._file_contents = {}

    def action(self, args):
        raise NotImplementedError()

    def _fetch_action_arg(self, action, arg):
        desired_arg = None
        action_json = '.{}.json'.format(action)
        # check if we have the json cached or not
        if not action_json in self._file_contents:
            if os.path.isfile(action_json):
                with open(action_json) as f:
                    self._file_contents[action_json] = json.load(f)
        desired_arg = self._file_contents[action_json][arg]
        return desired_arg


class NeedsInitCommand(Command):
    """
    Build, Deploy, Undeploy require being inside a dir that was created
    from Init
    """

    def __init__(self):
        self._verify_init()
        self._load_config()
        super(NeedsInitCommand, self).__init__()

    def _verify_init(self):
        if not os.path.isfile('mlt.json'):
            print("This command requires you to be in an `mlt init` "
                  "built directory.")
            sys.exit(1)

    def _load_config(self):
        with open('mlt.json') as f:
            self.config = json.load(f)


class NeedsBuildCommand(Command):
    """We cannot deploy without first having a build"""

    def __init__(self):
        self._verify_build()
        super(NeedsBuildCommand, self).__init__()

    def _verify_build(self):
        if not os.path.isfile('.build.json'):
            # TODO: see if there's a way to get rid of circular import here
            from mlt.commands.build import Build
            Build().action(args)
