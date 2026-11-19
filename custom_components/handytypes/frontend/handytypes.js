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
        // The address lives in tap_action, which the card editor accepts. A plain
        // url key is still honoured for rows written by hand in YAML.
        // A web link row errors without a url, so use a placeholder until set.
        url: options.tap_action?.url_path || options.url || "#",
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

// The card editor rejects unknown keys on a row, so the URL box saves the
// address as a "url" tap action, which is a key every row is allowed to have
const urlToTapAction = (config) => {
  const { url, ...rest } = config;
  if (url) return { ...rest, tap_action: { action: "url", url_path: url } };
  if (rest.tap_action?.action === "url") delete rest.tap_action;
  return rest;
};

// Browsers offer saved usernames, passwords and past searches in text boxes
// they think are logins or search fields. An unrecognised autocomplete value
// is the one setting browsers reliably leave alone, so use it on our boxes.
const NO_AUTOFILL = { text: { autocomplete: "nope" } };

// Make the pencil dialog for section and web link rows show plain text boxes
const addRowFields = (editor) => {
  const config = editor._config;
  const type = getHass()?.states?.[config?.entity]?.attributes?.[ATTR_TYPE];
  if (type !== "weblink" && type !== "section") return;

  const form = editor.shadowRoot?.querySelector("ha-form");
  if (!form || !Array.isArray(form.schema)) return;

  // Convert the URL box back into a tap action before the editor saves it
  if (!editor._htWrapped) {
    const dispatch = editor.dispatchEvent.bind(editor);
    editor.dispatchEvent = (event) => {
      if (event.type === "config-changed" && event.detail?.config) {
        event = new CustomEvent("config-changed", {
          detail: { config: urlToTapAction(event.detail.config) },
          bubbles: true,
          composed: true,
        });
      }
      return dispatch(event);
    };
    editor._htWrapped = true;
  }

  // Show the saved address in the URL box
  if (type === "weblink") {
    form.data = { ...config, url: config.tap_action?.url_path ?? "" };
  }

  // Only swap the fields once
  if (form.schema.some((field) => field.name === "name" && field.selector?.text)) {
    return;
  }

  // A plain text box replaces the Name box, which is awkward for static text
  const schema = form.schema.map((field) =>
    field.name === "name" ? { name: "name", selector: NO_AUTOFILL } : field
  );
  if (type === "weblink") {
    const nameIndex = schema.findIndex((field) => field.name === "name");
    schema.splice(nameIndex + 1, 0, {
      name: "url",
      selector: NO_AUTOFILL,
    });
  }

  const labels = { name: type === "weblink" ? "Text" : "Heading", url: "URL" };
  const originalLabel = form.computeLabel;
  form.computeLabel = (field, ...rest) =>
    labels[field.name] ?? originalLabel?.(field, ...rest);

  form.schema = schema;
};

// The row editor is loaded on demand, so wait for it to be registered
customElements.whenDefined("hui-generic-entity-row-editor").then(() => {
  const RowEditor = customElements.get("hui-generic-entity-row-editor");
  const originalUpdated = RowEditor.prototype.updated;

  RowEditor.prototype.updated = function (changed) {
    originalUpdated?.call(this, changed);
    addRowFields(this);
  };
});
