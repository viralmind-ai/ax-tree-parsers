import json
import sys
from macapptree import get_app_bundle, get_tree

from Quartz import (
    CGWindowListCopyWindowInfo,
    kCGWindowListOptionOnScreenOnly,
    kCGNullWindowID,
    kCGWindowOwnerName,
    kCGWindowBounds
)

INVALID_WINDOWS=['Window Server', 'Notification Center']
options = kCGWindowListOptionOnScreenOnly
windowList = CGWindowListCopyWindowInfo(options, kCGNullWindowID)
# Convert windowList to a list of Python dictionaries
app_names = []
for window in windowList:
  real = False
  for key, value in window.items():
    if key == kCGWindowBounds:
      if value["Y"] > 0:
        real = True
  for key, value in window.items():
    if key == kCGWindowOwnerName and real == True:
      if value not in INVALID_WINDOWS:
        app_names.append(value)
print("Found the following open applications:", list(app_names))

out = []
for app in app_names:
  bundle = get_app_bundle(app)
  print("Collecting tree for", app)
  out.append({
    'name': app,
    'role': 'application',
    'description': '',
    'value': '',
    'bbox': {'x': 0, 'y': 0, 'width': 0, 'height': 0},
    'children': get_tree(bundle)
  })

f = open(sys.argv[1] or "out.json", "w")
f.write(json.dumps(out))
f.close()

print(f"Accessibility tree exported to {sys.argv[1] or "out.json"}")