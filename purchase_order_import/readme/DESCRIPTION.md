This module provides the base wizards and hooks to import supplier quotation
documents and supplier OrderResponse documents on purchase orders. It provides
the generic import workflow; format-specific modules implement the XML parsers.

The import wizards accept XML files directly and PDF files containing embedded
XML attachments. For the Universal Business Language (UBL) format, install:

- `purchase_order_import_ubl` to import supplier quotations.
- `order_response_import_ubl` to import supplier OrderResponse documents.

On a Request for Quotation, the **Import Quotation File** button opens a wizard
to upload the supplier quotation and choose how the RFQ should be updated:

- update only the prices of the draft purchase order from the quotation file
  (default option);
- update both prices and quantities.

When the quotation is imported, Odoo compares it with the current RFQ:

- lines present in the quotation but missing from the RFQ are created on the
  purchase order;
- lines present in the RFQ but missing from the quotation are kept, and a
  warning is added to the chatter;
- lines present in both documents are updated when prices or, depending on the
  selected option, quantities differ;
- the incoterm is updated when the quotation contains a different incoterm;
- the imported file is attached to the purchase order.

After importing a quotation, review the purchase order chatter because it may
contain important warnings or import details.

OrderResponse imports are matched to a purchase order by reference and can
acknowledge, accept, reject, or conditionally accept the order. Conditional
acceptance updates receipt moves according to line amendments, including
splitting moves, creating backorders, or cancelling remaining quantities when no
backorder is planned.
