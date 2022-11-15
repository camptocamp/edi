# Copyright 2022 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import base64
from functools import partial

from odoo.tools import DotDict, file_open


def _as_base64(filename):
    path = f"product_import_ubl/tests/files/{filename}"
    with file_open(path, "rb") as fobj:
        data = fobj.read()
    return base64.b64encode(data)


def get_test_data(env):
    ref = env.ref
    return {
        "UBL-Catalogue_Example.xml": DotDict(
            {
                "_as_base64": partial(_as_base64, "UBL-Catalogue_Example.xml"),
                "products": [
                    {
                        "name": "Copy paper",
                        "code": "MNTR011",
                        "description": "Photo copy paper 80g A4, package of 500 sheets.",
                        "uom": ref("uom.product_uom_lb"),
                        "currency": ref("base.EUR"),
                        "min_qty": 1.0,
                        "price": 10.0,
                    },
                    {
                        "name": "Copy paper",
                        "code": "MNTR012",
                        "description": (
                            "Photo copy paper 80g A4, carton of 10 units "
                            "with 500 sheets each"
                        ),
                        "uom": ref("uom.product_uom_unit"),
                        "currency": ref("base.EUR"),
                        "min_qty": 0.0,
                        "price": 90.0,
                    },
                ],
            }
        ),
    }
