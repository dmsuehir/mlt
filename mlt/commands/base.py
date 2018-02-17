import json
import os
import sys


class Command(object):
    def __init__(self):
        pass

    def action(self, args):
        raise NotImplementedError()

    # TODO: remove this
    def _get_push_status(self):
        with open('.push.json') as f:
            return = json.load(f)

    def _fetch_action_arg(self, action, arg):
        desired_arg = None
        action_json = '.{}.json'.format(action)
        if os.path.isfile(action_json):
            with open(action_json) as f:
                desired_arg = json.load(f)[arg]
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
