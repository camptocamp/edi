# Copyright 2021 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).
import base64

from odoo import _, api, exceptions, fields, models


class SaleOrderImport(models.TransientModel):
    _name = "sale.order.import.http.reschedule.wiz"

    file_id = fields.Many2one(
        comodel_name="sale.order.ubl.import.file",
        ondelete="cascade",
        required=True,
        domain=[("job_state", "=", "failed")],
    )
    xml_data = fields.Text(compute="_compute_xml_data", readonly=False, store=True)
    # TODO: use a m2o?
    job_channel = fields.Char(
        compute="_compute_job_channel", readonly=False, store=True
    )

    @api.depends("file_id")
    def _compute_job_channel(self):
        for rec in self:
            job = rec.file_id.job_id
            rec.job_channel = job.channel if job else "ubl_import"

    @api.depends("file_id.datas")
    def _compute_xml_data(self):
        for rec in self:
            data = rec.file_id.datas
            rec.xml_data = base64.decodestring(data) if data else ""

    def action_execute(self):
        if self.file_id.job_state != "failed":
            raise exceptions.UserError(_("Only failed files can be re-scheduled"))
        if not self.xml_data.strip():
            raise exceptions.UserError(_("No XML provided"))
        job = self.file_id.job_id
        if job:
            job_values = {"description": job.name, "channel": job.channel}
        else:
            job_values = {
                "description": "Import UBL order from http",
                "channel": "ubl_import",
            }
        new_file = self.file_id._quick_create(
            self.xml_data.encode("utf-8"), self.file_id.method_name, parent=self.file_id
        )
        so_model = self.env["sale.order"].with_delay(**job_values)
        new_job = getattr(so_model, self.file_id.method_name)(new_file)
        new_file.job_id = new_job.db_record()
        return {
            "name": _("Re-scheduled import job"),
            "domain": [("id", "=", new_file.job_id.id)],
            "res_model": "queue.job",
            "type": "ir.actions.act_window",
            "view_id": False,
            "view_mode": "tree,form",
            "context": self.env.context,
        }
