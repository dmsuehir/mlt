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

from mock import patch
import os
import pytest
import shutil
import uuid

from mlt.commands.init import InitCommand
from mlt.utils import constants
from test_utils.io import catch_stdout
from test_utils import project


def test_init_dir_exists():
    new_dir = str(uuid.uuid4())
    os.mkdir(new_dir)
    init_dict = {
        'init': True,
        '--template': 'hello-world',
        '<name>': new_dir,
        '--template-repo': project.basedir()
    }
    try:
        with catch_stdout() as caught_output:
            with pytest.raises(SystemExit) as bad_init:
                InitCommand(init_dict).action()
                assert caught_output.getvalue() == \
                    "Directory '{}' already exists: delete ".format(
                        new_dir) + "before trying to initialize new " + \
                    "application"
                assert bad_init.value.code == 1
    finally:
        os.rmdir(new_dir)


@patch('mlt.commands.init.check_output')
@patch('mlt.commands.init.copytree')
@patch('mlt.commands.init.process_helpers')
@patch('mlt.commands.init.open')
def test_init(open_mock, proc_helpers, copytree_mock, check_output):
    check_output_mock.return_value.decode.return_value = 'bar'
    new_dir = str(uuid.uuid4())

    init_dict = {
        'init': True,
        '--template': 'hello-world',
        '--template-repo': project.basedir(),
        '--registry': None,
        '--namespace': None,
        '<name>': new_dir
    }
    init = InitCommand(init_dict)
    init.action()
    assert init.app_name == new_dir


@patch('mlt.commands.init.json')
@patch('mlt.commands.init.copytree')
@patch('mlt.commands.init.process_helpers')
@patch('mlt.commands.init.open')
def test_init(open_mock, proc_helpers, copytree_mock, json_mock):
    new_dir = str(uuid.uuid4())
    init_dict = {
        'init': True,
        '--template': 'hello-world',
        '--template-repo': project.basedir(),
        '--registry': True,
        '--namespace': None,
        '<name>': new_dir
    }
    json_mock.loads.return_value = {"greeting": "hello"}
    init = InitCommand(init_dict)
    init.action()
    assert init.app_name == new_dir


def test_template_params():
    new_dir = str(uuid.uuid4())
    init_dict = {
        'init': True,
        '--template': 'tf-dist-mnist',
        '--template-repo': project.basedir(),
        '--registry': True,
        '--namespace': None,
        '<name>': new_dir
    }
    init = InitCommand(init_dict)
    template_params = [{'name': 'num_ps', 'value': '1'},
                       {'name': 'num_workers', 'value': '2'}]
    result = init._build_mlt_json(template_params)
    assert constants.TEMPLATE_PARAMETERS in result
    result_params = result[constants.TEMPLATE_PARAMETERS]
    for param in template_params:
        assert param["name"] in result_params
        assert param["value"] == result_params[param["name"]]


def test_no_template_params():
    new_dir = str(uuid.uuid4())
    init_dict = {
        'init': True,
        '--template': 'tf-dist-mnist',
        '--template-repo': project.basedir(),
        '--registry': True,
        '--namespace': None,
        '<name>': new_dir
    }
    init = InitCommand(init_dict)
    template_params = None
    result = init._build_mlt_json(template_params)
    assert constants.TEMPLATE_PARAMETERS not in result


