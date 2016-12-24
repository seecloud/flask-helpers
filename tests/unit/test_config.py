# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import unittest

import ddt
import jsonschema
import mock
import yaml

from oss_lib import config


@ddt.ddt
class ConfigTestCase(unittest.TestCase):
    @ddt.data(
        "CEAGLE_SUFFIX",
        "CEAGLE_123_SUFFIX",
        "CEAGLE1_23_SUFFIX",
    )
    def test_check_service_prefix(self, service_prefix):
        config.check_service_prefix(service_prefix)

    @ddt.data(
        "123ceagle",
        "123CEAGLE",
        "ceagle",
        "-CEAGLE",
    )
    def test_create_safe_prefix_error(self, service_prefix):
        with self.assertRaises(RuntimeError):
            config.check_service_prefix(service_prefix)

    def test_register_arguments(self):
        parser = mock.Mock()
        config.register_arguments(parser, "CEAGLE")
        assert parser.add_argument.mock_calls == [
            mock.call("--config-file",
                      dest="config_path",
                      metavar="PATH",
                      help=mock.ANY),
            mock.call("--log-config-file",
                      dest="log_config_path",
                      metavar="PATH",
                      help=mock.ANY),
            mock.call("--debug",
                      action="store_true",
                      default=False,
                      help=mock.ANY),
        ]

    FULL_ENV = {
        "CEAGLE_CONF": "conf",
        "CEAGLE_LOG_CONF": "log-conf",
        "CEAGLE_DEBUG": "true",
    }
    UNCLEAR_ENV = dict(FULL_ENV, **{
        "_CONF": "conf2",
        "HEALTH_CONF": "conf3",
    })
    FULL_VARS = {
        "config_path": "conf",
        "log_config_path": "log-conf",
        "debug": True,
    }
    DEFAULT_VARS = {
        "config_path": None,
        "log_config_path": None,
        "debug": False,
    }

    @ddt.data(
        ("CEAGLE", FULL_ENV, FULL_VARS),
        ("CEAGLE", UNCLEAR_ENV, FULL_VARS),
        ("CEAGLE", {}, DEFAULT_VARS),
        ("HEALTH", FULL_ENV, DEFAULT_VARS),
    )
    @ddt.unpack
    def test_get_env_variables(self, service_prefix, env, variables):
        with mock.patch.dict("oss_lib.config.os.environ", env):
            result = config.get_env_variables(service_prefix)
        assert result == variables

    @ddt.data(
        ("path1", "path2", False, "path1"),
        (None, "path2", True, "path2"),
        (None, "path2", False, None),
        (None, None, False, None),
    )
    @ddt.unpack
    @mock.patch("oss_lib.config.os.path.exists")
    @mock.patch("oss_lib.config.yaml_load")
    def test_load_config_file(self, path, default_path, default_exists,
                              expected_path, mock_load, mock_exists):
        mock_load.return_value._path = expected_path
        mock_exists.return_value = default_exists

        result = config.load_config_file(
            path, default_config_path=default_path)

        if not path and default_path:
            mock_exists.assert_called_once_with(default_path)
        else:
            assert not mock_exists.called

        if expected_path is not None:
            mock_load.assert_called_once_with(expected_path)
            assert result is mock_load.return_value
            assert result._path == expected_path
        else:
            assert not mock_load.called
            assert result is None

    @mock.patch("oss_lib.config.open", create=True)
    @mock.patch("oss_lib.config.yaml.safe_load")
    def test_yaml_load(self, mock_load, mock_open):
        result = config.yaml_load("fakepath")
        mock_open.assert_called_once_with("fakepath")
        mock_load.assert_called_once_with(
            mock_open.return_value.__enter__.return_value)
        assert result is mock_load.return_value

    @mock.patch("oss_lib.config.open", create=True)
    @mock.patch("oss_lib.config.yaml.safe_load")
    @mock.patch("oss_lib.config.LOG.error")
    def test_yaml_load_open_error(self, mock_log, mock_load, mock_open):
        mock_open.side_effect = IOError("open errmsg")
        with self.assertRaisesRegexp(IOError, "open errmsg"):
            config.yaml_load("fakepath")
        assert mock_open.called
        assert not mock_load.called
        assert mock_log.called

    @mock.patch("oss_lib.config.open", create=True)
    @mock.patch("oss_lib.config.yaml.safe_load")
    @mock.patch("oss_lib.config.LOG.error")
    def test_yaml_load_load_error(self, mock_log, mock_load, mock_open):
        mock_load.side_effect = yaml.YAMLError("yaml errmsg")
        with self.assertRaisesRegexp(yaml.YAMLError, "yaml errmsg"):
            config.yaml_load("fakepath")
        assert mock_open.called
        assert mock_load.called
        assert mock_log.called

    @ddt.data(
        (
            {},
            {"a": 1, "b": [2, 3]},
            {"a": 1, "b": [2, 3]},
        ),
        (
            {"a": 1, "b": [2, 3]},
            {},
            {"a": 1, "b": [2, 3]},
        ),
        (
            {"a": 1, "c": 2},
            {"b": 3, "c": 4},
            {"a": 1, "b": 3, "c": 4},
        ),
        (
            {"a": {"b": 1, "c": 2}, "d": 3},
            {"a": {"b": 4}},
            {"a": {"b": 4, "c": 2}, "d": 3},
        ),
    )
    @ddt.unpack
    def test_merge_dicts(self, one, other, result):
        config.merge_dicts(one, other)
        assert one == result

    @ddt.data(
        ({}, {}, []),
        (None, {}, []),
        ({}, {"a": {"type": "integer"}}, ["a"]),
        ({"a": 1}, {"a": {"type": "integer"}}, []),
        (
            {"a": 1},
            {"a": {"type": "integer"}, "b": {"type": "string"}},
            ["b"],
        ),
    )
    @ddt.unpack
    def test_get_required_properties(self, defaults, schema, result):
        value = config.get_required_properties(defaults, schema)
        assert value == result

    @ddt.data(
        ({}, None, False),
        ({"a": 1234}, None, True),
        ({"a": 1234}, {"a": {"type": "integer"}}, False),
        ({"a": 1234}, {"a": {"type": "string"}}, True),
        ({}, {"b": {"type": "string"}}, True),
        (
            {"a": 1234},
            {"a": {"type": "integer"}, "b": {"type": "string"}},
            True,
        ),
    )
    @ddt.unpack
    def test_validate_config(self, conf, schema, error):
        if error:
            with self.assertRaises(jsonschema.exceptions.ValidationError):
                config.validate_config(conf, validation_schema=schema)
        else:
            config.validate_config(conf, validation_schema=schema)
