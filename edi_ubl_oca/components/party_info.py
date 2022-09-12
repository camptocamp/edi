# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class EDIPartyInfoUBL(Component):

    _name = "edi.party.info.ubl"
    _inherit = "edi.party.info"
    _backend_type = "ubl"
