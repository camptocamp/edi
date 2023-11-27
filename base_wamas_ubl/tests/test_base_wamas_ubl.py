# Copyright 2023 Jacques-Etienne Baudoux (BCIM) <je@bcim.be>
# Copyright 2023 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from difflib import SequenceMatcher

from freezegun import freeze_time

from odoo.tests.common import TransactionCase
from odoo.tools import file_open

from odoo.addons.account.tests.common import AccountTestInvoicingCommon


class TestBaseWamas(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.base_wamas_ubl = cls.env["base.wamas.ubl"]
        cls.assertXmlTreeEqual = AccountTestInvoicingCommon.assertXmlTreeEqual
        cls.get_xml_tree_from_string = (
            AccountTestInvoicingCommon.get_xml_tree_from_string
        )
        cls._turn_node_as_dict_hierarchy = (
            AccountTestInvoicingCommon._turn_node_as_dict_hierarchy
        )
        cls.partner_1 = cls.env.ref("base.res_partner_1")
        cls.partner_2 = cls.env.ref("base.res_partner_2")
        cls.extra_data = {
            "DespatchSupplierParty": {
                "CustomerAssignedAccountID": cls.partner_1.commercial_partner_id.ref
                or "",
                "PartyName": cls.partner_1.commercial_partner_id.name or "",
                "StreetName": cls.partner_1.commercial_partner_id.street or "",
                "CityName": cls.partner_1.commercial_partner_id.city or "",
                "PostalZone": cls.partner_1.commercial_partner_id.zip or "",
                "Country.IdentificationCode": cls.partner_1.commercial_partner_id.country_id.code
                or "",
                "CompanyID": cls.partner_1.commercial_partner_id.vat or "",
                "TaxScheme.ID": "",
                "TaxScheme.TaxTypeCode": "",
                "Contact.Name": cls.partner_1.child_ids
                and cls.partner_1.child_ids[0].name
                or "",
                "Contact.Telephone": cls.partner_1.child_ids
                and cls.partner_1.child_ids[0].phone
                or "",
                "Contact.ElectronicMail": cls.partner_1.child_ids
                and cls.partner_1.child_ids[0].email
                or "",
            },
            "DeliveryCustomerParty": {
                "PartyName": cls.partner_2.commercial_partner_id.name or "",
                "StreetName": cls.partner_2.commercial_partner_id.street or "",
                "CityName": cls.partner_2.commercial_partner_id.city or "",
                "PostalZone": cls.partner_2.commercial_partner_id.zip or "",
                "CountrySubentity": cls.partner_2.commercial_partner_id.state_id.name
                or "",
                "Country.IdentificationCode": cls.partner_2.commercial_partner_id.country_id.code
                or "",
                "CompanyID": cls.partner_2.commercial_partner_id.vat or "",
                "TaxScheme.ID": "",
                "TaxScheme.TaxTypeCode": "",
                "Contact.Name": cls.partner_2.child_ids
                and cls.partner_2.child_ids[0].name
                or "",
                "Contact.Telephone": cls.partner_2.child_ids
                and cls.partner_2.child_ids[0].phone
                or "",
                "Contact.Telefax": "",
                "Contact.ElectronicMail": cls.partner_2.child_ids
                and cls.partner_2.child_ids[0].email
                or "",
            },
        }

    def _is_string_similar(self, s1, s2, threshold=0.9):
        return SequenceMatcher(a=s1, b=s2).ratio() > threshold

    @freeze_time("2023-05-01")
    def _convert_wamas2ubl(self, input_file, expected_output_files):
        str_input = file_open(input_file, "r").read()
        outputs = self.base_wamas_ubl.parse_wamas2ubl(str_input, self.extra_data)

        for i, output in enumerate(outputs):
            output_tree = self.get_xml_tree_from_string(output)
            expected_output = file_open(expected_output_files[i], "r").read()
            expected_output_tree = self.get_xml_tree_from_string(expected_output)
            self.assertXmlTreeEqual(output_tree, expected_output_tree)

    @freeze_time("2023-05-01")
    def _convert_ubl2wamas(self, input_file, expected_output_file, telegram_type):
        str_input = file_open(input_file, "r").read()
        output = self.base_wamas_ubl.parse_ubl2wamas(str_input, telegram_type)
        expected_output = file_open(expected_output_file, "r").read()
        self.assertTrue(self._is_string_similar(output, expected_output))

    def test_convert_wamas2ubl(self):
        dict_data = {
            "wamas2ubl": {
                "picking": [
                    {
                        "input_file": "base_wamas_ubl/tests/files/"
                        "WAMAS2UBL-SAMPLE_AUSKQ_WATEKQ_WATEPQ.wamas",
                        "lst_expected_output": [
                            "base_wamas_ubl/tests/files/"
                            "WAMAS2UBL-SAMPLE_AUSKQ_WATEKQ_WATEPQ-DESPATCH_ADVICE.xml"
                        ],
                    },
                ],
                "reception": [
                    {
                        "input_file": "base_wamas_ubl/tests/files/"
                        "WAMAS2UBL-SAMPLE_WEAKQ_WEAPQ.wamas",
                        "lst_expected_output": [
                            "base_wamas_ubl/tests/files/"
                            "WAMAS2UBL-SAMPLE_WEAKQ_WEAPQ-DESPATCH_ADVICE.xml"
                        ],
                    },
                    {
                        "input_file": "base_wamas_ubl/tests/files/"
                        "WAMAS2UBL-SAMPLE_KRETKQ_KRETPQ.wamas",
                        "lst_expected_output": [
                            "base_wamas_ubl/tests/files/"
                            "WAMAS2UBL-SAMPLE_KRETKQ_KRETPQ-DESPATCH_ADVICE.xml",
                            "base_wamas_ubl/tests/files/"
                            "WAMAS2UBL-SAMPLE_KRETKQ_KRETPQ-DESPATCH_ADVICE-2.xml",
                        ],
                    },
                ],
            },
            "ubl2wamas": {
                "picking": [
                    {
                        "input_file": "base_wamas_ubl/tests/files/"
                        "UBL2WAMAS-SAMPLE_AUSK_AUSP-DESPATCH_ADVICE.xml",
                        "expected_output": "base_wamas_ubl/tests/files/"
                        "UBL2WAMAS-SAMPLE_AUSK_AUSP.wamas",
                        "type": "AUSK,AUSP",
                    },
                ],
                "reception": [
                    {
                        "input_file": "base_wamas_ubl/tests/files/"
                        "UBL2WAMAS-SAMPLE_WEAK_WEAP-DESPATCH_ADVICE.xml",
                        "expected_output": "base_wamas_ubl/tests/files/"
                        "UBL2WAMAS-SAMPLE_WEAK_WEAP.wamas",
                        "type": "WEAK,WEAP",
                    },
                    {
                        "input_file": "base_wamas_ubl/tests/files/"
                        "UBL2WAMAS-SAMPLE_KRETK_KRETP-DESPATCH_ADVICE.xml",
                        "expected_output": "base_wamas_ubl/tests/files/"
                        "UBL2WAMAS-SAMPLE_KRETK_KRETP.wamas",
                        "type": "KRETK,KRETP",
                    },
                ],
            },
        }

        # ==== wamas2ubl ====
        # picking
        for data in dict_data["wamas2ubl"]["picking"]:
            self._convert_wamas2ubl(data["input_file"], data["lst_expected_output"])

        # reception
        for data in dict_data["wamas2ubl"]["reception"]:
            self._convert_wamas2ubl(data["input_file"], data["lst_expected_output"])

        # ==== ubl2wamas ====
        # picking
        for data in dict_data["ubl2wamas"]["picking"]:
            self._convert_ubl2wamas(
                data["input_file"], data["expected_output"], data["type"]
            )

        # reception
        for data in dict_data["ubl2wamas"]["reception"]:
            self._convert_ubl2wamas(
                data["input_file"], data["expected_output"], data["type"]
            )
