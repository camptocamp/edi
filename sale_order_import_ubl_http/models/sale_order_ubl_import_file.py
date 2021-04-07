# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import base64
import logging

from odoo import fields, models

_logger = logging.getLogger(__name__)


class SaleOrderUBLImportFile(models.Model):
    _name = "sale.order.ubl.import.file"
    _description = "UBL files to generate sale orders"

    active = fields.Boolean(default=True)
    attachment_id = fields.Many2one(
        comodel_name="ir.attachment",
        ondelete="cascade",
        index=True,
        auto_join=True,
        delegate=True,
        required=True,
    )
    method_name = fields.Char(required=True)
    job_id = fields.Many2one(comodel_name="queue.job", ondelete="set null",)
    job_state = fields.Selection(related="job_id.state", store=True)
    parent_id = fields.Many2one(
        comodel_name="sale.order.ubl.import.file",
        ondelete="cascade",
        help="Valued if this import has been attempted several times.",
    )

    def _quick_create(self, xml_data, method_name, parent=None, **kw):
        """Create files quickly with relevant data.

        :param xml_data: bytes-like xml data
        :param method_name: str name of the method used on sale order
        :param parent: optional file record for parent
        """
        xml_data = base64.encodestring(xml_data)
        number = self.env["ir.sequence"].next_by_code("ubl.import.sale.order")
        vals = {
            "datas": xml_data,
            "res_model": "sale.order",
            "mimetype": "application/xml",
            "name": "{}.xml".format(number),
            "method_name": method_name,
            "parent_id": parent.id if parent else False,
        }
        vals.update(kw)
        return self.create(vals)

    def _mark_done_for_order(self, order):
        """Mark current file as done for given sale order.

        Link the order and archive current record and all parents if any.
        """
        self.res_id = order.id
        # Archive parents as well
        to_archive = self
        parent = self.parent_id
        while parent and parent.active:
            to_archive |= parent
            parent = parent.parent_id
        to_archive.write({"active": False})
        _logger.info("Archived records: %s", ", ".join(to_archive.mapped("name")))
