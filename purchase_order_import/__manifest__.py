# © 2016-2017 Akretion (Alexis de Lattre <alexis.delattre@akretion.com>)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

{
    "name": "Purchase Order Import",
    "version": "19.0.1.0.0",
    "category": "Purchase Management",
    "license": "AGPL-3",
    "summary": "Update RFQ via the import of quotations from suppliers",
    "author": "Akretion,Odoo Community Association (OCA)",
    "website": "https://github.com/OCA/edi",
    "depends": [
        # Odoo/core
        "purchase_stock",
        # OCA/edi
        "base_business_document_import",
        # OCA/server-tools
        "onchange_helper",
        # OCA/reporting-engine
        "pdf_xml_attachment",
    ],
    "data": [
        # Security
        "security/ir.model.access.csv",
        # Wizard
        "wizard/order_response_import_wizard_view.xml",
        "wizard/purchase_order_import_wizard_view.xml",
        # Views
        "views/purchase_order.xml",
    ],
    "installable": True,
}
