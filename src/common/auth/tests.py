# -*- coding: utf-8 -*-
from django.conf import settings
from rest_framework.test import APITestCase
from apps.common.auth.perms import UserPerm


class TestUserPerm(APITestCase):

    def test_check(self):
        self.assertFalse(UserPerm('test_user', settings.APP_CODE).check(
            'project.retrieve', '132')
        )

    def test_list_scope(self):
        self.assertFalse(UserPerm('test_user', settings.APP_CODE).list_scopes('project.retrieve'))
