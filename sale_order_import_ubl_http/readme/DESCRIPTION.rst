This module extends the `sale_order_import_ubl` module to allow for importing sales order automatically.
To do so it adds a HTTP endpoint `ubl_api\sales` accepting a POST request containing the XML UBL formatted sale order.

On reception the endpoint will check the validity of the XML received and if ok create a queue.job that will import the sale.order and set it as confirmed.
