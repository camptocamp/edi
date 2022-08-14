# Copyright 2022 Camptocamp SA
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

{
    "name": "EDI Sales",
    "summary": """
        Configuration and special behaviors for EDI on sales.
    """,
    "version": "14.0.1.0.0",
    "license": "LGPL-3",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi",
    "depends": [
        "edi_oca",
        "edi_exchange_type_auto",
        "sale_order_import",
    ],
    "data": [
        "data/job_function.xml",
        "views/res_partner.xml",
        "views/sale_order.xml",
        "views/edi_exchange_record.xml",
        "templates/exchange_chatter_msg.xml",
    ],
}
