# Copyright 2026 Camptocamp SA (https://camptocamp.com/)

from openupgradelib import openupgrade


@openupgrade.migrate()
def migrate(env, version):
    """Migrate order response menu, action and form view XMLIDs"""
    openupgrade.rename_xmlids(
        env.cr,
        [
            (
                "purchase_order_import.order_response_import_form",
                "purchase_order_import.purchase_order_response_import_form",
            ),
            (
                "purchase_order_import.order_response_import_action",
                "purchase_order_import.purchase_order_response_import_action",
            ),
            (
                "purchase_order_import.order_response_import_importer_menu",
                "purchase_order_import.purchase_order_response_import_importer_menu",
            ),
        ],
    )
