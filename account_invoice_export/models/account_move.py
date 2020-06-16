# Copyright 2020 Camptocamp SA
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html)

import requests

import odoo
from odoo import _, fields, models
from odoo.exceptions import UserError

from odoo.addons.queue_job.job import job


class AccountMove(models.Model):
    _inherit = "account.move"

    invoice_sent_through_http = fields.Boolean()

    def send_through_http(self):
        for invoice in self:
            invoice.with_delay()._send_through_http()

    @job
    def _send_through_http(self):
        """Send invoice to server configured in transmit method."""
        self.ensure_one()
        if self.invoice_sent_through_http:
            return "Invoice has already been sent through http before."
        if not self.transmit_method_id.send_through_http:
            raise UserError(_("Transmit method is not configured to send through HTTP"))
        file_data = self._get_file_for_transmission_method()
        headers = self.transmit_method_id.get_transmition_http_header()
        res = requests.post(
            self.transmit_method_id.destination_url, headers=headers, files=file_data
        )
        if res.status_code != 200:
            values = {
                "job_id": self.env.context.get("job_uuid"),
                "send_error": res.status_code,
                "transmit_method_name": self.transmit_method_id.name,
            }
            with odoo.api.Environment.manage():
                with odoo.registry(self.env.cr.dbname).cursor() as new_cr:
                    # Create a new environment with new cursor database
                    new_env = odoo.api.Environment(
                        new_cr, self.env.uid, self.env.context
                    )
                    # The chatter of the invoice need to be updated, when the job fails
                    self.with_env(new_env).log_error_sending_invoice(values)
            raise UserError(
                _(
                    "HTTP error {} sending invoice to {}".format(
                        res.status_code, self.transmit_method_id.name
                    )
                )
            )
        self.invoice_sent_through_http = True
        self.invoice_send = True
        self.log_success_sending_invoice()
        return res.text

    def _get_file_for_transmission_method(self):
        """Return the file description to send.

        Use the format expected by the request library
        By default returns the PDF report.
        """
        r = self.env["ir.actions.report"]._get_report_from_name(
            "account.report_invoice"
        )
        pdf, _ = r.render([self.id])
        return {"file": ("test_invoice", pdf, "application/pdf")}

    def log_error_sending_invoice(self, values):
        """Log an exception in invoice's chatter when sending fails.

        If an exception already exists it is update otherwise a new one
        is created.

        """
        activity_type = "account_invoice_export.mail_activity_transmit_warning"
        activity = self.activity_reschedule([activity_type], date_deadline="2020-12-31")
        if not activity:
            message = self.env.ref(
                "account_invoice_export.exception_sending_invoice"
            ).render(values=values)
            self.activity_schedule(
                activity_type, summary="Job error sending invoice", note=message
            )
        else:
            activity.note += "<p>It failed again, ouch!</p>"

    def log_success_sending_invoice(self):
        """Log success sending invoice and clear existing exception, if any."""
        self.activity_feedback(
            ["account_invoice_export.mail_activity_transmit_warning"],
            feedback="It worked on a later try",
        )
        self.message_post(
            body=_("Invoice successfuly sent to {}").format(
                self.transmit_method_id.name
            )
        )
