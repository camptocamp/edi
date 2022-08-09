# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from odoo import fields, models


class EdiAutoExchangeConsumerTest(models.Model):
    _name = "edi.auto.exchange.consumer.test"
    _inherit = [
        "edi.auto.exchange.consumer.mixin",
    ]
    _description = _name

    name = fields.Char()
    state = fields.Char()
    number = fields.Integer()
    m2o = fields.Many2one("res.partner")
