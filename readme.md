# Accessibility Tree Parsers

This repository contains scripts to extract the accessibility trees from three of the more popular operating system desktops.

## Building Binaries

The scripts can be compiled into standalone binaries for each platform. Binaries are output to the `target` directory organized by platform and architecture:

```
target/
  windows-x64/    # Windows x64 binaries
  linux-x64/      # Linux x64 binaries
  macos-x64/      # macOS Intel binaries
  macos-arm64/    # macOS Apple Silicon binaries
```

Use the build script for your desired operating system:

```bash
./build.sh --platform windows
./build.sh --platform linux
./build.sh --platform macos-arm64
./build.sh --platform macos-x64
```

### Linux Binary

The Linux implementation uses GJS (GNOME JavaScript) with GNOME-specific dependencies (atspi-2.0, etc.). Due to these system-level dependencies, it cannot be compiled into a fully standalone binary. Instead, the compiled JavaScript should be run with GJS.

To build and run the Linux binary, GJS and the GNOME dependencies must be installed:

```bash
sudo apt-get install \
  gjs \
  build-essential git \
  gobject-introspection \
  libgirepository1.0-dev \
  libcairo2 \
  libcairo2-dev
gjs -m target/linux-x64/dump-tree.js
```

## Usage

All binaries support both file output and console output:

```bash
  ./dump-tree         # outputs to console
  ./dump-tree -o file.json  # outputs to file
```

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

## linux-ax: [GNOME Atspi-2](https://docs.gtk.org/atspi2/)

### Development

1. Make sure you have all dependencies installed.

    ```bash
    sudo apt-get install \
      gjs \
      build-essential git \
      gobject-introspection \
      libgirepository1.0-dev \
      libcairo2 \
      libcairo2-dev
    ```

2. Build the GTK+ JS file from typescript.

    ```bash
    # make sure npm deps are installed
    npm install
    npm run build
    ```

3. Run the GTK+ JS file.

    ```bash
    npm start
    ```

## mac-ax:  [MacOS Accessibility](https://developer.apple.com/documentation/accessibility)

### Development

1. Setup your virtal python env of choice.

    ```bash
    # conda
    conda create --name mac-at python=3.9
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
    python3 dump-tree.py -o tree.json
    ```

## win-ax:  [Windows UIA](https://learn.microsoft.com/en-us/dotnet/framework/ui-automation/ui-automation-overview)

### Development

1. Setup your virtal python env of choice.

    ```bash
    # conda
    conda create --name win-ax python=3.9
    conda activate win-ax
    # or others
    ```

2. Install requirements.

    ```bash
    cd win-ax
    pip3 install -r requirements.txt
    ```

3. Run the script and output to `tree.json`

    ```bash
    python3 dump-tree.py -o tree.json
    ```
