"""Constants for Handy Types."""

DOMAIN = "handytypes"

# Subentry types that take user input (each one becomes its own entity)
TYPE_SECTION = "section"
TYPE_TEXT = "text"
TYPE_WEBLINK = "weblink"

# Fixed types created automatically with the integration (no input needed)
TYPE_DIVIDER = "divider"
TYPE_SPACER = "spacer"

# Config keys used by the subentry forms
CONF_LABEL = "label"
CONF_TEXT = "text"
CONF_URL = "url"
CONF_ICON = "icon"

# State attribute read by the frontend module to decide how to draw a row
ATTR_TYPE = "ht_type"

# URL the frontend module is served from
FRONTEND_URL = "/handytypes/handytypes.js"
