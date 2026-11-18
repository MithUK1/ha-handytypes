"""Handy Types - extra row types for the entities card, selectable as entities."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.util import slugify

from .const import (
    ATTR_TYPE,
    CONF_ICON,
    CONF_LABEL,
    CONF_TEXT,
    CONF_URL,
    DOMAIN,
    FRONTEND_URL,
    STATE_DOMAIN,
    TYPE_DIVIDER,
    TYPE_SPACER,
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
    """Publish a state for every row type so they show up in the entity picker."""
    published: list[str] = []

    def publish(object_id: str, row_type: str, name: str, extra: dict | None = None):
        """Write one state, adding a number if the ID is already taken."""
        entity_id = f"{STATE_DOMAIN}.{object_id}"
        count = 2
        while entity_id in published:
            entity_id = f"{STATE_DOMAIN}.{object_id}_{count}"
            count += 1

        hass.states.async_set(
            entity_id,
            row_type,
            {"friendly_name": name, ATTR_TYPE: row_type, **(extra or {})},
        )
        published.append(entity_id)

    # Fixed rows that need no input
    publish(TYPE_DIVIDER, TYPE_DIVIDER, "Divider")
    publish(TYPE_SPACER, TYPE_SPACER, "Spacer")

    # Items the user added through the integration page
    for subentry in entry.subentries.values():
        label = subentry.data[CONF_LABEL]

        # Only pass on the fields that belong to this type
        extra = {
            key: subentry.data[key]
            for key in (CONF_TEXT, CONF_URL, CONF_ICON)
            if subentry.data.get(key)
        }
        publish(
            f"{subentry.subentry_type}_{slugify(label)}",
            subentry.subentry_type,
            label,
            extra,
        )

    # Remember what we published so it can be removed on unload
    entry.runtime_data = published

    # Reload when a section/text/weblink item is added, edited or removed
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Remove the published states."""
    for entity_id in entry.runtime_data:
        hass.states.async_remove(entity_id)
    return True


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry after its subentries change."""
    await hass.config_entries.async_reload(entry.entry_id)
