# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _wamas_export(self, specific_dict=None, telegram_type=False):
        """
        Export the product data as WAMAS format

        :return: product data as WAMAS format
        :rtype: a byte
        """
        self.ensure_one()
        dict_product = self.read()[0]
        # If having a specific dict for the product, we use it
        if specific_dict and isinstance(specific_dict, dict):
            dict_product = specific_dict
        return self.env["base.wamas.ubl"].export_dict2wamas(dict_product, telegram_type)
