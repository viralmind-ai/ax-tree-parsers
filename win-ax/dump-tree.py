import argparse
import sys
import time
import pywinauto
from pywinauto.application import Application
from pywinauto import Desktop
import json
import threading
from functools import wraps
import atexit
from concurrent.futures import ThreadPoolExecutor, as_completed
import win32gui
import win32api
from ctypes.wintypes import tagPOINT

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

def get_control_value(control):
    """Get control value trying multiple methods"""
    value = ''
    
    # Try different value getters
    value_getters = [
        lambda: control.get_value(),
        lambda: control.value(),
        lambda: control.get_position(),
        lambda: control.window_text() if control.window_text() != control.element_info.name else ''
    ]
    
    for getter in value_getters:
        try:
            val = getter()
            if val:
                value = str(val)
                break
        except:
            continue
            
    return value

def get_control_states(control):
    """Get all available control states"""
    states = {}
    
    state_checks = [
        ("enabled", "is_enabled"),
        ("visible", "is_visible"),
        ("focused", "is_focused"),
        ("minimized", "is_minimized"),
        ("maximized", "is_maximized"),
        ("collapsed", "is_collapsed"),
        ("expanded", "is_expanded"),
        ("selected", "is_selected"),
        ("checked", "is_checked"),
        ("checkable", "is_checkable"),
        ("editable", "is_editable"),
        ("pressable", "is_pressable"),
        ("pressed", "is_pressed"),
        ("keyboard_focusable", "is_keyboard_focusable"),
        ("keyboard_focused", "is_keyboard_focused"),
        ("selection_required", "is_selection_required")
    ]
    
    for state_name, func_name in state_checks:
        try:
            if hasattr(control, func_name):
                states[state_name] = getattr(control, func_name)()
        except:
            continue
            
    return states

# warning: this seems to modify window focus
def get_control_properties(control):
    """Get additional control properties"""
    props = {}
    
    def serialize_value(val):
        """Convert value to JSON serializable format"""
        if hasattr(val, '_fields_'):  # Handle ctypes structures like RECT
            return str(val)
        elif isinstance(val, (bool, int, float, str)):
            return val
        elif val is None:
            return None
        else:
            return str(val)
    
    # Try to get all properties
    try:
        base_props = control.get_properties()
        for key, value in base_props.items():
            try:
                props[key] = serialize_value(value)
            except:
                continue
    except:
        # Fallback to getting writable properties only
        try:
            orig_class = control.__class__
            class TempElement(control.__class__):
                writable_props = pywinauto.base_wrapper.BaseWrapper.writable_props
            control.__class__ = TempElement
            base_props = control.get_properties()
            control.__class__ = orig_class
            
            for key, value in base_props.items():
                try:
                    props[key] = serialize_value(value)
                except:
                    continue
        except:
            pass
    
    # Get specific properties
    property_getters = {
        "control_id": lambda: control.control_id() if hasattr(control, "control_id") else None,
        "automation_id": lambda: control.element_info.automation_id,
        "class_name": lambda: control.class_name(),
        "control_count": lambda: control.control_count() if hasattr(control, "control_count") else None,
        "handle": lambda: control.handle,
    }
    
    for prop_name, getter in property_getters.items():
        try:
            value = getter()
            if value is not None:
                props[prop_name] = serialize_value(value)
        except:
            continue
            
    return props

def get_element_info(control, executor=None, path=''):
    """Get comprehensive element information using a queue-based approach"""
    from collections import deque
    
    try:
        # Initialize queue and result tree
        queue = deque([(control, None)])  # (control, parent_id) pairs
        elements = {}
        next_id = 0
        
        while queue:
            current_control, parent_id = queue.popleft()
            current_id = next_id
            next_id += 1
            
            try:
                # Get basic info
                try:
                    rect = current_control.rectangle()
                    bbox = {
                        "x": rect.left,
                        "y": rect.top,
                        "width": rect.width(),
                        "height": rect.height()
                    }
                except Exception as e:
                    print(f"Error getting rectangle: {e}", file=sys.stderr)
                    bbox = {"x": 0, "y": 0, "width": 0, "height": 0}
                
                # Build element info
                element = {
                    "name": current_control.element_info.name or '',
                    "role": current_control.element_info.control_type or '',
                    "description": getattr(current_control.element_info, 'description', ''),
                    "value": get_control_value(current_control),
                    "bbox": bbox,
                    "states": get_control_states(current_control),
                    "children": []
                }
                
                # Store element and update parent's children list
                elements[current_id] = element
                if parent_id is not None:
                    elements[parent_id]["children"].append(element)
                
                # Add children to queue
                try:
                    children = current_control.children()
                    for child in children:
                        queue.append((child, current_id))
                except Exception as e:
                    print(f"Error processing children: {e}", file=sys.stderr)
                    
            except Exception as e:
                print(f"Error processing control: {e}", file=sys.stderr)
                continue
        
        # Return root element if we processed anything
        return elements[0] if elements else None
        
    except Exception as e:
        print(f"Error in get_element_info: {e}", file=sys.stderr)
        return None

