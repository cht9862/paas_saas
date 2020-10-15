from django.test import TestCase

from apps.node_man.handlers.tjj import TjjHandler


class TestTJJ(TestCase):
    def test_fetch_pwd(self):
        # 第一个分支
        result = TjjHandler().fetch_pwd("admin", ["111.111.111.111"], "ticket")
        self.assertEqual(result["code"], -1)
