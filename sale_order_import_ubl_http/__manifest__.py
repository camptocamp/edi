# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

{
    "name": "Sale Order Import Http",
    "version": "13.0.1.0.1",
    "category": "Sales Management",
    "license": "AGPL-3",
    "summary": "Add an HTTP endpoint to import UBL formatted orders"
    "automatically as sales order",
    "author": "Camptocamp,Odoo Community Association (OCA)",
    "website": "https://github.com/oca/edi",
    "depends": ["auth_api_key", "queue_job", "sale_order_import_ubl"],
    "data": [
        "data/res_users.xml",
        "data/queue_job_channel.xml",
        "data/queue_job_function.xml",
        "data/res_users.xml",
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "wizard/sale_order_import_reschedule_wiz.xml",
        "views/res_config_settings.xml",
        "views/sale_order_ubl_import_file_view.xml",
    ],
    "installable": True,
}
