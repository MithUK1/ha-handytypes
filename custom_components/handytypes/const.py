"""Constants for Handy Types."""

DOMAIN = "handytypes"

# Prefix of the entity IDs, so typing "ht" in the entity picker finds them
STATE_DOMAIN = "ht"

# Row types offered as entities: type -> (display name, picker icon)
ROW_TYPES = {
    "divider": ("Divider", "mdi:minus"),
    "spacer": ("Spacer", "mdi:arrow-expand-vertical"),
    "section": ("Section", "mdi:format-title"),
    "weblink": ("Web link", "mdi:link-variant"),
}

# State attribute read by the frontend module to decide how to draw a row
ATTR_TYPE = "ht_type"

# URL the frontend module is served from
FRONTEND_URL = "/handytypes/handytypes.js"
