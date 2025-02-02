# Win-AX: Windows Accessibility Tree Parser

The Windows accessibility parser uses the [pywinauto](https://github.com/pywinauto/pywinauto) library to parse the windows UI Automation tree.

## Setup

Install `pywinauto` and dependencies using your preferred python environment:

```bash
pip3 install -r requirements.txt
```

Run the script. Remove `-o` to output to stdout.

```bash
python3 dump-tree.py -o out.json
```

The tree will output in `out.json` with the following structure:

```json
[
  {
    "name": "Windows PowerShell",
    "role": "Window",
    "description": "",
    "value": "",
    "bbox": {
      "x": -7,
      "y": 805,
      "width": 1733,
      "height": 594
    },
    "children": []
  }
]
```
