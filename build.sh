#!/bin/bash

# Function to display usage information
show_help() {
    echo "Usage: $0 --platform <platform>"
    echo "Supported platforms:"
    echo "  - windows"
    echo "  - linux"
    echo "  - macos-arm"
    echo "  - macos-x64"
    exit 1
}

setup_venv() {
    local platform=$1
    echo "Setting up Python virtual environment for $platform..."
    
    # Check if Python is installed
    local python_cmd
    if [ "$platform" = "windows" ]; then
        python_cmd="python"
    else
        python_cmd="python3"
    fi

    if ! command -v $python_cmd >/dev/null 2>&1; then
        echo "Error: Python ($python_cmd) is not installed or not in PATH"
        exit 1
    fi

    # Create virtual environment directory if it doesn't exist
    VENV_DIR="venv"
    if [ ! -d "$VENV_DIR" ]; then
        echo "Creating virtual environment..."
        $python_cmd -m venv "$VENV_DIR"
        
        if [ $? -ne 0 ]; then
            echo "Error: Failed to create virtual environment"
            exit 1
        fi
    else
        echo "Virtual environment already exists at $VENV_DIR"
    fi

    # Activate virtual environment based on platform
    echo "Activating virtual environment..."
    if [ "$platform" = "windows" ]; then
        . "$VENV_DIR/Scripts/activate"
    else
        . "$VENV_DIR/bin/activate"
    fi
    
    echo "Installing pyinstaller..."
    pip install -q pyinstaller
}

# Function to validate and process platform
handle_platform() {
    case "$1" in
        windows)
            echo "Building for Windows..."
            # Add Windows-specific commands here
            setup_venv "windows"
            cd win-ax
            pyinstaller --onefile dump-tree.py
            cd ..
            mkdir -p target/windows-x64
            cp win-ax/dist/dump-tree.exe target/windows-x64/
            echo "Build finished. Output in $(pwd)/target/windows-x64"
            ;;
        linux)
            echo "Building for Linux..."
            # Add Linux-specific commands here
            cd linux-ax
            npm install
            npm run build
            cd ..
            mkdir -p target/linux-x64
            cp linux-ax/dist/dump-tree.js target/linux-x64/
            echo "Build finished. Output in $(pwd)/target/linux-x64-arm64"
            ;;
        macos-arm)
            echo "Building for macOS ARM..."
            # Add macOS ARM-specific commands here
            setup_venv "macos"
            # install macapptree
            cd mac-ax/macapptree
            pip uninstall -q -y macapptree
            pip install -q -r requirements.txt
            cd ..
            # install script reqs
            pip install -q -r requirements.txt
            # build & copy to target
            pyinstaller \
                --add-data "./macapptree/macapptree:macapptree" \
                --onefile \
                --target-arch arm64\
                dump-tree.py
            cd ..
            mkdir -p target/macos-arm64
            cp mac-ax/dist/dump-tree target/macos-arm64/
            echo "Build finished. Output in $(pwd)/target/macos-arm64"
            ;;
        macos-x64)
            # Add macOS x64-specific commands here
            setup_venv "macos"
            # install macapptree
            cd mac-ax/macapptree
            pip uninstall -q -y macapptree
            pip install -q -r requirements.txt
            cd ..
            # install script reqs
            pip install -q -r requirements.txt
            # build & copy to target
            pyinstaller \
                --add-data "./macapptree/macapptree:macapptree" \
                --onefile \
                --target-arch x86_64\
                dump-tree.py
            cd ..
            mkdir -p target/macos-x64
            cp mac-ax/dist/dump-tree target/macos-x64/
            echo "Build finished. Output in $(pwd)/target/macos-x64"
           ;;
        *)
            echo "Error: Invalid platform specified"
            show_help
            ;;
    esac
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case "$1" in
        --platform)
            if [ -n "$2" ]; then
                PLATFORM=$2
                shift 2
            else
                echo "Error: --platform requires an argument"
                show_help
            fi
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo "Error: Unknown option $1"
            show_help
            ;;
    esac
done

# Check if platform is specified
if [ -z "$PLATFORM" ]; then
    echo "Error: Platform must be specified with --platform"
    show_help
fi

# Process the platform
handle_platform "$PLATFORM"