# Copyright 2020 ACSONE SA
# Copyright 2022 Camptocamp
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo.addons.http_routing.models.ir_http import slugify


def normalize_string(a_string, sep="_"):
    """Normalize given string, replace dashes with given separator."""
    return slugify(a_string).replace("-", sep)


def get_exception_msg(exc):
    if hasattr(exc, "args") and isinstance(exc.args[0], str):
        return exc.args[0]
    # TODO: not sure this happens anymore
    # as Odoo exceptions now inherit fully from python base classes.
    return repr(exc)
