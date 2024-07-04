# Copyright 2022 Camptocamp SA
# @author: Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from freezegun import freeze_time

from odoo.addons.component.tests.common import ComponentMixin

from .common import OrderMixin, XMLBaseTestCase, get_xml_handler


class TestOrderResponseOutbound(XMLBaseTestCase, OrderMixin, ComponentMixin):

    maxDiff = None

    _schema_path = "base_ubl:data/xsd-2.2/maindoc/UBL-OrderResponse-2.2.xsd"

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.setUpComponent()
        cls._setup_order()
        cls.exc_type_in = cls.env.ref("edi_sale_ubl_oca.demo_edi_exc_type_order_in")
        cls.exc_type_out = cls.env.ref(
            "edi_sale_ubl_oca.demo_edi_exc_type_order_response_out"
        )
        cls.exc_tmpl = cls.env.ref(
            "edi_sale_ubl_oca.demo_edi_exc_template_order_response_out"
        )
        vals = {
            "model": cls.sale._name,
            "res_id": cls.sale.id,
            "type_id": cls.exc_type_out.id,
        }
        cls.record = cls.backend.create_record(cls.exc_type_out.code, vals)
        cls.sale.origin_exchange_record_id = cls.record
        cls.sale.order_line.origin_exchange_record_id = cls.record
        cls.sale._edi_update_state()

    def setUp(self):
        super().setUp()
        ComponentMixin.setUp(self)
        self.sale.action_confirm()

    @classmethod
    def _get_backend(cls):
        return cls.env.ref("edi_ubl_oca.edi_backend_ubl_demo")

    def test_get_template(self):
        template = self.backend._get_output_template(self.record)
        self.assertEqual(template, self.exc_tmpl)
        self.assertEqual(
            template.template_id.key,
            "edi_sale_ubl_oca.qwb_tmpl_ubl_order_response_out",
        )

    def test_render_values(self):
        # TODO: test w/ some identifiers
        def make_party(record):
            return dict(
                name=record.name,
                identifiers=[],
                endpoint={},
            )

        values = self.exc_tmpl._get_render_values(self.record)
        expected = [
            ("seller_party", make_party(self.sale.company_id)),
            ("buyer_party", make_party(self.sale.partner_id)),
        ]
        for k, v in expected:
            self.assertEqual(values[k], v, f"{k} is wrong")

    @freeze_time("2022-07-28 10:30:00")
    def test_xml(self):
        self.record.action_exchange_generate()
        file_content = self.record._get_file_content()
        with open("/tmp/ordrsp.test.xml", "w") as ff:
            ff.write(file_content)
        handler = get_xml_handler(self.backend, self._schema_path)
        err = handler.validate(file_content)
        self.assertEqual(err, None, err)
        data = handler.parse_xml(file_content)
        # TODO: test all main data
        self.assertEqual(data["cbc:OrderResponseCode"], "CA")
