# Copyright 2024 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.addons.component.core import Component


class EDIConfigSOListener(Component):
    _name = "edi.listener.config.sale.order"
    _inherit = "base.event.listener"
    _apply_on = ["sale.order"]

    # STATES
    # ('draft', 'Quotation'),
    # ('sent', 'Quotation Sent'),
    # ('sale', 'Sales Order'),
    # ('done', 'Locked'),
    # ('cancel', 'Cancelled'),

    def on_edi_sale_order_state_sale(self, record):
        trigger = "on_edi_sale_order_state_sale"
        return self._exec_conf(record, trigger)

    def on_edi_sale_order_state_quotation_sent(self, record):
        trigger = "on_edi_sale_order_state_quotation_sent"
        return self._exec_conf(record, trigger)

    def on_edi_sale_order_state_cancel(self, record):
        trigger = "on_edi_sale_order_state_cancel"
        return self._exec_conf(record, trigger)

    def on_edi_sale_order_state_done(self, record):
        trigger = "on_edi_sale_order_state_done"
        return self._exec_conf(record, trigger)

    def on_edi_sale_order_state_draft(self, record):
        trigger = "on_edi_sale_order_state_draft"
        return self._exec_conf(record, trigger)

    def _exec_conf(self, record, trigger, conf_field="edi_sale_conf_ids"):
        confs = record.partner_id[conf_field].edi_get_conf(trigger)
        for conf in confs:
            conf.edi_exec_snippet_do(record)
