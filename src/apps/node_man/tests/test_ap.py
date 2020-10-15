from unittest.mock import patch

from django.test import TestCase

from apps.node_man.handlers.ap import APHandler
from apps.node_man.models import AccessPoint
from apps.node_man.tests.utils import mock_read_remote_file_content, create_ap


class TestAP(TestCase):
    def test_ap_list(self):
        number = 3
        create_ap(number)
        ap_ids = AccessPoint.objects.all().values_list("id", flat=True)
        result = APHandler().ap_list(ap_ids)
        self.assertEqual(number, len(result))

    @patch("apps.node_man.handlers.ap.read_remote_file_content", mock_read_remote_file_content)
    def test_init_plugin_data(self):
        create_ap(1)
        result = APHandler().init_plugin_data("admin")
        self.assertEqual(result[0]["gseplugindesc"]["name"], "basereport")
        result = APHandler().init_plugin_data("admin", ap_id=1)
        self.assertEqual(result[0]["gseplugindesc"]["name"], "basereport")

    def test_init(self):
        data = {
            "gseplugindesc": {"id": 1, "name": "basereport"},
            "packages": {
                "id": 1,
                "module": "gse_plugin",
                "project": "basereport",
                "version": "latest",
                "os": "linux",
                "cpu_arch": "x86_64",
                "pkg_size": 2,
            },
            "proccontrol": {"id": 1, "module": "gse_plugin", "project": "basereport", "os": "linux"},
        }
        result = APHandler()._init(data)
        self.assertEqual(result["gseplugindesc"]["name"], "basereport")
