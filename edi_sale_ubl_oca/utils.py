# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.tools import DotDict


def ubl_party_from_partner(partner, **kw):
    party = DotDict(
        name=partner.name, identifiers=[DotDict(attrs={}, value=partner.id)]
    )
    party.update(kw)
    return party
