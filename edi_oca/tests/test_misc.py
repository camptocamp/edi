# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import exceptions
from odoo.tests.common import TreeCase

from odoo.addons.edi_oca.utils import get_exception_msg, normalize_string


# Cannot use basic unittest class otherwise Odoo test suite won't find it.
class TestMisc(TreeCase):
    def test_get_exception_msg(self):
        class RandomException(Exception):
            pass

        excs = (
            exceptions.UserError("Too bad"),
            exceptions.ValidationError("Too bad"),
            exceptions.MissingError("Too bad"),
            ValueError("Too bad"),
            KeyError("Too bad"),
            RandomException("Too bad"),
        )
        for exc in excs:
            self.assertEqual(get_exception_msg(exc), "Too bad")

    def test_normalize_string(self):
        self.assertEqual(normalize_string("WhAtever! IT? Comes"), "whatever_it_comes")
        self.assertEqual(
            normalize_string("WhAtever! IT? Comes", sep="."), "whatever.it.comes"
        )