def get_all_windows_accessibility_tree(timeout_seconds=5, max_workers=None):
    """Get accessibility tree using Desktop to enumerate windows"""
    try:
        desktop = Desktop(backend="uia")
        tree = []
        
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for window in desktop.windows():
                if not window.is_visible():
                    continue
                    
                @timeout(timeout_seconds)
                def process_window(w):
                    return get_element_info(w)
                
                try:
                    futures.append(executor.submit(process_window, window))
                except Exception as e:
                    print(f"Error submitting window task: {e}", file=sys.stderr)
            
            for future in as_completed(futures):
                try:
                    window_info = future.result()
                    if window_info:
                        tree.append(window_info)
                except TimeoutError:
                    print(f"Timeout processing window after {timeout_seconds} seconds", file=sys.stderr)
                except Exception as e:
                    print(f"Error processing window: {e}", file=sys.stderr)
        
        return tree
    except Exception as e:
        print(f"Error getting desktop windows: {e}", file=sys.stderr)
        return []

def get_focused_element():
    """Get the currently focused element"""
    try:
        focused = pywinauto.uia_defines.IUIA().iuia.GetFocusedElement()
        element_info = pywinauto.uia_element_info.UIAElementInfo(focused)
        wrapper = pywinauto.controls.uiawrapper.UIAWrapper(element_info)
        return get_element_info(wrapper)
    except:
        print("Failed to get focused element", file=sys.stderr)
        return None

def get_element_at_position(x, y):
    """Get element at specific screen coordinates"""
    try:
        elem = pywinauto.uia_defines.IUIA().iuia.ElementFromPoint(tagPOINT(x, y))
        element_info = pywinauto.uia_element_info.UIAElementInfo(elem)
        wrapper = pywinauto.controls.uiawrapper.UIAWrapper(element_info)
        return {
            "position": {"x": x, "y": y},
            "element": get_element_info(wrapper)
        }
    except:
        print(f"Failed to get element at ({x}, {y})", file=sys.stderr)
        return {
            "position": {"x": x, "y": y},
            "element": None
        }

def get_cursor_element():
    """Get element under the cursor"""
    x, y = win32api.GetCursorPos()
    return get_element_at_position(x, y)

def get_random_screen_points():
    """Get two random points on the primary monitor"""
    monitor = win32api.GetMonitorInfo(win32api.MonitorFromPoint((0,0)))
    monitor_area = monitor.get("Monitor")
    width = monitor_area[2] - monitor_area[0]
    height = monitor_area[3] - monitor_area[1]
    
    import random
    points = []
    for _ in range(2):
        x = random.randint(0, width-1)
        y = random.randint(0, height-1)
        points.append(get_element_at_position(x, y))
    return points

def save_accessibility_tree(output_file=None, timeout=5, max_workers=None, event_format=False):
    start_time = int(time.time() * 1000)  # JS equivalent of timestamp_millis
    
    # Get focused element
    focused = get_focused_element()
    
    # Get element queries
    cursor = get_cursor_element()
    random_points = get_random_screen_points()
    
    # Combine all queries with enumerated random points
    queries = {
        "cursor": cursor,
        "random1": random_points[0],
        "random2": random_points[1]
    }

    # Get main tree last (slowest)
    tree = get_all_windows_accessibility_tree(timeout, max_workers)
    
    end_time = int(time.time() * 1000)
    duration = end_time - start_time
    
    if event_format:
        output = {
            "time": start_time,
            "data": {
                "duration": duration,
                "tree": tree,
                "focused_element": focused,
                "queries": queries
            }
        }
    else:
        output = {
            "tree": tree,
            "focused_element": focused,
            "queries": queries
        }
    
    # Ensure all strings are properly encoded
    def clean_string(s):
        if isinstance(s, str):
            return s.encode('utf-8', errors='ignore').decode('utf-8')
        return s

    def clean_dict(d):
        if isinstance(d, dict):
            return {k: clean_value(v) for k, v in d.items()}
        return d

    def clean_list(l):
        if isinstance(l, list):
            return [clean_value(v) for v in l]
        return l

    def clean_value(v):
        if isinstance(v, str):
            return clean_string(v)
        elif isinstance(v, dict):
            return clean_dict(v)
        elif isinstance(v, list):
            return clean_list(v)
        return v

    # Clean the output data
    output = clean_value(output)
    
    # Convert to JSON with ASCII-only encoding
    json_output = json.dumps(output, ensure_ascii=True)
    
    if output_file:
        try:
            with open(output_file, 'w', encoding='ascii') as f:
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
                      help='Maximum time in seconds to spend processing each window (default: 5)',
                      type=float,
                      default=5)
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
