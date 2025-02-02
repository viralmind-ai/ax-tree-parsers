import argparse
import sys
from pywinauto.application import Application
from pywinauto.findwindows import find_windows
import json

def is_valid_window(control):
    """Additional validation for windows if needed"""
    try:
        return (control.is_visible() and 
                control.element_info.name and 
                control.element_info.control_type)
    except:
        return False

def safe_get_value(control):
    """Safely get control value"""
    try:
        if hasattr(control, 'get_value'):
            return control.get_value()
        return ''
    except:
        return ''

def get_element_info(control):
    if not is_valid_window(control):
        return None
        
    try:
        rect = control.rectangle()
        bbox = {
            "x": rect.left,
            "y": rect.top,
            "width": rect.width(),
            "height": rect.height()
        }
        
        element = {
            "name": control.element_info.name or '',
            "role": control.element_info.control_type or '',
            "description": getattr(control.element_info, 'description', ''),
            "value": safe_get_value(control),
            "bbox": bbox,
            "children": []
        }
        
        for child in control.children():
            child_info = get_element_info(child)
            if child_info:
                element["children"].append(child_info)
        
        return element
        
    except Exception as e:
        print(f"Error processing element: {e}", file=sys.stderr)
        return None

def get_all_windows_accessibility_tree():
    # Get all visible top-level windows
    windows = find_windows(visible_only=True)
    tree = []
    
    for win_handle in windows:
        try:
            # Connect to each window using UI Automation
            app = Application(backend="uia").connect(handle=win_handle)
            window = app.window(handle=win_handle)
            
            if window.is_visible():
                window_info = get_element_info(window)
                if window_info:
                    tree.append(window_info)
                    
        except Exception as e:
            print(f"Failed to process window: {e}", file=sys.stderr)
            continue
    
    return tree

def save_accessibility_tree(output_file=None):
    tree = get_all_windows_accessibility_tree()
    
    # Convert tree to JSON string with consistent formatting
    json_output = json.dumps(tree, indent=2, ensure_ascii=False)
    
    if output_file:
        # Write to file if output path is specified
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
        except IOError as e:
            print(f"Error writing to file {output_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        # Write to stdout if no file specified
        print(json_output)
    
    return tree

def main():
    parser = argparse.ArgumentParser(description='Generate accessibility tree for visible windows')
    parser.add_argument('-o', '--out', 
                        help='Output file path. If not specified, prints to stdout',
                        type=str,
                        default=None)
    
    args = parser.parse_args()
    
    try:
        save_accessibility_tree(args.out)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()