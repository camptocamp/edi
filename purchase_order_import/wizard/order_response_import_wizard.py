# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

import logging
import mimetypes
from base64 import b64decode, b64encode
from typing import Any

from lxml import etree

from odoo import api, fields, models
from odoo.exceptions import UserError, ValidationError
from odoo.fields import Domain

logger = logging.getLogger(__name__)


class OrderResponseImportWizard(models.TransientModel):
    _name = "order.response.import.wizard"
    _description = "Purchase Order Response Import from Files"

    document = fields.Binary(
        string="XML or PDF Order response",
        required=True,
        help="Upload an Order response file that you received from "
        "your supplier. Supported formats: XML and PDF "
        "(PDF with an embeded XML file).",
    )
    filename = fields.Char()

    @api.model
    def parse_xml_order_document(self, xml_root: etree._Element) -> dict[str, Any]:
        """Parse an XML order response document.

        The hook method to be implemented by other modules supporting
        specific XML formats. It should return the parsed document in a
        normalized dictionary format.
        """
        raise UserError(
            self.env._(
                "This type of XML Order Response is not supported. Did you "
                "install the module to support this XML format?"
            )
        )

    @api.model
    def parse_pdf_order_document(self, document: bytes) -> dict[str, Any]:
        """Get PDF attachments, filter on XML files and call import_order_xml."""
        xml_files_dict = self.env["pdf.xml.tool"].pdf_get_xml_files(document)
        if not xml_files_dict:
            raise UserError(
                self.env._("There are no embedded XML files in this PDF file.")
            )
        for xml_filename, xml_root in xml_files_dict.items():
            logger.info("Trying to parse XML file %s", xml_filename)
            try:
                return self.parse_xml_order_document(xml_root)
            except UserError:
                continue
        raise UserError(
            self.env._(
                "This type of XML Order Document is not supported. Did you "
                "install the module to support this XML format?"
            )
        )

    # Format of parsed order response
    # {
    # 'ref': 'SO01234' # the buyer party identifier
    #                  # (specified into the Order document -> po's name)
    # 'supplier': {'vat': 'FR25499247138'},
    # 'company': {'vat': 'FR12123456789'}, # Only used to check we are not
    #                                      # importing the quote in the
    #                                      # wrong company by mistake
    # 'status': 'acknowledgement | accepted | rejected |
    #            conditionally_accepted'
    # 'currency': {'iso': 'EUR', 'symbol': u'€'},
    # 'note': 'some notes',
    # 'chatter_msg': ['msg1', 'msg2']
    # 'lines': [{
    #           'id': 123456,
    #           'qty': 2.5,
    #           'uom': {'unece_code': 'C62'},
    #           'status': 5,
    #           'note': 'my note'
    #           'backorder_qty: None  # if provided and qty != expected
    #                                 # the backorder qty will be delivered
    #                                 # in a next shipping
    #    }]

    @api.model
    def parse_order_response(self, document: bytes, filename: str) -> dict[str, Any]:
        """Parse an uploaded order response file into normalized import data."""
        if not document:
            raise UserError(self.env._("Missing document file."))
        if not filename:
            raise UserError(self.env._("Missing document filename."))
        filetype = mimetypes.guess_type(filename)[0]
        logger.debug("OrderResponse file mimetype: %s", filetype)
        if filetype in ["application/xml", "text/xml"]:
            try:
                xml_root = etree.fromstring(document)
            except etree.XMLSyntaxError as e:
                logger.exception("File is not XML-compliant")
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
            parsed_order_document = self.parse_xml_order_document(xml_root)
        elif filetype == "application/pdf":
            parsed_order_document = self.parse_pdf_order_document(document)
        else:
            raise UserError(
                self.env._(
                    "This file '%(filename)s' is not recognised as XML nor PDF file. "
                    "Please check the file and it's extension.",
                    filename=filename,
                )
            )
        logger.debug("Result of OrderResponse parsing: %s", parsed_order_document)
        if "attachments" not in parsed_order_document:
            parsed_order_document["attachments"] = {}
        parsed_order_document["attachments"][filename] = b64encode(document).decode()
        if "chatter_msg" not in parsed_order_document:
            parsed_order_document["chatter_msg"] = []
        if parsed_order_document.get("company") and not self.env.context.get(
            "edi_skip_company_check"
        ):
            self.env["business.document.import"]._check_company(
                parsed_order_document["company"],
                parsed_order_document["chatter_msg"],
            )
        return parsed_order_document

    def process_document(self) -> dict[str, Any]:
        """Process the uploaded document from the import wizard."""
        self.ensure_one()
        parsed_order_document = self.parse_order_response(
            b64decode(self.document), self.filename
        )
        return self.process_data(parsed_order_document)

    @api.model
    def process_data(self, parsed_order_document: dict[str, Any]) -> dict[str, Any]:
        """Apply parsed order response data to its matching purchase order."""
        bdio = self.env["business.document.import"]
        po_name = parsed_order_document.get("ref")
        order = self.env["purchase.order"].search([Domain("name", "=", po_name)])
        if not order:
            bdio.user_error_wrap(
                "process_data",
                parsed_order_document,
                self.env._(
                    "No purchase order found for name %(po_name)s.",
                    po_name=po_name,
                ),
                parsed_order_document["chatter_msg"],
                True,
            )

        currency = bdio._match_currency(
            parsed_order_document.get("currency"),
            parsed_order_document["chatter_msg"],
        )
        partner = bdio._match_partner(
            parsed_order_document["supplier"],
            parsed_order_document["chatter_msg"],
            partner_type="supplier",
        )
        if partner.commercial_partner_id != order.partner_id.commercial_partner_id:
            bdio.user_error_wrap(
                "process_data",
                parsed_order_document,
                self.env._(
                    "The supplier of the imported OrderResponse (%(supplier)s) "
                    "is different from the supplier of the purchase order "
                    "(%(order_supplier)s).",
                    supplier=partner.commercial_partner_id.name,
                    order_supplier=order.partner_id.commercial_partner_id.name,
                ),
                parsed_order_document["chatter_msg"],
                True,
            )
        if currency and currency != order.currency_id:
            bdio.user_error_wrap(
                "process_data",
                parsed_order_document,
                self.env._(
                    "The currency of the imported OrderResponse (%(currency)s) "
                    "is different from the currency of the purchase order "
                    "(%(order_currency)s).",
                    currency=currency.name,
                    order_currency=order.currency_id.name,
                ),
                parsed_order_document["chatter_msg"],
                True,
            )

        status = parsed_order_document.get("status")
        if status == "acknowledgement":
            self._process_ack(order, parsed_order_document)
        elif status == "rejected":
            self._process_rejected(order, parsed_order_document)
        elif status == "accepted":
            self._process_accepted(order, parsed_order_document)
        elif status == "conditionally_accepted":
            self._process_conditional(order, parsed_order_document)
        else:
            bdio.user_error_wrap(
                "process_data",
                parsed_order_document,
                self.env._("Unknown status '%(status)s'.", status=status),
                parsed_order_document["chatter_msg"],
                True,
            )

        bdio.post_create_or_update(parsed_order_document, order)
        logger.info(
            "purchase.order ID %d updated via import of file %s.",
            order.id,
            self.filename,
        )
        order.message_post(
            body=self.env._(
                "This purchase order has been updated automatically via the import "
                "of OrderResponse file %(filename)s.",
                filename=self.filename,
            )
        )
        return order.get_formview_action()

    @api.model
    def _process_ack(
        self, purchase_order: models.Model, parsed_order_document: dict[str, Any]
    ):
        """Store the supplier acknowledgement date on the purchase order."""
        if not purchase_order.supplier_ack_dt:
            purchase_order.supplier_ack_dt = fields.Datetime.now()

    @api.model
    def _process_rejected(
        self, purchase_order: models.Model, parsed_order_document: dict[str, Any]
    ):
        """Cancel the purchase order rejected by the supplier."""
        parsed_order_document["chatter_msg"] = (
            parsed_order_document["chatter_msg"] or []
        )
        parsed_order_document["chatter_msg"].append(
            self.env._("PO cancelled by the supplier.")
        )
        purchase_order.button_cancel()

    @api.model
    def _process_accepted(
        self, purchase_order: models.Model, parsed_order_document: dict[str, Any]
    ):
        """Confirm the purchase order accepted by the supplier."""
        parsed_order_document["chatter_msg"] = (
            parsed_order_document["chatter_msg"] or []
        )
        parsed_order_document["chatter_msg"].append(
            self.env._("PO confirmed by the supplier.")
        )
        purchase_order.button_approve()

    @api.model
    def _process_conditional(
        self, purchase_order: models.Model, parsed_order_document: dict[str, Any]
    ):
        """Confirm an amended order response and synchronize receipt moves.

        A conditional supplier acceptance must describe every PO line. Accepted
        lines keep their receipt move, rejected lines cancel it, and amended
        lines split the receipt between accepted, backordered, and cancelled
        quantities according to the supplier response.
        """
        chatter = parsed_order_document["chatter_msg"] = (
            parsed_order_document["chatter_msg"] or []
        )
        chatter.append(self.env._("PO confirmed with amendment by the supplier."))
        lines = parsed_order_document["lines"]
        try:
            line_ids = {int(line["line_id"]) for line in lines}
        except (KeyError, TypeError, ValueError):
            line_ids = set()
        if line_ids != set(purchase_order.order_line.ids):
            self.env["business.document.import"].user_error_wrap(
                "_process_conditional",
                parsed_order_document,
                self.env._(
                    "Unable to conditionally confirm the purchase order. \n"
                    "Line IDS into the parsed document differs from the "
                    "expected list of order line ids: \n "
                    "received: %(received_line_ids)s\n"
                    "expected: %(expected_line_ids)s\n",
                    received_line_ids=[line.get("line_id") for line in lines],
                    expected_line_ids=purchase_order.order_line.ids,
                ),
                chatter,
                True,
            )
            return
        purchase_order.button_approve()
        # apply changes to the created moves...
        lines_by_id = {int(line["line_id"]): line for line in lines}
        for order_line in purchase_order.order_line:
            line_info = lines_by_id[order_line.id]
            note = line_info.get("note")
            move = order_line.move_ids.filtered(
                lambda x: x.state not in ("cancel", "done")
            )
            if len(move) != 1:
                self.env["business.document.import"].user_error_wrap(
                    "_process_conditional",
                    parsed_order_document,
                    self.env._(
                        "More than one move found for PO line.\n"
                        "Move IDs: %(move_ids)s\n"
                        "Line Info: %(line_info)s",
                        move_ids=move.ids,
                        line_info=line_info,
                    ),
                    chatter,
                    True,
                )
            if note:
                move.write({"description_picking": note})
            status = line_info["status"]
            if status == "accepted":
                continue
            if status == "rejected":
                order_line.move_ids._action_cancel()
            elif status == "amend":
                qty = line_info["qty"]
                backorder_qty = line_info["backorder_qty"]
                move_qty = move.product_qty
                if move.product_uom.compare(qty, move_qty) < 0:
                    self._check_picking_status(move.picking_id)
                    new_move = self._split_move(move, move_qty - qty)
                    to_cancel = None
                    if backorder_qty:
                        note = note + "\n" if note else ""
                        note += self.env._(
                            "%(qty)s items should be delivered into a next delivery.",
                            qty=backorder_qty,
                        )
                        move.description_picking = note
                        # if the backorder qty is < than the remaining qty
                        # split and cancel the qty that will not be delivered
                        if (
                            new_move.product_uom.compare(
                                backorder_qty, new_move.product_qty
                            )
                            < 0
                        ):
                            to_cancel = self._split_move(
                                new_move, new_move.product_qty - backorder_qty
                            )
                    else:
                        to_cancel = new_move
                    if to_cancel:
                        to_cancel._action_cancel()
                        to_cancel.write(
                            {
                                "description_picking": self.env._(
                                    "No backorder planned by the supplier."
                                )
                            }
                        )
                    if new_move.state != "cancel":
                        # move the new move into an backorder picking to avoid
                        # that the scheduler merge the two moves into the same
                        # pack operation
                        self._add_move_to_backorder(new_move)

                    move.picking_id.action_assign()

    @api.model
    def _split_move(self, move: models.Model, qty: float) -> models.Model:
        """Split a stock move and create the new move with modern stock APIs."""
        new_move_vals = move._split(qty)
        new_move = self.env["stock.move"].create(new_move_vals)
        new_move._action_confirm(merge=False, create_proc=False)
        return new_move

    @api.model
    def _add_move_to_backorder(self, move: models.Model):
        """Move a split stock move to the receipt backorder."""
        StockPicking = self.env["stock.picking"]
        current_picking = move.picking_id
        backorder = StockPicking.search(
            [Domain("backorder_id", "=", current_picking.id)]
        )
        if not backorder:
            date_done = current_picking.date_done
            move.picking_id._create_backorder(backorder_moves=move)
            # preserve date_done....
            current_picking.date_done = date_done
        else:
            move.write({"picking_id": backorder.id})
            backorder.action_confirm()
            backorder.action_assign()

    @api.model
    def _check_picking_status(self, picking: models.Model):
        """Block amendments when receipt operations have already started."""
        if any(move_line.picked for move_line in picking.move_line_ids):
            raise ValidationError(
                self.env._(
                    "Some operations have already started! "
                    "Please validate or reset operations on "
                    "picking %(picking)s to ensure delivery slip to be computed.",
                    picking=picking.name,
                )
            )
