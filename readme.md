# Accessibility Tree Parsers

This repository contains scripts to extract the accessibility trees from three of the more popular operating system desktops.

All scripts output a JSON tree with the following format.

```json
[
  {
    "name": "Application Name",
    "tree": {
      "name": "item_name",
      "role": "item_role",
      "description": "item_desc",
      "value": "item_value",
      "bbox": ["x", "y", "width", "height"],
      "children": ["new_tree_item"]
    }
  }
]
```

## atspi - (GNOME: [atspi-2](https://docs.gtk.org/atspi2/))

## mac-at - (MacOS: [Accessibility](https://developer.apple.com/documentation/accessibility))

## win-at - (Windows: [UIA](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-overview))
