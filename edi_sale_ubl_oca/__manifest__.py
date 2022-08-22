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
        "sale_order_import_ubl",
        "edi_xml_oca",
        "edi_exchange_template_oca",
        "edi_ubl_oca",
    ],
    "data": [
        "templates/qweb_tmpl_party.xml",
        "templates/qweb_tmpl_order_response.xml",
        "data/edi_exchange_type.xml",
        "data/exc_templ_order_response.xml",
    ],
}
