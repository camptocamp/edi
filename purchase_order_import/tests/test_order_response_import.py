# Copyright 2020 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo.exceptions import UserError

from .common import TestOrderResponseImportCommon


class TestOrderResponseImportWizard(TestOrderResponseImportCommon):
    def test_unknown_purchase_order_reference(self):
        """Raise an error when no purchase order matches the response reference."""
        data = self._get_base_data(ref="123456")
        with self.assertRaisesRegex(
            UserError,
            "No purchase order found for name 123456.",
        ):
            self.OrderResponseImport.process_data(data)

    def test_unknown_status(self):
        """Raise an error when the response status is not supported."""
        data = self._get_base_data(status="unknown")
        with self.assertRaisesRegex(UserError, "Unknown status 'unknown'."):
            self.OrderResponseImport.process_data(data)

    def test_different_currency(self):
        """Raise an error when the response currency differs from the order."""
        data = self._get_base_data(currency={"iso": self.currency_usd.name})
        with self.assertRaisesRegex(
            UserError,
            "The currency of the imported OrderResponse",
        ):
            self.OrderResponseImport.process_data(data)

    def test_acknowledgement_sets_supplier_acknowledgement_date(self):
        """Set the supplier acknowledgement date on acknowledgement."""
        data = self._get_base_data(status="acknowledgement")
        self.assertFalse(self.purchase_order.supplier_ack_dt)
        self.OrderResponseImport.process_data(data)
        self.assertTrue(self.purchase_order.supplier_ack_dt)

    def test_accepted_response_confirms_order(self):
        """Confirm the purchase order and create a receipt on acceptance."""
        data = self._get_base_data(status="accepted")
        self.assertFalse(self.purchase_order.picking_ids)
        self.assertEqual(self.purchase_order.state, "draft")
        self.OrderResponseImport.process_data(data)
        self.assertTrue(self.purchase_order.picking_ids)
        self.assertEqual(self.purchase_order.state, "purchase")

    def test_rejected_response_cancels_order(self):
        """Cancel the purchase order on rejection."""
        data = self._get_base_data(status="rejected")
        self.assertEqual(self.purchase_order.state, "draft")
        self.OrderResponseImport.process_data(data)
        self.assertEqual(self.purchase_order.state, "cancel")

    def test_conditional_response_requires_all_lines(self):
        """Raise an error when conditional acceptance omits order lines."""
        data = self._line_response_data()
        with self.assertRaisesRegex(
            UserError,
            "Unable to conditionally confirm the purchase order.",
        ):
            self.OrderResponseImport.process_data(data)

    def test_conditional_response_rejects_wrong_line_id(self):
        """Raise an error when conditional acceptance references unknown lines."""
        line2 = self._order_line_to_data(self.line2)
        line2["line_id"] = "WRONG"
        data = self._line_response_data(
            self._order_line_to_data(self.line1),
            line2,
        )
        with self.assertRaisesRegex(
            UserError,
            "Unable to conditionally confirm the purchase order.",
        ):
            self.OrderResponseImport.process_data(data)

    def test_conditional_response_accepts_all_lines(self):
        """Confirm the order when all conditional response lines are accepted."""
        data = self._line_response_data(
            self._order_line_to_data(self.line1),
            self._order_line_to_data(self.line2),
        )
        self.OrderResponseImport.process_data(data)
        self.assertEqual(self.purchase_order.state, "purchase")
        self.assertTrue(self.purchase_order.picking_ids)
        self.assertEqual(self.line1.move_ids.state, "assigned")
        self.assertEqual(self.line2.move_ids.state, "assigned")

    def test_conditional_response_rejects_a_line(self):
        """Cancel the receipt move for a rejected conditional response line."""
        data = self._line_response_data(
            self._order_line_to_data(self.line1),
            self._order_line_to_data(
                self.line2,
                status="rejected",
                note="cancel by import",
            ),
        )
        self.OrderResponseImport.process_data(data)
        self.assertEqual(self.purchase_order.state, "purchase")
        self.assertTrue(self.purchase_order.picking_ids)
        self.assertEqual(self.line1.move_ids.state, "assigned")
        self.assertEqual(self.line2.move_ids.state, "cancel")
        self.assertIn("cancel by import", self.line2.move_ids.description_picking)

    def test_conditional_response_amends_qty_without_backorder(self):
        """Cancel the remaining receipt quantity when no backorder is planned."""
        confirmed_qty = self.line1.product_qty - 3
        data = self._line_response_data(
            self._order_line_to_data(
                self.line1,
                status="amend",
                qty=confirmed_qty,
            ),
            self._order_line_to_data(self.line2),
        )
        self.OrderResponseImport.process_data(data)
        self.assertEqual(self.purchase_order.state, "purchase")
        self.assertTrue(self.purchase_order.picking_ids)
        move_ids = self.line1.move_ids
        self.assertEqual(len(move_ids), 2)
        self.assertEqual(sum(move_ids.mapped("product_qty")), self.line1.product_qty)
        assigned = move_ids.filtered(lambda move: move.state == "assigned")
        self.assertEqual(assigned.product_qty, confirmed_qty)
        cancel = move_ids.filtered(lambda move: move.state == "cancel")
        self.assertEqual(cancel.product_qty, 3)
        self.assertEqual(
            cancel.description_picking,
            "No backorder planned by the supplier.",
        )

    def test_conditional_response_amends_qty_with_full_backorder(self):
        """Split the remaining receipt quantity into a backorder."""
        confirmed_qty = self.line1.product_qty - 3
        data = self._line_response_data(
            self._order_line_to_data(
                self.line1,
                status="amend",
                qty=confirmed_qty,
                backorder_qty=3,
                note="my note",
            ),
            self._order_line_to_data(self.line2),
        )
        self.OrderResponseImport.process_data(data)
        self.assertEqual(self.purchase_order.state, "purchase")
        self.assertEqual(len(self.purchase_order.picking_ids), 2)
        move_ids = self.line1.move_ids
        self.assertEqual(len(move_ids), 2)
        self.assertEqual(sum(move_ids.mapped("product_qty")), self.line1.product_qty)
        move_confirmed = move_ids.filtered(
            lambda move: move.state == "assigned" and move.product_qty == confirmed_qty
        )
        self.assertTrue(move_confirmed)
        self.assertEqual(
            "my note\n3 items should be delivered into a next delivery.",
            move_confirmed.description_picking,
        )
        move_backorder = move_ids.filtered(
            lambda move: move.state == "assigned" and move.product_qty == 3
        )
        self.assertTrue(move_backorder)
        self.assertEqual(
            move_backorder.picking_id.backorder_id,
            move_confirmed.picking_id,
        )

    def test_conditional_response_amends_multiple_lines_with_backorder(self):
        """Create one backorder containing amended quantities for several lines."""
        line1_confirmed_qty = self.line1.product_qty - 3
        line2_confirmed_qty = self.line2.product_qty - 3
        data = self._line_response_data(
            self._order_line_to_data(
                self.line1,
                status="amend",
                qty=line1_confirmed_qty,
                backorder_qty=3,
                note="my note",
            ),
            self._order_line_to_data(
                self.line2,
                status="amend",
                qty=line2_confirmed_qty,
                backorder_qty=3,
                note="my note",
            ),
        )
        self.OrderResponseImport.process_data(data)
        self.assertEqual(self.purchase_order.state, "purchase")
        self.assertEqual(len(self.purchase_order.picking_ids), 2)
        self._assert_amended_moves(self.line1, line1_confirmed_qty, 3, "my note")
        self._assert_amended_moves(self.line2, line2_confirmed_qty, 3, "my note")

    def test_conditional_response_amends_qty_with_partial_backorder(self):
        """Cancel the unplanned part of an amended remaining quantity."""
        confirmed_qty = self.line1.product_qty - 3
        data = self._line_response_data(
            self._order_line_to_data(
                self.line1,
                status="amend",
                qty=confirmed_qty,
                backorder_qty=2,
            ),
            self._order_line_to_data(self.line2),
        )
        self.OrderResponseImport.process_data(data)
        self.assertEqual(self.purchase_order.state, "purchase")
        self.assertEqual(len(self.purchase_order.picking_ids), 2)
        move_ids = self.line1.move_ids
        self.assertEqual(len(move_ids), 3)
        self.assertEqual(sum(move_ids.mapped("product_qty")), self.line1.product_qty)
        move_confirmed = move_ids.filtered(
            lambda move: move.state == "assigned" and move.product_qty == confirmed_qty
        )
        self.assertTrue(move_confirmed)
        self.assertIn(
            "2 items should be delivered into a next delivery.",
            move_confirmed.description_picking,
        )
        move_cancel = move_ids.filtered(
            lambda move: move.state == "cancel" and move.product_qty == 1
        )
        self.assertTrue(move_cancel)
        self.assertEqual(
            "No backorder planned by the supplier.",
            move_cancel.description_picking,
        )
        move_backorder = move_ids.filtered(
            lambda move: move.state == "assigned" and move.product_qty == 2
        )
        self.assertTrue(move_backorder)
        self.assertEqual(
            move_backorder.picking_id.backorder_id,
            move_confirmed.picking_id,
        )

    def _assert_amended_moves(
        self,
        order_line,
        confirmed_qty: float,
        backorder_qty: float,
        note: str | None = None,
    ):
        """Assert that amended moves are split between receipt and backorder."""
        move_ids = order_line.move_ids
        self.assertEqual(len(move_ids), 2)
        self.assertEqual(sum(move_ids.mapped("product_qty")), order_line.product_qty)
        move_confirmed = move_ids.filtered(
            lambda move: move.state == "assigned" and move.product_qty == confirmed_qty
        )
        self.assertTrue(move_confirmed)
        expected_note = (
            f"{backorder_qty} items should be delivered into a next delivery."
        )
        if note:
            expected_note = f"{note}\n{expected_note}"
        self.assertEqual(
            expected_note,
            move_confirmed.description_picking,
        )
        move_backorder = move_ids.filtered(
            lambda move: move.state == "assigned" and move.product_qty == backorder_qty
        )
        self.assertTrue(move_backorder)
        self.assertEqual(
            move_backorder.picking_id.backorder_id,
            move_confirmed.picking_id,
        )
