# Mac-AT: MacOS Accessibility Tree Parser

The MacOS accessibility parser uses a modified version of [macapptree](https://github.com/MacPaw/macapptree) (found in the `macapptree` directory) to parse the tree.

## Setup

Install `macapptree` and dependencies using your preferred python environment:

```bash
cd macapptree
pip3 install -r requirements.txt
pip3 install -e .
```

Run the script

```bash
python3 run.py
```

The tree will output in `tree.json` with the following structure:

```json
[
  {
    {
    "application": "Code",
    "tree": {
      "id": "11lfkmfi3930fjfkdnf39",
      "name": "run.py",
      "role": "AXWindow",
      "description": null,
      "role_description": "standard window",
      "value": null,
      "absolute_position": "0.00;44.00",
      "position": "0.00;0.00",
      "size": "1800;1125",
      "enabled": true,
      "bbox": [
        0,
        0,
        1800,
        1125
      ],
      "visible_bbox": [
        0,
        0,
        1800,
        1125
      ],
      "children": []
    },
  }
]
```
