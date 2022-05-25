# Copyright 2020 ACSONE
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
from .common import EDIBackendCommonTestCase


class EDIExchangeTypeTestCase(EDIBackendCommonTestCase):
    def test_advanced_settings(self):
        settings = """
        components:
            foo: this
            boo: that
        whatever:
            ok: True
        """
        self.exchange_type_out.advanced_settings_edit = settings
        # fmt:off
        expected = {
            "components": {
                "foo": "this",
                "boo": "that",
            },
            "whatever": {
                "ok": True,
            }
        }
        # fmt:on
        self.assertEqual(self.exchange_type_out.advanced_settings, expected)
        self.assertEqual(self.exchange_type_out.get_settings(), expected)
