# Accessibility Tree Parsers

This repository contains scripts to extract the accessibility trees from three of the more popular operating system desktops.

All scripts output a JSON tree with the following format.

```json
[
  {
      "name": "item_name",
      "role": "item_role",
      "description": "item_desc",
      "value": "item_value",
      "bbox": { "x": 0, "y": 0, "width": 0 , "height": 0 },
      "children": ["new_tree_item"]
  }
]
```

## linux-at: [GNOME Atspi-2](https://docs.gtk.org/atspi2/)

### Usage

1. Make sure you have all dependencies installed.

    ```bash
      sudo apt-get install \
        build-essential git \
        gobject-introspection \
        libgirepository1.0-dev \
        libcairo2 \
        libcairo2-dev
      npm install
    ```

2. Build the GTK+ JS file from typescript.

    ```bash
      npm run build
    ```

3. Run the GTK+ JS file.

    ```bash
    npm start
    ```

## mac-at:  [MacOS Accessibility](https://developer.apple.com/documentation/accessibility)

### Usage

1. Setup your virtal python env of choice.

    ```bash
      # conda
      conda create --name mac-at python=3.12
      conda activate mac-at
      # or others
    ```

2. Install the requirements for `macapptree` and build the package.

    ```bash
      cd macapptree
      pip3 install -r requirements.txt
      pip3 install -e .
    ```

3. Run the script and output to `tree.json`

    ```bash
      cd ..
      python3 run.py tree.json
    ```

## win-at:  [Windows UIA](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-overview)
