The goal of this module is to improve on the `client_order_ref` on `sale.order`.

By default Odoo only has one field to handle the customer reference of a sale order.
But when using EDI some specifications allow to have two fields for this, the customer
order Id and a customer (free) reference.

To help with this, this module adds two specific fields for them and transform the
`client_order_ref` standard field into a computed one.

The two new fields are also passed on to created invoices.
