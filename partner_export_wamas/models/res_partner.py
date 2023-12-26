# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _wamas_export(self, specific_dict=None, telegram=False):
        """
        Export the partner data as WAMAS format

        :return: partner data as WAMAS format
        :rtype: a byte
        """
        self.ensure_one()
        dict_partner = self.read()[0]
        # If having a specific dict for the partner, we use it
        if specific_dict and isinstance(specific_dict, dict):
            dict_partner = specific_dict
        base_wamas_ubl = self.env["base.wamas.ubl"]
        return base_wamas_ubl.export_dict2wamas(dict_partner, telegram)
