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
        // A web link row errors without a url, so use a placeholder until set
        url: options.url || "#",
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

// Add a URL box to the row editor (the pencil dialog) for web link rows
const addUrlField = (editor) => {
  const entityId = editor._config?.entity;
  const attrs = getHass()?.states?.[entityId]?.attributes;
  if (!attrs || attrs[ATTR_TYPE] !== "weblink") return;

  const form = editor.shadowRoot?.querySelector("ha-form");
  if (!form || !Array.isArray(form.schema)) return;
  if (form.schema.some((field) => field.name === "url")) return;

  // Put the URL box straight after the Name box
  const schema = [...form.schema];
  const nameIndex = schema.findIndex((field) => field.name === "name");
  schema.splice(nameIndex + 1, 0, {
    name: "url",
    selector: { text: { type: "url" } },
  });

  // Give the new box a readable label, leave the others as they are
  const originalLabel = form.computeLabel;
  form.computeLabel = (field, ...rest) =>
    field.name === "url" ? "URL" : originalLabel?.(field, ...rest);

  form.schema = schema;
};

// The row editor is loaded on demand, so wait for it to be registered
customElements.whenDefined("hui-generic-entity-row-editor").then(() => {
  const RowEditor = customElements.get("hui-generic-entity-row-editor");
  const originalUpdated = RowEditor.prototype.updated;

  RowEditor.prototype.updated = function (changed) {
    originalUpdated?.call(this, changed);
    addUrlField(this);
  };
});
