import Atspi from "@girs/atspi-2.0";
import Gio from "@girs/gio-2.0";
import GLib from "@girs/glib-2.0";

interface Node {
  name: string | null;
  role: string;
  description: string;
  value: string | null;
  bbox: {
    x: number;
    y: number;
    width: number;
    height: number;
  };
  children: Node[];
}

function getLabel(accessible: Atspi.Accessible) {
  const relationSet = accessible.get_relation_set();
  if (!relationSet) return null;

  for (let relation of relationSet) {
    if (relation.get_relation_type() === Atspi.RelationType.LABELLED_BY)
      return relation.get_target(0).get_name();
  }

  return null;
}

function formatInfo(accessible: Atspi.Accessible): Node {
  let name = accessible.get_name();
  if (!name) name = getLabel(accessible);
  const roleName = accessible.get_role_name()!;
  const description = accessible.get_description()!;

  const bbox: Node["bbox"] = {
    x: 0,
    y: 0,
    width: 0,
    height: 0,
  };
  try {
    // @ts-ignore
    if (accessible.get_component) {
      let coordType: Atspi.CoordType;

      switch (roleName) {
        case Atspi.Role.APPLICATION.toString():
          coordType = Atspi.CoordType.SCREEN;
          break;
        case Atspi.Role.WINDOW.toString():
          coordType = Atspi.CoordType.SCREEN;
          break;
        case Atspi.Role.FRAME.toString():
          coordType = Atspi.CoordType.WINDOW;
          break;
        default:
          coordType = Atspi.CoordType.PARENT;
          break;
      }

      const rect: Atspi.Rect = //@ts-ignore
        (accessible.get_component() as Atspi.Component)?.get_extents(coordType);
      bbox.x = rect.x;
      bbox.y = rect.y;
      bbox.width = rect.width;
      bbox.height = rect.height;
    }
  } catch (e) {
    // print(e);
  }

  return {
    name,
    role: roleName,
    description,
    value: null,
    bbox,
    children: [],
  };
}

function dumpNodeContent(node: Atspi.Accessible): Node {
  const nodeInfo = formatInfo(node);

  for (let i = 0; i < node.get_child_count(); i++) {
    const child: Atspi.Accessible | null = node.get_child_at_index(i);

    if (!child) continue;

    if (child.get_state_set().contains(Atspi.StateType.VISIBLE)) {
      nodeInfo.children.push(dumpNodeContent(child));
    }
  }

  return nodeInfo;
}

async function main(outFile: string | null) {
  Atspi.init();

  let out: Node[] = [];
  const desktop = Atspi.get_desktop(0);
  for (let i = 0, app; (app = desktop.get_child_at_index(i)); i++) {
    out.push(dumpNodeContent(app));
  }
  return out;
}

Gio._promisify(Gio.File.prototype, "copy_async");
Gio._promisify(Gio.File.prototype, "create_async");
Gio._promisify(Gio.File.prototype, "delete_async");
Gio._promisify(Gio.File.prototype, "enumerate_children_async");
Gio._promisify(Gio.File.prototype, "load_contents_async");
Gio._promisify(Gio.File.prototype, "make_directory_async");
Gio._promisify(Gio.File.prototype, "move_async");
Gio._promisify(Gio.File.prototype, "open_readwrite_async");
Gio._promisify(Gio.File.prototype, "query_info_async");
Gio._promisify(Gio.File.prototype, "replace_contents_async");
Gio._promisify(
  Gio.File.prototype,
  "replace_contents_bytes_async",
  "replace_contents_finish"
);
Gio._promisify(Gio.File.prototype, "trash_async");

/* Gio.FileEnumerator */
Gio._promisify(Gio.FileEnumerator.prototype, "next_files_async");

/* Gio.InputStream */
Gio._promisify(Gio.InputStream.prototype, "read_bytes_async");

/* Gio.OutputStream */
Gio._promisify(Gio.OutputStream.prototype, "write_bytes_async");

// Parse command line arguments
let outFile: string | null = null;
for (let i = 0; i < ARGV.length; i++) {
  if (ARGV[i] === "-o" || ARGV[i] === "--out") {
    outFile = ARGV[i + 1] || null;
    break;
  }
}

main(outFile).then(async (out) => {
  const jsonOutput = JSON.stringify(out, null, 2);

  if (outFile) {
    try {
      const file = Gio.File.new_for_path(outFile);
      const enc = new TextEncoder();
      const bytes = new GLib.Bytes(enc.encode(jsonOutput));

      // Using the synchronous version for simplicity
      const [success] = file.replace_contents(
        //@ts-ignore
        bytes.get_data(),
        null, // etag
        false, // make_backup
        Gio.FileCreateFlags.REPLACE_DESTINATION,
        null // cancellable
      );

      if (success) {
        print("Accessibility tree exported to", outFile);
      }
    } catch (error) {
      print(`Error writing file: ${(error as Error).message}`);
      process.exit(1);
    }
  } else {
    // Write to stdout by default
    print(jsonOutput);
  }
});
