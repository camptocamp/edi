# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
import base64

import mock

from odoo.addons.edi_oca.tests.common import EDIBackendCommonComponentTestCase

MOCK_PATH = "odoo.addons.webservice.models.webservice_backend.WebserviceBackend"


class TestEDIWebserviceBase(EDIBackendCommonComponentTestCase):
    @classmethod
    def _get_backend(cls):
        return cls.env.ref("edi_webservice_oca.demo_edi_backend")

    @classmethod
    def _setup_records(cls):
        super()._setup_records()
        cls.filedata = base64.b64encode(b"This is a simple file")
        vals = {
            "model": cls.partner._name,
            "res_id": cls.partner.id,
            "exchange_file": cls.filedata,
        }
        cls.record = cls.backend.create_record("test_csv_output", vals)
        cls.sender = cls.backend._find_component(
            cls.partner._name,
            ["webservice.send"],
            work_ctx={"exchange_record": cls.record},
        )

    def _mock_ws_call(self):
        return mock.patch(MOCK_PATH + ".call")
