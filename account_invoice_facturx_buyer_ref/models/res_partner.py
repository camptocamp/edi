# Copyright 2021 Camptocamp
# @author: Iván Todorovich <ivan.todorovich@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models, fields


class ResPartner(models.Model):
    _inherit = "res.partner"

    facturx_ref = fields.Char(
        string="Factur-X Reference",
        help="Used as Buyer Reference in Factur-X data. "
             "It's required for public organizations in some countries.",
    )
