"""Handy Types - extra row types for the entities card, selectable as entities."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN, FRONTEND_URL

PLATFORMS = ["sensor"]


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
    """Set up the entities for this config entry."""
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Reload when a section/text/weblink item is added, edited or removed
    entry.async_on_unload(entry.add_update_listener(_async_reload_entry))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload the entities."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the entry after its subentries change."""
    await hass.config_entries.async_reload(entry.entry_id)
