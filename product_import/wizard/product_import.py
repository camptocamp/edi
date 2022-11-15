# Copyright 2022 Camptocamp
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

import logging
import mimetypes
from base64 import b64decode, b64encode
from datetime import date, timedelta

from lxml import etree

from odoo import _, api, fields, models
from odoo.exceptions import UserError

logger = logging.getLogger(__name__)


class ProductImport(models.TransientModel):
    _name = "product.import"
    _description = "Product import from files"

    product_file = fields.Binary(
        string="Product Catalogue",
        required=True,
        help="Upload a Product Catalogue",
    )
    product_filename = fields.Char(string="Filename")

    @property
    def _bdimport(self):
        return self.env["business.document.import"]

    @api.onchange("product_file")
    def product_file_change(self):
        if not self.product_filename or not self.product_file:
            return

        doc_type = self._parse_file(
            self.product_filename, b64decode(self.product_file), detect_doc_type=True
        )
        if doc_type is None:
            return {"warning": self._unsupported_file_msg(self.product_filename)}

    def _parse_file(self, filename, filecontent, detect_doc_type=False):
        assert filename, "Missing filename"
        assert filecontent, "Missing file content"
        filetype = mimetypes.guess_type(filename)
        logger.debug("File mimetype: %s", filetype)
        mimetype = filetype[0]
        supported_types = {
            "CSV": ("text/csv", "text/plain"),
            "XML": ("application/xml", "text/xml"),
        }
        if mimetype in supported_types["CSV"]:
            res = "CSV"
        elif mimetype in supported_types["XML"]:
            xml_root, error_msg = self._parse_xml(filecontent)
            if error_msg:
                raise UserError(error_msg)
            res = self.parse_xml_catalogue(xml_root, detect_doc_type=detect_doc_type)
        else:
            res = None
        return res

    def _unsupported_file_msg(self, filename):
        return {
            "title": _("Unsupported file format"),
            "message": _(
                "This file '%s' is not recognised as a CSV nor XML file. "
                "Please check the file and its extension."
            )
            % filename,
        }

    @api.model
    def _parse_xml(self, data):
        xml_root = error_msg = None
        if data:
            try:
                xml_root = etree.fromstring(data)
            except etree.XMLSyntaxError:
                error_msg = _("This XML file is not XML-compliant")
        else:
            error_msg = _("No data provided")
        if not error_msg:
            try:
                self.parse_xml_catalogue(xml_root, detect_doc_type=True)
            except (UserError, NotImplementedError):
                error_msg = _("Unsupported XML document")
        return xml_root, error_msg

    @api.model
    def parse_xml_catalogue(self, xml_root, detect_doc_type=False):
        raise NotImplementedError(
            _(
                "This file is not supported. Did you install "
                "the module to support this XML format?"
            )
        )

    @api.model
    def parse_product_catalogue(self, product_file, product_filename):
        catalogue = self._parse_file(product_filename, product_file)
        # logger.debug("Result of catalogue parsing: %s", catalogue)
        if "attachments" not in catalogue:
            catalogue["attachments"] = {}
        if "chatter_msg" not in catalogue:
            catalogue["chatter_msg"] = []
        catalogue["attachments"][product_filename] = b64encode(product_file)
        return catalogue

    @api.model
    def _prepare_supplierinfo(self, seller_info, product):
        today = date.today()
        yesterday = today - timedelta(days=1)
        seller_id = False
        result = []
        if product:
            # Terminate previous prices
            for s_info in product.seller_ids:
                if s_info.name.id != seller_info["name"]:
                    continue
                if s_info.date_end and s_info.date_end < today:
                    continue
                if (
                    s_info.min_qty == seller_info["min_qty"]
                    and s_info.price == seller_info["price"]
                    and s_info.currency_id.id == seller_info["currency_id"]
                ):
                    seller_id = s_info.id
                else:
                    result.append((1, s_info.id, {"date_end": yesterday}))
        if not seller_id:
            seller_info.setdefault("date_start", today)
            result.append((0, 0, seller_info))
        return result

    @api.model
    def _prepare_product(self, parsed_product, chatter_msg, seller=None):
        try:
            product = self._bdimport._match_product(
                parsed_product, chatter_msg, seller=seller
            )
        except UserError:
            product = None
        uom = self._bdimport._match_uom(parsed_product["uom"], chatter_msg)
        currency = self._bdimport._match_currency(
            parsed_product["currency"], chatter_msg
        )

        product_vals = {
            "default_code": parsed_product["code"],
            "barcode": parsed_product["barcode"],
            "name": parsed_product["name"],
            "description": parsed_product["description"],
            "uom_id": uom.id,
            "uom_po_id": uom.id,
        }
        seller_info = {
            "name": seller and seller.id or False,
            "price": parsed_product["price"],
            "currency_id": currency.id,
            "min_qty": parsed_product["min_qty"],
        }
        product_vals["seller_ids"] = self._prepare_supplierinfo(seller_info, product)
        if product:
            product_vals["recordset"] = product

        return product_vals

    @api.model
    def create_product(self, parsed_product, chatter_msg, seller=None, filename=None):
        product_vals = self._prepare_product(parsed_product, chatter_msg, seller=seller)
        product = product_vals.pop("recordset", None)
        if product:
            product.write(product_vals)
            logger.info("Product %d updated", product.id)
        else:
            product = self.env["product.product"].create(product_vals)
            logger.info("Product %d created", product.id)
        return product

    def import_button(self):
        self.ensure_one()
        file_content = b64decode(self.product_file)
        catalogue = self.parse_product_catalogue(file_content, self.product_filename)
        seller = self._bdimport._match_partner(
            catalogue["seller"], catalogue["chatter_msg"], partner_type="supplier"
        )
        if not catalogue.get("products"):
            raise UserError(_("This catalogue doesn't have any product!"))
        for product in catalogue.get("products"):
            self.create_product(
                product,
                catalogue["chatter_msg"],
                seller=seller,
                filename=self.product_filename,
            )
        self._bdimport.post_create_or_update(
            catalogue, seller, doc_filename=self.product_filename
        )
        logger.info("Products updated for vendor %d", seller.id)
        return {"type": "ir.actions.act_window_close"}
