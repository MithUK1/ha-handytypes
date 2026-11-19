/*
 * Handy Types - frontend module
 *
 * Entities created by the Handy Types integration carry an "ht_type"
 * attribute. When the entities card is given one of them, this module swaps
 * the entity row for the matching row type, so picking "Divider" from the
 * entity list behaves the same as writing "- type: divider" in YAML.
 *
 * Section and web link rows take their text from the row's own Name field,
 * which is editable with the pencil icon in the card editor.
 */

const ATTR_TYPE = "ht_type";

// Spacer is not a built-in row type, so draw it as a small custom row
class HandyTypesSpacerRow extends HTMLElement {
  setConfig(config) {
    this._config = config;
    this.style.display = "block";
    this.style.height = "16px";
  }

  // The entities card passes hass to every row, nothing to do with it here
  set hass(_hass) {}
}

if (!customElements.get("ht-spacer-row")) {
  customElements.define("ht-spacer-row", HandyTypesSpacerRow);
}

// Latest hass object, read from the root Home Assistant element
const getHass = () => document.querySelector("home-assistant")?.hass;

// Use the name set on the row if it is plain text, otherwise the entity name
const rowName = (row, stateObj) =>
  typeof row === "object" && typeof row.name === "string" && row.name
    ? row.name
    : stateObj.attributes.friendly_name;

// Turn an entity row into the real row config, or return it untouched
const convertRow = (row) => {
  const entityId = typeof row === "string" ? row : row && row.entity;
  if (!entityId) return row;

  const stateObj = getHass()?.states?.[entityId];
  const attrs = stateObj?.attributes;
  if (!attrs || !attrs[ATTR_TYPE]) return row;

  const options = typeof row === "object" ? row : {};

  switch (attrs[ATTR_TYPE]) {
    case "divider":
      return { type: "divider" };
    case "spacer":
      return { type: "custom:ht-spacer-row" };
    case "section":
      return { type: "section", label: rowName(row, stateObj) };
    case "weblink":
      return {
        type: "weblink",
        name: rowName(row, stateObj),
        url: options.url,
        icon: options.icon || attrs.icon,
      };
    default:
      return row;
  }
};

// Wait until the entities card is registered, then wrap its setConfig
customElements.whenDefined("hui-entities-card").then(() => {
  const EntitiesCard = customElements.get("hui-entities-card");
  const originalSetConfig = EntitiesCard.prototype.setConfig;

  EntitiesCard.prototype.setConfig = function (config) {
    if (config && Array.isArray(config.entities)) {
      config = { ...config, entities: config.entities.map(convertRow) };
    }
    return originalSetConfig.call(this, config);
  };
});
