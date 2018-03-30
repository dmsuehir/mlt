#
# -*- coding: utf-8 -*-
#
# Copyright (c) 2018 Intel Corporation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# SPDX-License-Identifier: EPL-2.0
#

import getpass
import json
import os
import sys
import shutil
from subprocess import check_output
import traceback

from mlt import TEMPLATES_DIR
from mlt.commands import Command
from mlt.utils import constants, process_helpers, git_helpers


class InitCommand(Command):
    def __init__(self, args):
        super(InitCommand, self).__init__(args)
        self.app_name = self.args["<name>"]

    def action(self):
        """Creates a new git repository based on an mlt template in the
           current working directory.
        """
        template_name = self.args["--template"]
        template_repo = self.args["--template-repo"]

        with git_helpers.clone_repo(template_repo) as temp_clone:
            templates_directory = os.path.join(
                temp_clone, TEMPLATES_DIR, template_name)

            try:
                shutil.copytree(templates_directory, self.app_name)

                template_params = self._get_template_parameters(templates_directory)
                data = self._build_mlt_json(template_params)
                with open(os.path.join(self.app_name,
                                       constants.MLT_CONFIG_FILE), 'w') as f:
                    json.dump(data, f, indent=2)
                self._init_git_repo()
            except OSError as exc:
                if exc.errno == 17:
                    print(
                        "Directory '{}' already exists: delete before trying "
                        "to initialize new application".format(self.app_name))
                else:
                    traceback.print_exc()

                sys.exit(1)

    def _get_template_parameters(self, templates_directory):
        """
        Returns template-specific parameters from the template config file
        in the app directory.  
        """
        parameters_file = os.path.join(templates_directory,
                                       constants.TEMPLATE_CONFIG_FILE)

        params = None
        if os.path.isfile(parameters_file):
            with open(parameters_file) as f:
                params = json.load(f).get("parameters")

        return params

    def _build_mlt_json(self, template_parameters):
        """generates the data to write to mlt.json"""
        data = {'name': self.app_name, 'namespace': self.app_name}
        if not self.args["--registry"]:
            raw_project_bytes = check_output(
                ["gcloud", "config", "list", "--format",
                 "value(core.project)"])
            project = raw_project_bytes.decode("utf-8").strip()
            data['gceProject'] = project
        else:
            data['registry'] = self.args["--registry"]
        if not self.args["--namespace"]:
            data['namespace'] = getpass.getuser()
        else:
            data['namespace'] = self.args["--namespace"]

        # Add template specific parameters to the data dictionary
        if template_parameters:
            template_data = data[constants.TEMPLATE_PARAMETERS] = {}
            for param in template_parameters:
                template_data[param["name"]] = param["value"]

        return data

    def _init_git_repo(self):
        """
        Initialize new git repo in the project dir and commit initial state.
        """
        process_helpers.run(["git", "init", self.app_name])
        process_helpers.run(["git", "add", "."], cwd=self.app_name)
        print(process_helpers.run(
            ["git", "commit", "-m", "Initial commit."], cwd=self.app_name))
