# Copyright 2021 Camptocamp SA
# @author: Simone Orsi <simone.orsi@camptocamp.com>
# License LGPL-3.0 or later (http://www.gnu.org/licenses/lgpl).

_REGISTRY_BY_DB = {}
import time;


class EndpointRegistry:
    """Registry for endpoints.

    Used to:

    * track registered endpoints
    * retrieve routing rules to load in ir.http routing map
    """

    __slots__ = ("_mapping", "_updated_on")

    def __init__(self):
        # collect EndpointRule objects
        self._mapping = {}
        # timestamp of last update
        self._updated_on = 0.0

    def get_rules(self):
        return self._mapping.values()

    # TODO: add test
    def get_rules_by_group(self, group):
        for key, rule in self._mapping.items():
            if rule.route_group == group:
                yield (key, rule)

    def add_or_update_rule(self, rule, force=False, init=False):
        """Add or update an existing rule.

        :param rule: instance of EndpointRule
        :param force: replace a rule forcedly
        :param init: given when adding rules for the first time
        """
        key = rule.key
        existing = self._mapping.get(key)
        if not existing or force:
            self._mapping[key] = rule
            if not init:
                self._refresh_update_required()
            return True
        if existing.endpoint_hash != rule.endpoint_hash:
            # Override and set as to be updated
            self._mapping[key] = rule
            if not init:
                self._refresh_update_required()
            return True

    def drop_rule(self, key):
        existing = self._mapping.pop(key, None)
        if not existing:
            print("DROP not existing")
            return False
        print("DROP refresh")
        self._refresh_update_required()
        return True

    def routing_update_required(self, ts):
        if not ts:
            return True
        return ts < self._updated_on

    def _refresh_update_required(self):
        self._updated_on = time.time()
        print("*******************************")
        print("UPDATED ON", self._updated_on)

    @classmethod
    def registry_for(cls, dbname):
        if dbname not in _REGISTRY_BY_DB:
            _REGISTRY_BY_DB[dbname] = cls()
        return _REGISTRY_BY_DB[dbname]

    @classmethod
    def wipe_registry_for(cls, dbname):
        if dbname in _REGISTRY_BY_DB:
            del _REGISTRY_BY_DB[dbname]

    @staticmethod
    def make_rule(*a, **kw):
        return EndpointRule(*a, **kw)


class EndpointRule:
    """Hold information for a custom endpoint rule."""

    __slots__ = ("key", "route", "endpoint", "routing", "endpoint_hash", "route_group")

    def __init__(self, key, route, endpoint, routing, endpoint_hash, route_group=None):
        self.key = key
        self.route = route
        self.endpoint = endpoint
        self.routing = routing
        self.endpoint_hash = endpoint_hash
        self.route_group = route_group

    def __repr__(self):
        return f"{self.key}: {self.route}" + (
            f"[{self.route_group}]" if self.route_group else ""
        )
