# Copyright 2016-2018 Akretion France (http://www.akretion.com/)
# @author: Alexis de Lattre <alexis.delattre@akretion.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import mimetypes
from base64 import b64decode, b64encode
from typing import Any

from lxml import etree

from odoo import api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class PurchaseOrderImportWizard(models.TransientModel):
    _name = "purchase.order.import.wizard"
    _description = "Purchase Order Import from Files"

    @api.model
    def _get_purchase_id(self) -> models.Model:
        """Return the active purchase order selected for quotation import."""
        assert self.env.context["active_model"] == "purchase.order", "bad active_model"
        return self.env["purchase.order"].browse(self.env.context["active_id"])

    quote_file = fields.Binary(
        string="XML or PDF Quotation",
        required=True,
        help="Upload a quotation file that you received from "
        "your supplier. Supported formats: XML and PDF "
        "(PDF with an embeded XML file).",
    )
    quote_filename = fields.Char(string="Filename")
    update_option = fields.Selection(
        [
            ("price", "Price"),
            ("all", "Price and Quantity"),
        ],
        default="price",
        required=True,
    )
    purchase_id = fields.Many2one(
        "purchase.order",
        string="RFQ to Update",
        default=lambda self: self._get_purchase_id(),
        readonly=True,
    )

    @api.model
    def parse_xml_quote(self, xml_root: etree._Element) -> dict[str, Any]:
        """Parse an XML quotation document.

        The hook method to be implemented by other modules supporting
        specific XML formats. It should return the parsed quotation in a
        normalized dictionary format.
        """
        raise UserError(
            self.env._(
                "This type of XML quotation is not supported. Did you install "
                "the module to support this XML format?"
            )
        )

    @api.model
    def parse_pdf_quote(self, quote_file: bytes) -> dict[str, Any]:
        """Parse the first supported XML attachment embedded in a PDF."""
        xml_files_dict = self.env["pdf.xml.tool"].pdf_get_xml_files(quote_file)
        if not xml_files_dict:
            raise UserError(
                self.env._("There are no embedded XML files in this PDF file.")
            )
        for xml_filename, xml_root in xml_files_dict.items():
            logger.info("Trying to parse XML file %s", xml_filename)
            try:
                return self.parse_xml_quote(xml_root)
            except UserError:
                continue
        raise UserError(
            self.env._(
                "This type of XML quotation is not supported. Did you install "
                "the module to support this XML format?"
            )
        )

    # Format of parsed_quote
    # {
    # 'partner': {
    #     'vat': 'FR25499247138',
    #     'name': 'Camptocamp',
    #     'email': 'luc@camptocamp.com',
    #     },
    # 'company': {'vat': 'FR12123456789'}, # Only used to check we are not
    #                                      # importing the quote in the
    #                                      # wrong company by mistake
    # 'currency': {'iso': 'EUR', 'symbol': u'€'},
    # 'incoterm': 'EXW',
    # 'note': 'some notes',
    # 'chatter_msg': ['msg1', 'msg2']
    # 'lines': [{
    #           'product': {
    #                'code': 'EA7821',
    #                'ean13': '2100002000003',
    #                },
    #           'qty': 2.5,
    #           'uom': {'unece_code': 'C62'},
    #           'price_unit': 12.42,  # without taxes
    #    }]

    @api.model
    def parse_quote(self, quote_file: bytes, quote_filename: str) -> dict[str, Any]:
        """Parse an uploaded quotation file into normalized import data."""
        if not quote_file:
            raise UserError(self.env._("Missing quote file."))
        if not quote_filename:
            raise UserError(self.env._("Missing quote filename."))
        filetype = mimetypes.guess_type(quote_filename)[0]
        logger.debug("Quote file mimetype: %s", filetype)
        if filetype in ["application/xml", "text/xml"]:
            try:
                xml_root = etree.fromstring(quote_file)
            except etree.XMLSyntaxError as e:
                raise UserError(
                    self.env._("This XML file is not XML-compliant.")
                ) from e
            if logger.isEnabledFor(logging.DEBUG):
                pretty_xml_string = etree.tostring(
                    xml_root,
                    pretty_print=True,
                    encoding="UTF-8",
                    xml_declaration=True,
                )
                logger.debug("Starting to import the following XML file:")
                logger.debug(pretty_xml_string)
            parsed_quote = self.parse_xml_quote(xml_root)
        elif filetype == "application/pdf":
            parsed_quote = self.parse_pdf_quote(quote_file)
        else:
            raise UserError(
                self.env._(
                    "This file '%(filename)s' is not recognised as XML nor PDF file. "
                    "Please check the file and it's extension.",
                    filename=quote_filename,
                )
            )
        logger.debug("Result of quotation parsing: %s", parsed_quote)
        if "attachments" not in parsed_quote:
            parsed_quote["attachments"] = {}
        parsed_quote["attachments"][quote_filename] = b64encode(quote_file).decode()
        if "chatter_msg" not in parsed_quote:
            parsed_quote["chatter_msg"] = []
        if parsed_quote.get("company") and not self.env.context.get(
            "edi_skip_company_check"
        ):
            self.env["business.document.import"]._check_company(
                parsed_quote["company"], parsed_quote["chatter_msg"]
            )
        return parsed_quote

    @api.model
    def _prepare_update_order_vals(
        self, parsed_quote: dict[str, Any], order: models.Model
    ) -> dict[str, Any]:
        """Prepare purchase order values updated from the parsed quotation."""
        vals = {}
        incoterm = self.env["business.document.import"]._match_incoterm(
            parsed_quote.get("incoterm"), parsed_quote["chatter_msg"]
        )
        if incoterm and incoterm != order.incoterm_id:
            parsed_quote["chatter_msg"].append(
                self.env._(
                    "The incoterm has been updated from %(old_incoterm)s to "
                    "%(new_incoterm)s upon import of the quotation file "
                    "'%(filename)s'",
                    old_incoterm=order.incoterm_id.code,
                    new_incoterm=incoterm.code,
                    filename=self.quote_filename,
                )
            )
            vals["incoterm_id"] = incoterm.id
        return vals

    def update_order_lines(
        self, parsed_quote: dict[str, Any], order: models.Model
    ) -> bool:
        """Update RFQ lines from a parsed supplier quotation.

        The import compares matched products and keeps a conservative behavior:
        it updates existing prices, optionally updates quantities, adds missing
        quoted products, and only warns about RFQ lines absent from the quote.
        """
        polo = self.env["purchase.order.line"]
        chatter = parsed_quote["chatter_msg"]
        bdio = self.env["business.document.import"]
        existing_lines = []
        for oline in order.order_line:
            price_unit = 0.0
            if not oline.product_uom_id.is_zero(oline.product_qty):
                price_unit = oline.price_subtotal / float(oline.product_qty)
            existing_lines.append(
                {
                    "product": oline.product_id,
                    "name": oline.name,
                    "qty": oline.product_qty,
                    "uom": oline.product_uom_id,
                    "price_unit": price_unit,
                    "line": oline,
                }
            )

        compare_res = bdio.compare_lines(
            existing_lines,
            parsed_quote["lines"],
            chatter,
            seller=order.partner_id.commercial_partner_id,
        )

        update_option = self.update_option
        if not compare_res:
            return True
        for oline, cdict in compare_res["to_update"].items():
            write_vals = {}
            if cdict.get("price_unit"):
                chatter.append(
                    self.env._(
                        "The unit price has been updated on the RFQ line with "
                        "product '%(product)s' from %(old_price)s to "
                        "%(new_price)s %(currency)s.",
                        product=oline.product_id.display_name,
                        old_price=cdict["price_unit"][0],
                        new_price=cdict["price_unit"][1],
                        currency=order.currency_id.name,
                    )
                )
                write_vals["price_unit"] = cdict["price_unit"][1]  # TODO
            if update_option == "all" and cdict.get("qty"):
                chatter.append(
                    self.env._(
                        "The quantity has been updated on the RFQ line with "
                        "product '%(product)s' from %(old_qty)s to "
                        "%(new_qty)s %(uom)s.",
                        product=oline.product_id.display_name,
                        old_qty=cdict["qty"][0],
                        new_qty=cdict["qty"][1],
                        uom=oline.product_uom_id.name,
                    )
                )
                write_vals["product_qty"] = cdict["qty"][1]
            if write_vals:
                oline.write(write_vals)
        if compare_res["to_remove"]:  # we don't delete the lines, only warn
            warn_label = [
                f"{line.product_qty} {line.product_uom_id.name} x "
                f"{line.product_id.name}"
                for line in compare_res["to_remove"]
            ]
            chatter.append(
                self.env._(
                    "%(line_count)d order line(s) are not in the imported "
                    "quotation: %(lines)s",
                    line_count=len(compare_res["to_remove"]),
                    lines=", ".join(warn_label),
                )
            )
        if compare_res["to_add"]:
            to_create_label = []
            for add in compare_res["to_add"]:
                line_vals = self._prepare_create_order_line(
                    add["product"], add["uom"], add["import_line"], order
                )
                line_vals["order_id"] = order.id
                new_line = polo.create(line_vals)
                to_create_label.append(
                    f"{new_line.product_qty} {new_line.product_uom_id.name} x "
                    f"{new_line.name}"
                )
            chatter.append(
                self.env._(
                    "%(line_count)d new order line(s) created: %(lines)s",
                    line_count=len(compare_res["to_add"]),
                    lines=", ".join(to_create_label),
                )
            )
        return True

    @api.model
    def _prepare_create_order_line(
        self,
        product: models.Model,
        uom: models.Model,
        import_line: dict[str, Any],
        order: models.Model,
    ) -> dict[str, Any]:
        """Prepare a purchase order line for a quoted product missing on the RFQ."""
        polo = self.env["purchase.order.line"]
        vals = {
            "product_id": product.id,
            "order_id": order.id,
            "price_unit": import_line["price_unit"],
            "product_qty": import_line.get("qty") or 1.0,
            "product_uom_id": uom.id,
        }
        vals.update(polo.play_onchanges(vals, ["product_id"]))
        vals["product_qty"] = import_line.get("qty") or vals.get("product_qty") or 1.0
        vals["product_uom_id"] = uom.id
        vals.pop("order_id", None)
        return vals

    def update_rfq_button(self) -> bool:
        """Update the active RFQ from the uploaded quotation file."""
        self.ensure_one()
        bdio = self.env["business.document.import"]
        order = self.purchase_id
        assert order, "No link to PO"
        if not order:
            raise UserError(self.env._("You must select a quotation to update."))
        order.ensure_one()
        parsed_quote = self.parse_quote(b64decode(self.quote_file), self.quote_filename)
        currency = bdio._match_currency(
            parsed_quote.get("currency"), parsed_quote["chatter_msg"]
        )
        partner = bdio._match_partner(
            parsed_quote["partner"],
            parsed_quote["chatter_msg"],
            partner_type="supplier",
        )
        if partner.commercial_partner_id != order.partner_id.commercial_partner_id:
            raise UserError(
                self.env._(
                    "The supplier of the imported quotation (%(supplier)s) is "
                    "different from the supplier of the RFQ (%(order_supplier)s).",
                    supplier=partner.commercial_partner_id.name,
                    order_supplier=order.partner_id.commercial_partner_id.name,
                )
            )
        if currency != order.currency_id:
            raise UserError(
                self.env._(
                    "The currency of the imported quotation (%(currency)s) is "
                    "different from the currency of the RFQ (%(order_currency)s)",
                    currency=currency.name,
                    order_currency=order.currency_id.name,
                )
            )
        vals = self._prepare_update_order_vals(parsed_quote, order)
        if vals:
            order.write(vals)
        if not parsed_quote.get("lines"):
            raise UserError(self.env._("This quotation doesn't have any line."))
        self.update_order_lines(parsed_quote, order)
        bdio.post_create_or_update(parsed_quote, order)
        logger.info(
            "purchase.order ID %d updated via import of file %s",
            order.id,
            self.quote_filename,
        )
        order.message_post(
            body=self.env._(
                "This RFQ has been updated automatically via the import of "
                "quotation file %(filename)s",
                filename=self.quote_filename,
            )
        )
        return True
