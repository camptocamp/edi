# Copyright 2021 ForgeFlow S.L. (https://www.forgeflow.com)
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

import functools
from pathlib import PurePath

from odoo.addons.component.core import Component


class EdiStorageListener(Component):
    _name = "edi.storage.component.listener"
    _inherit = "base.event.listener"

    def _move_file(self, storage, from_dir_str, to_dir_str, filename):
        from_dir = PurePath(from_dir_str)
        to_dir = PurePath(to_dir_str)
        if filename not in storage.list_files(from_dir.as_posix()):
            # The file might have been moved after a previous error.
            return False
        self._add_after_commit_hook(
            storage._move_files, [(from_dir / filename).as_posix()], to_dir.as_posix()
        )
        return True

    def _add_after_commit_hook(self, move_func, sftp_filepath, sftp_destination_path):
        """Add hook after commit to move the file when transaction is over."""
        self.env.cr.after(
            "commit",
            functools.partial(move_func, sftp_filepath, sftp_destination_path),
        )

    def _get_exchange_type_path(self, storage_settings):
        """Retrieve specific path for current exchange type.

        In your exchange type you can pass this config:

            storage:
                # simple string
                path: path/to/file

        Or

            storage:
                # name of the param containing the path
                path_config_param: path/to/file

        Thanks to the param you could even configure it by env.
        """
        # TODO: Do a common function!
        path = storage_settings.get("path")
        if path:
            return PurePath(path)
        path_config_param = storage_settings.get("path_config_param")
        if path_config_param:
            icp = self.env["ir.config_parameter"].sudo()
            path = icp.get_param(path_config_param)
            if path:
                return PurePath(path)

    def _get_full_input_dir(self, exchange_type, input_dir):
        # TODO: Do a common function!
        type_settings = exchange_type.get_settings()
        storage_settings = type_settings.get("storage", {})

        path_prefix = self._get_exchange_type_path(storage_settings)

        path = PurePath((input_dir or "").strip().rstrip("/"))
        if path_prefix:
            path = path_prefix / path
        return path.as_posix()

    def on_edi_exchange_done(self, record):
        storage = record.backend_id.storage_id
        res = False
        if record.direction == "input" and storage:
            file = record.exchange_filename
            # TODO: Search all places we need to use full input/output dir
            pending_dir = self._get_full_input_dir(record.type_id, record.backend_id.input_dir_pending)
            done_dir = self._get_full_input_dir(record.type_id, record.backend_id.input_dir_done)
            error_dir = self._get_full_input_dir(record.type_id, record.backend_id.input_dir_error)
            if not done_dir:
                return res
            res = self._move_file(storage, pending_dir, done_dir, file)
            if not res:
                # If a file previously failed it should have been previously
                # moved to the error dir, therefore it is not present in the
                # pending dir and we need to retry from error dir.
                res = self._move_file(storage, error_dir, done_dir, file)
        return res

    def on_edi_exchange_error(self, record):
        storage = record.backend_id.storage_id
        res = False
        if record.direction == "input" and storage:
            file = record.exchange_filename
            pending_dir = self._get_full_input_dir(record.type_id, record.backend_id.input_dir_pending)
            error_dir = self._get_full_input_dir(record.type_id, record.backend_id.input_dir_error)
            if error_dir:
                res = self._move_file(storage, pending_dir, error_dir, file)
        return res
