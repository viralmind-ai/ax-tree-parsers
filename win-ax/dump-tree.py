import argparse
import sys
from pywinauto.application import Application
from pywinauto.findwindows import find_windows
import json

def safe_get_value(control):
    """Safely get control value from various patterns"""
    try:
        if hasattr(control, 'get_value'):
            return control.get_value()
        return ''
    except:
        return ''

def is_valid_window(control):
    """Additional validation for windows if needed"""
    try:
        is_valid = (control.element_info.name is not None and
                   control.element_info.control_type is not None)
        if is_valid:
            # Only print for significant controls like windows, panes, buttons
            significant_types = {
                'AppBar',
                'Button',
                'Calendar',
                'CheckBox',
                'ComboBox',
                'DataGrid',
                'DataItem',
                'Edit',
                'Group',
                'Header',
                'HeaderItem',
                'Hyperlink',
                'Image',
                'List',
                'ListItem',
                'Menu',
                'MenuBar',
                'MenuItem',
                'Pane',
                'ProgressBar',
                'RadioButton',
                'ScrollBar',
                'SemanticZoom',
                'Separator',
                'Slider',
                'Spinner',
                'SplitButton',
                'StatusBar',
                'Tab',
                'TabItem',
                'Table',
                'Thumb',
                'TitleBar',
                'ToolBar',
                'ToolTip',
                'Tree',
                'TreeItem',
                'Window'
            }
            if control.element_info.control_type in significant_types:
                is_valid = True
            else:
                is_valid = False
        return is_valid
    except Exception as e:
        print(f"Validation error: {e}", file=sys.stderr)
        return False

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
        print(f"Error processing {control.element_info.control_type} '{control.element_info.name}': {e}", file=sys.stderr)
        return None

def get_all_windows_accessibility_tree():
    windows = find_windows(visible_only=False)
    tree = []
    
    for win_handle in windows:
        try:
            app = Application(backend="uia").connect(handle=win_handle)
            window = app.window(handle=win_handle)
            
            window_info = get_element_info(window)
            if window_info:
                tree.append(window_info)
                
        except Exception as e:
            print(f"Failed to process window {win_handle}: {e}", file=sys.stderr)
            continue
    
    return tree

def save_accessibility_tree(output_file=None):
    tree = get_all_windows_accessibility_tree()
    
    json_output = json.dumps(tree, ensure_ascii=False)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
            # Silently succeed when writing to file
        except IOError as e:
            print(f"Error writing to file {output_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json_output)
    
    return tree

def main():
    parser = argparse.ArgumentParser(description='Generate accessibility tree for all windows')
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