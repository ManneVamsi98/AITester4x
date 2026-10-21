"""Module name resolution: case-insensitive keys, aliases and did-you-mean."""

from __future__ import annotations

import difflib
import re

from fastmcp.exceptions import ToolError

# Short forms users type that do not match the canonical slug.
ALIASES: dict[str, str] = {
    "ab": "A/B Testing",
    "ab testing": "A/B Testing",
    "sdk": "SDK / Server-Side API",
    "server side": "SDK / Server-Side API",
    "server side api": "SDK / Server-Side API",
    "billing": "Account & Billing",
    "account": "Account & Billing",
    "account billing": "Account & Billing",
}


def module_key(name: str) -> str:
    """Lowercase and collapse non-alphanumeric runs to single spaces."""
    return re.sub(r"[^a-z0-9]+", " ", name.lower()).strip()


class ModuleResolver:
    def __init__(self, modules: list[str]):
        self.modules = sorted(modules)
        self._by_key: dict[str, str] = {}
        for module in modules:
            self._by_key.setdefault(module_key(module), module)
        # Aliases only apply if they do not shadow a real module key.
        for alias, canonical in ALIASES.items():
            if canonical in self._by_key.values() and alias not in self._by_key:
                self._by_key[alias] = canonical
        self._keys = list(self._by_key.keys())

    def resolve(self, name: str) -> str:
        key = module_key(name)
        if key in self._by_key:
            return self._by_key[key]
        # Case-insensitive substring match (e.g. "server" -> SDK module).
        matches = [m for m in self.modules if key in module_key(m)]
        if len(matches) == 1:
            return matches[0]
        suggestion = difflib.get_close_matches(key, self._keys, n=1, cutoff=0.6)
        hint = ""
        if suggestion:
            hint = f" Did you mean '{self._by_key[suggestion[0]]}'?"
        valid = ", ".join(repr(m) for m in self.modules)
        raise ToolError(f"Unknown module '{name}'.{hint} Valid: {valid}")

    def resolve_many(self, names: list[str]) -> list[str]:
        return [self.resolve(n) for n in names]

    def alias_map(self) -> dict[str, str]:
        return dict(sorted(ALIASES.items()))
