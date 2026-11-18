"""Entities that stand in for entities card row types."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry, ConfigSubentry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util import slugify

from .const import (
    ATTR_TYPE,
    CONF_ICON,
    CONF_LABEL,
    CONF_TEXT,
    CONF_URL,
    TYPE_DIVIDER,
    TYPE_SPACER,
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Create the fixed entities plus one entity per user-added item."""
    async_add_entities(
        [
            HandyTypeEntity(
                unique_id=f"{entry.entry_id}_{TYPE_DIVIDER}",
                row_type=TYPE_DIVIDER,
                name="Divider",
                object_id=f"ht_{TYPE_DIVIDER}",
            ),
            HandyTypeEntity(
                unique_id=f"{entry.entry_id}_{TYPE_SPACER}",
                row_type=TYPE_SPACER,
                name="Spacer",
                object_id=f"ht_{TYPE_SPACER}",
            ),
        ]
    )

    # Items the user added through the integration page (section, text, weblink)
    for subentry_id, subentry in entry.subentries.items():
        async_add_entities(
            [_entity_from_subentry(subentry)],
            config_subentry_id=subentry_id,
        )


def _entity_from_subentry(subentry: ConfigSubentry) -> HandyTypeEntity:
    """Build an entity from a saved section, text or weblink item."""
    data = subentry.data
    label = data[CONF_LABEL]

    # Only pass on the fields that belong to this type
    extra = {
        key: data[key]
        for key in (CONF_TEXT, CONF_URL, CONF_ICON)
        if data.get(key)
    }

    return HandyTypeEntity(
        unique_id=subentry.subentry_id,
        row_type=subentry.subentry_type,
        name=label,
        object_id=f"ht_{subentry.subentry_type}_{slugify(label)}",
        extra=extra,
    )


class HandyTypeEntity(SensorEntity):
    """A static entity the frontend swaps for a real row type."""

    _attr_should_poll = False
    # Diagnostic keeps these out of auto-generated dashboards
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        unique_id: str,
        row_type: str,
        name: str,
        object_id: str,
        extra: dict | None = None,
    ) -> None:
        """Store the row type and any extra settings."""
        self._attr_unique_id = unique_id
        self._attr_name = name
        self._attr_native_value = row_type
        self._attr_extra_state_attributes = {ATTR_TYPE: row_type, **(extra or {})}

        # The ht_ prefix means typing "ht" in the entity picker finds these
        self.entity_id = f"sensor.{object_id}"
