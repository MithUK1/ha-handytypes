"""Handy Types - extra row types for the entities card, selectable as entities."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import (
    ATTR_TYPE,
    DOMAIN,
    FRONTEND_URL,
    ROW_TYPES,
    STATE_DOMAIN,
)


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    """Serve the frontend module and load it on every dashboard."""
    js_path = Path(__file__).parent / "frontend" / "handytypes.js"

    # cache_headers=False so a browser refresh always picks up a new version
    await hass.http.async_register_static_paths(
        [StaticPathConfig(FRONTEND_URL, str(js_path), False)]
    )
    add_extra_js_url(hass, FRONTEND_URL)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Publish one state per row type so they show up in the entity picker."""
    # Earlier versions stored items as subentries, which are no longer used
    for subentry_id in list(entry.subentries):
        hass.config_entries.async_remove_subentry(entry, subentry_id)

    published: list[str] = []
    for row_type, (name, icon) in ROW_TYPES.items():
        entity_id = f"{STATE_DOMAIN}.{row_type}"
        hass.states.async_set(
            entity_id,
            row_type,
            {"friendly_name": name, "icon": icon, ATTR_TYPE: row_type},
        )
        published.append(entity_id)

    # Remember what we published so it can be removed on unload
    entry.runtime_data = published
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove the published states."""
    for entity_id in entry.runtime_data:
        hass.states.async_remove(entity_id)
    return True
