# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import models

from ..utils import ubl_party_from_partner


class EDIExchangeTemplateMixin(models.AbstractModel):
    _inherit = "edi.exchange.template.mixin"

    def _get_code_snippet_eval_context(self):
        res = super()._get_code_snippet_eval_context()
        res["ubl_party_from_partner"] = ubl_party_from_partner
        return res
