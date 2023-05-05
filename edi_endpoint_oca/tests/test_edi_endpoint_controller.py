# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import os
import unittest

import requests

from odoo import tools
from odoo.tests.common import HttpSavepointCase

HOST = "127.0.0.1"
PORT = tools.config["http_port"]


@unittest.skipIf(os.getenv("SKIP_HTTP_CASE"), "EDIEndpointHttpCase skipped")
class EDIEndpointHttpCase(HttpSavepointCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # force sync for demo records
        cls.env["edi.endpoint"].search([])._handle_registry_sync()

    def test_call1(self):
        endpoint = "/edi/demo/try"
        url = "http://{}:{}{}".format(HOST, PORT, endpoint)
        response = requests.get(url)
        self.assertEqual(response.status_code, 401)
        # Let's login now
        response = requests.get(url, auth=("admin", "admin"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("Created record:", response.content.decode())
