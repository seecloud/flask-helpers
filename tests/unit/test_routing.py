# Copyright 2016: Mirantis Inc.
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

import mock
import testtools

from oss_lib import routing


class RoutingTestCase(testtools.TestCase):

    def test_get_routing_list(self):
        app = mock.Mock()
        rules = (
            {"rule": "foo_rule", "methods": ["f", "a"], "endpoint": "foo_ep"},
            {"rule": "bar_rule", "methods": ["b", "c"], "endpoint": "bar_ep"})
        app.url_map.iter_rules.return_value = [
            mock.Mock(**kv) for kv in rules]
        expected = [
            {"endpoint": "bar_ep", "methods": ["b", "c"], "uri": "bar_rule"},
            {"endpoint": "foo_ep", "methods": ["a", "f"], "uri": "foo_rule"}]
        self.assertEqual(expected, routing.get_routing_list(app))

    @mock.patch("oss_lib.routing.flask")
    @mock.patch("oss_lib.routing.get_routing_list")
    def test_add_routing_map(self, mock_get_routing_list, mock_flask):
        app = mock.Mock()
        mock_bp = mock.Mock()
        mock_flask.Blueprint.return_value = mock_bp
        mock_get_routing_list.return_value = ["foo_route", "bar_route"]
        result_app = routing.add_routing_map(app)

        mock_flask.Blueprint.assert_called_once_with(
            "routing_map", "oss_lib.routing",
            template_folder="templates")
        mock_bp.route.assert_has_calls(
            [mock.call("/map.html", endpoint="routing_map_html"),
             mock.call("/map.json", endpoint="routing_map_json")],
            any_order=True)
        result_app.register_blueprint.assert_called_once_with(mock_bp)
        self.assertEqual(app, result_app)
