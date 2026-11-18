"""Config flow for Handy Types."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.core import callback
from homeassistant.helpers import selector

from .const import (
    CONF_ICON,
    CONF_LABEL,
    CONF_TEXT,
    CONF_URL,
    DOMAIN,
    TYPE_SECTION,
    TYPE_TEXT,
    TYPE_WEBLINK,
)


class HandyTypesConfigFlow(ConfigFlow, domain=DOMAIN):
    """One click setup, there is nothing to configure."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Confirm adding the integration."""
        if user_input is not None:
            return self.async_create_entry(title="Handy Types", data={})
        return self.async_show_form(step_id="user")

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Items the user can add on top of the fixed divider and spacer."""
        return {
            TYPE_SECTION: SectionSubentryFlow,
            TYPE_TEXT: TextSubentryFlow,
            TYPE_WEBLINK: WeblinkSubentryFlow,
        }


class _ItemSubentryFlow(ConfigSubentryFlow):
    """Shared add and edit steps, each item type supplies its own form."""

    schema: vol.Schema

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Add a new item."""
        if user_input is not None:
            return self.async_create_entry(
                title=user_input[CONF_LABEL], data=user_input
            )
        return self.async_show_form(step_id="user", data_schema=self.schema)

    async def async_step_reconfigure(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """Edit an existing item."""
        subentry = self._get_reconfigure_subentry()

        if user_input is not None:
            return self.async_update_and_abort(
                self._get_entry(),
                subentry,
                title=user_input[CONF_LABEL],
                data=user_input,
            )

        return self.async_show_form(
            step_id="reconfigure",
            data_schema=self.add_suggested_values_to_schema(
                self.schema, subentry.data
            ),
        )


class SectionSubentryFlow(_ItemSubentryFlow):
    """A heading row."""

    schema = vol.Schema({vol.Required(CONF_LABEL): str})


class TextSubentryFlow(_ItemSubentryFlow):
    """A row showing a label and a line of static text."""

    schema = vol.Schema(
        {
            vol.Required(CONF_LABEL): str,
            vol.Required(CONF_TEXT): str,
        }
    )


class WeblinkSubentryFlow(_ItemSubentryFlow):
    """A row that opens a link."""

    schema = vol.Schema(
        {
            vol.Required(CONF_LABEL): str,
            vol.Required(CONF_URL): str,
            vol.Optional(CONF_ICON): selector.IconSelector(),
        }
    )
