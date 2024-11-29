from odoo import api, models


class Base(models.AbstractModel):
    _inherit = "base"

    @api.model
    def _job_prepare_context_before_enqueue_keys(self):
        """Keys to keep in context of stored jobs."""
        context_keys = super()._job_prepare_context_before_enqueue_keys()
        return context_keys + ["product_company_id"]
