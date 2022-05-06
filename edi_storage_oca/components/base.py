# Copyright 2020 ACSONE
# Copyright 2022 Camptocamp
# @author: Simone Orsi <simahawk@gmail.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

from pathlib import PurePath

from odoo.addons.component.core import AbstractComponent


class EDIStorageComponentMixin(AbstractComponent):

    _name = "edi.storage.component.mixin"
    _inherit = "edi.component.mixin"
    # Components having `_storage_backend_type` will have precedence.
    # If the value is not set, generic components will be used.
    _storage_backend_type = None

    def __init__(self, work_context):
        super().__init__(work_context)
        self.storage_settings = self.type_settings.get("storage", {})

    @classmethod
    def _component_match(cls, work, usage=None, model_name=None, **kw):
        res = super()._component_match(work, usage=usage, model_name=model_name, **kw)
        storage_type = kw.get("storage_backend_type")
        if storage_type and cls._storage_backend_type:
            return cls._storage_backend_type == storage_type
        return res

    @property
    def storage(self):
        return self.backend.storage_id

    def _dir_by_state(self, direction, state):
        """Return remote directory path by direction and state.

        :param direction: string stating direction of the exchange
        :param state: string stating state of the exchange
        :return: PurePath object
        """
        assert direction in ("input", "output")
        assert state in ("pending", "done", "error")
        return PurePath(
            (self.backend[direction + "_dir_" + state] or "").strip().rstrip("/")
        )

    def _remote_file_path(self, direction, state, filename, prefix=None):
        """Return remote file path by direction and state for give filename.

        :param direction: string stating direction of the exchange
        :param state: string stating state of the exchange
        :param filename: string for file name
        :return: PurePath object
        """
        path = self._dir_by_state(direction, state) / filename.strip("/ ")
        if prefix:
            path = prefix / path
        return path

    def _get_remote_file(self, state, filename=None, binary=False):
        """Get file for current exchange_record in the given destination state.

        :param state: string ("pending", "done", "error")
        :param filename: custom file name, exchange_record filename used by default
        :return: remote file content as string
        """
        filename = filename or self.exchange_record.exchange_filename
        path_prefix = self._get_exchange_type_path()
        path = self._remote_file_path(
            self.exchange_record.direction, state, filename, prefix=path_prefix
        )
        try:
            # TODO: support match via pattern (eg: filename-prefix-*)
            # otherwise is impossible to retrieve input files and acks
            # (the date will never match)
            return self.storage.get(path.as_posix(), binary=binary)
        except FileNotFoundError:
            return None

    def _get_exchange_type_path(self):
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
        path = self.storage_settings.get("path")
        if path:
            return PurePath(path)
        path_config_param = self.storage_settings.get("path_config_param")
        if path_config_param:
            icp = self.env["ir.config_parameter"].sudo()
            path = icp.get_param(path_config_param)
            return PurePath(path)
