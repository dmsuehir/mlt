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

import uuid
from mock import patch

from mlt.utils.kubernetes_helpers import check_crds, ensure_namespace_exists
from test_utils.io import catch_stdout


@patch('mlt.utils.kubernetes_helpers.call')
@patch('mlt.utils.kubernetes_helpers.open')
@patch('mlt.utils.kubernetes_helpers.process_helpers')
def test_ensure_namespace_no_exist(proc_helpers, open_mock, call):
    call.return_value = 0

    ensure_namespace_exists(str(uuid.uuid4()))
    proc_helpers.run.assert_not_called()


@patch('mlt.utils.kubernetes_helpers.call')
@patch('mlt.utils.kubernetes_helpers.open')
@patch('mlt.utils.kubernetes_helpers.process_helpers')
def test_ensure_namespace_already_exists(proc_helpers, open_mock, call):
    call.return_value = 1

    ensure_namespace_exists(str(uuid.uuid4()))
    proc_helpers.run.assert_called_once()


def test_crd_check_file_does_not_exist():
    with catch_stdout() as caught_output:
        check_crds(False, "foo")
        output = caught_output.getvalue().lower()

    assert "skipping crd check" in output
    assert "does not exist" in output
