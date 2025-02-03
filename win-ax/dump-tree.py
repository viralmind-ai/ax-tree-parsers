import argparse
import sys
import time
from pywinauto.application import Application
from pywinauto.findwindows import find_windows
import json
import threading
from functools import wraps
import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed

# Track active threads for cleanup
active_threads = []

def cleanup_threads():
    """Clean up any active threads on program exit"""
    for thread in active_threads:
        if thread.is_alive():
            thread.join(0)  # Non-blocking join

atexit.register(cleanup_threads)

def timeout(seconds):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = [TimeoutError('Timed out')]
            def worker():
                try:
                    result[0] = func(*args, **kwargs)
                except Exception as e:
                    result[0] = e
            thread = threading.Thread(target=worker)
            thread.daemon = True
            active_threads.append(thread)
            thread.start()
            thread.join(seconds)
            if thread in active_threads:
                active_threads.remove(thread)
            if isinstance(result[0], Exception):
                raise result[0]
            return result[0]
        return wrapper
    return decorator

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
        print(f"Validation error for control {getattr(control, 'element_info', {}).get('name', 'unknown')}: {e}", file=sys.stderr)
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

def process_single_window(win_handle, timeout_seconds, index, total):
    """Process a single window with timeout"""
    try:
        @timeout(timeout_seconds)
        def process_window_with_timeout(handle):
            app = Application(backend="uia").connect(handle=handle)
            window = app.window(handle=handle)
            return get_element_info(window)
        
        window_info = process_window_with_timeout(win_handle)
        if window_info:
            return window_info
                
    except TimeoutError:
        print(f"Timeout processing window handle {win_handle} after {timeout_seconds} seconds", file=sys.stderr)
    except Exception as e:
        print(f"Failed to process window {win_handle}: {e}", file=sys.stderr)
    
    return None

def get_all_windows_accessibility_tree(timeout_seconds=1, max_workers=None):
    windows = find_windows(visible_only=True)
    total_windows = len(windows)
    tree = []
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_window = {
            executor.submit(
                process_single_window, 
                win_handle, 
                timeout_seconds,
                i + 1,
                total_windows
            ): win_handle 
            for i, win_handle in enumerate(windows)
        }
        
        for future in as_completed(future_to_window):
            win_handle = future_to_window[future]
            try:
                window_info = future.result()
                if window_info:
                    tree.append(window_info)
            except Exception as e:
                print(f"Window {win_handle} generated an exception: {e}", file=sys.stderr)
    
    return tree

def save_accessibility_tree(output_file=None, timeout=1, max_workers=None, event_format=False):
    start_time = int(time.time() * 1000)  # JS equivalent of timestamp_millis
    tree = get_all_windows_accessibility_tree(timeout, max_workers)
    end_time = int(time.time() * 1000)
    duration = end_time - start_time
    
    if event_format:
        output = {
            "time": start_time,
            "data": {
                "duration": duration,
                "tree": tree
            }
        }
    else:
        output = tree
    
    json_output = json.dumps(output, ensure_ascii=False)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(json_output)
        except IOError as e:
            print(f"Error writing to file {output_file}: {e}", file=sys.stderr)
            sys.exit(1)
    else:
        print(json_output)
    
    return output

def main():
    parser = argparse.ArgumentParser(description='Generate accessibility tree for all windows')
    parser.add_argument('-o', '--out',
                      help='Output file path. If not specified, prints to stdout',
                      type=str,
                      default=None)
    parser.add_argument('-t', '--timeout',
                      help='Maximum time in seconds to spend processing each window (default: 1)',
                      type=float,
                      default=1)
    parser.add_argument('-w', '--workers',
                      help='Maximum number of parallel workers (default: number of CPUs * 5)',
                      type=int,
                      default=None)
    parser.add_argument('-e', '--event',
                      help='Output in event format with timing data',
                      action='store_true')
    
    args = parser.parse_args()
    
    try:
        save_accessibility_tree(args.out, args.timeout, args.workers, args.event)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
