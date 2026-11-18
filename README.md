# Handy Types

Adds the extra row types of the entities card as real entities, so you can pick
them from the entity list in the dashboard editor instead of writing YAML.

Pick **Divider** from the list and you get the same result as:

```yaml
- type: divider
```

## What you get

| Entity | Same as | Added how |
| --- | --- | --- |
| Divider | `type: divider` | Automatic |
| Spacer | An empty gap between rows | Automatic |
| Section | `type: section` with a label | Add from the integration page |
| Text row | `type: text` with a label and text | Add from the integration page |
| Web link | `type: weblink` with a label, URL and icon | Add from the integration page |

All entities use the `ht.` prefix (for example `ht.divider`), so typing `ht` in the
entity picker filters down to them. They show with clean names such as Divider and
Spacer.

## Install

1. Open the Marketplace and add this repository as a custom repository
   (type: Integration).
2. Download **Handy Types** and restart Home Assistant.
3. Go to **Settings > Devices & services > Add integration** and add
   **Handy Types**.
4. Hard refresh your browser once so the frontend module loads.

For a manual install, copy `custom_components/handytypes` into your
`custom_components` folder and restart.

## Use

1. Edit an **Entities** card.
2. Add an entity and type `ht` to filter, then choose Divider, Spacer, or one of
   your own items.

To add a section, text row or web link, open the Handy Types integration page and
use the add buttons. Each item becomes its own entity named after its label, and
can be edited from the same page.

## Notes

- Works in the **Entities** card only. Other cards do not use row types.
- The rows are swapped in when the card renders, so the entity must exist and the
  frontend module must be loaded (hard refresh after installing).
- These are state-only entities: they can't be renamed or edited from the entity
  settings page. Edit sections, text rows and web links from the integration page.
- Editing an item reloads the integration; refresh the dashboard to see it.

## Licence

See [LICENSE](LICENSE).
