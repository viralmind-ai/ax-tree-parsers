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

### Windows Binary

```powershell
cd win-ax
pip install pyinstaller
pyinstaller --onefile dump-tree.py
# Binary will be in win-ax/dist/dump-tree.exe
# Copy to target directory
mkdir -p ../target/windows-x64
cp dist/dump-tree.exe ../target/windows-x64/
```

### Linux Binary

The Linux implementation uses GJS (GNOME JavaScript) with GNOME-specific dependencies (atspi-2.0, etc.). Due to these system-level dependencies, it cannot be compiled into a fully standalone binary. Instead, the compiled JavaScript should be run with GJS:

```bash
cd linux-ax
npm install
npm run build
# The compiled file will be in dist/dump-tree.js
# Copy to target directory
mkdir -p ../target/linux-x64
cp dist/dump-tree.js ../target/linux-x64/
```

To run the Linux binary, GJS and the GNOME dependencies must be installed:

```bash
sudo apt-get install gjs gobject-introspection libgirepository1.0-dev
gjs -m target/linux-x64/dump-tree.js
```

### macOS Binaries

For Intel Macs:

```bash
cd mac-ax
pip install pyinstaller
pyinstaller --add-data "macapptree/macapptree:macapptree" --hidden-import macapptree --onefile --target-arch x86_64 dump-tree.py
# Binary will be in mac-ax/dist/dump-tree
# Copy to target directory
mkdir -p ../target/macos-x64
cp dist/dump-tree ../target/macos-x64/
```

For Apple Silicon Macs:

```bash
cd mac-ax
pip install pyinstaller
pyinstaller --add-data "macapptree/macapptree:macapptree" --hidden-import macapptree --onefile --target-arch arm64 dump-tree.py
# Binary will be in mac-ax/dist/dump-tree
# Copy to target directory
mkdir -p ../target/macos-arm64
cp dist/dump-tree ../target/macos-arm64/
```

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

### Usage

1. Make sure you have all dependencies installed.

    ```bash
      sudo apt-get install \
        build-essential git \
        gobject-introspection \
        libgirepository1.0-dev \
        libcairo2 \
        libcairo2-dev
    ```

If using from a release, once dependencies are installed, run `gjs -m dump-tree.js` and ignore the rest of the steps.

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

### Usage

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

### Usage

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
