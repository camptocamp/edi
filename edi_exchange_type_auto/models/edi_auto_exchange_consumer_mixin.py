# Copyright 2022 Camptocamp SA
# @author Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).
# TODO: consider AGPL

import logging

from odoo import api, models
from odoo.tools import frozendict

_logger = logging.getLogger("edi_exchange_auto")


class EDIAutoExchangeConsumerMixin(models.AbstractModel):
    """Enhance edi.exchange.consumer.mixin behavior to automatize actions."""

    _name = "edi.auto.exchange.consumer.mixin"
    _inherit = "edi.exchange.consumer.mixin"
    _description = __doc__

    @api.model
    def _edi_get_exchange_type_conf(self, exchange_type):
        conf = super()._edi_get_exchange_type_conf(exchange_type)
        conf.update({"auto": exchange_type.get_settings().get("auto", {})})
        return conf

    """Disable automatic EDI programmatically on models.
    """  # pylint: disable=pointless-string-statement
    _edi_no_auto_for_operation = (
        # "create",
        # "write",
        # "unlink",
    )

    def create(self, vals):
        rec = super().create(vals)
        to_be_done = None
        operation = "create"
        if not self._edi_auto_skip(operation):
            to_be_done = rec._edi_auto_collect_to_be_done(operation, vals)
        if to_be_done:
            rec._edi_auto_trigger_events(to_be_done)
        return rec

    def write(self, vals):
        to_be_done = None
        operation = "write"
        if not self._edi_auto_skip(operation):
            to_be_done = self._edi_auto_collect_to_be_done(operation, vals)
        res = super().write(vals)
        if to_be_done:
            self._edi_auto_trigger_events(to_be_done)
        return res

    def _edi_auto_skip(self, operation):
        if self.env.context.get("edi__skip_auto_handle"):
            return True
        if operation in self._edi_no_auto_for_operation:
            return True
        return False

    def _edi_auto_collect_to_be_done(self, operation, new_vals):
        res = []
        # auto:
        #   disable: true|false
        #   actions:
        #     generate:
        #         on:
        #           - create
        #           - write
        #           - unlink
        #         force: true
        #         trigger_fields:
        #           - state
        #           - order_line
        #         tracked_fields:
        #           - state
        #           - expected_date
        #
        rec_by_type = self._edi_auto_collect_records_by_type(operation)
        for type_id, data in rec_by_type.items():
            conf = data["conf"]
            records = data["records"]
            for action_name, action_conf in conf.get("actions", {}).items():
                if operation not in action_conf.get("on"):
                    skip_reason = f"Operation not allowed by action={action_name}"
                    self._edi_auto_log_skip(operation, type_id, skip_reason)
                    continue
                triggers = action_conf.get("trigger_fields", [])
                if not triggers:
                    skip_reason = f"No trigger set for action={action_name}"
                    self._edi_auto_log_skip(operation, type_id, skip_reason)
                    continue
                tracked = action_conf.get("tracked_fields", [])
                trigger = None
                for k in triggers:
                    if k in new_vals:
                        trigger = k
                        break
                if trigger:
                    if trigger not in tracked:
                        tracked.append(trigger)
                    vals = frozendict(
                        {k: v for k, v in new_vals.items() if k in tracked}
                    )
                    for rec in records:
                        old_vals = frozendict({k: rec[k] for k in tracked})
                        todo = self._edi_auto_prepare_todo(
                            type_id=type_id,
                            edi_action=action_name,
                            conf=action_conf,
                            triggered_by=trigger,
                            record=rec,
                            vals=vals,
                            old_vals=old_vals,
                            force=action_conf.get("force", False),
                        )
                        res.append(todo)
        return res

    def _edi_auto_log_skip(self, operation, type_id, reason):
        _logger.debug(
            "Skip model=%(model)s type=%(type_id)s op=%(op)s: %(reason)s",
            {
                "model": self._name,
                "op": operation,
                "type_id": type_id,
                "reason": reason,
            },
        )

    def _edi_auto_prepare_todo(self, **kw):
        return AutoEventToDo(**kw)

    def _edi_auto_collect_records_by_type(self, operation):
        skip_type_ids = set()
        rec_by_type = {}
        for rec in self:
            for type_id, conf in rec.expected_edi_configuration.items():
                if type_id in skip_type_ids:
                    continue
                auto_conf = conf.get("auto", {})
                actions = auto_conf.get("actions", {})
                skip_reason = None
                if not auto_conf or auto_conf.get("disable"):
                    skip_reason = "Auto-conf not found or disabled"
                elif not actions:
                    skip_reason = "Auto-conf has no action configured"
                if skip_reason:
                    skip_type_ids.add(type_id)
                    self._edi_auto_log_skip(operation, type_id, skip_reason)
                    continue
                if type_id not in rec_by_type:
                    rec_by_type[type_id] = {"conf": auto_conf, "records": []}
                rec_by_type[type_id]["records"].append(rec)
        return rec_by_type

    def _edi_auto_trigger_events(self, to_be_done):
        for todo in to_be_done:
            evt_name = f"on_edi_auto_{todo.edi_action}"
            self._event(evt_name).notify(todo.record, todo)

    # TODO
    # def create(self, vals):
    # def unlink(self):


class AutoEventToDo:
    __slots__ = (
        "type_id",
        "edi_action",
        "conf",
        "triggered_by",
        "record",
        "vals",
        "old_vals",
        "force",
    )

    def __init__(self, **kw):
        for k, v in kw.items():
            if k in self.__slots__:
                setattr(self, k, v)
