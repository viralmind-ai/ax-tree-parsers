import Atspi from "@girs/atspi-2.0";
import Gio from "@girs/gio-2.0";
import GLib from "@girs/glib-2.0";

function getLabel(accessible: Atspi.Accessible) {
  const relationSet = accessible.get_relation_set();
  if (!relationSet) return null;

  for (let relation of relationSet) {
    if (relation.get_relation_type() === Atspi.RelationType.LABELLED_BY)
      return relation.get_target(0).get_name();
  }

  return null;
}

function formatInfo(accessible: Atspi.Accessible) {
  let name = accessible.get_name();
  if (!name) name = getLabel(accessible);
  const roleName = accessible.get_role_name()!;
  const description = accessible.get_description()!;

  const bbox = {
    x: 0,
    y: 0,
    width: 0,
    height: 0,
  };
  if (accessible.get_component) {
    const rect: Atspi.Rect = (
      accessible.get_component() as Atspi.Component
    ).get_extents(Atspi.CoordType.SCREEN);
    bbox.x = rect.x;
    bbox.y = rect.y;
    bbox.width = rect.width;
    bbox.height = rect.height;
  }

  return `(${name}, ${roleName}, ${description}, ${JSON.stringify(bbox)})`;
}

function dumpNodeContent(node: Atspi.Accessible, padding: string) {
  let newPadding = padding + "  ";

  const nodeInfo = formatInfo(node);

  out += padding + nodeInfo + "\n";

  for (let i = 0; i < node.get_child_count(); i++) {
    const child: Atspi.Accessible | null = node.get_child_at_index(i);

    if (!child) continue;

    if (child.get_state_set().contains(Atspi.StateType.VISIBLE))
      dumpNodeContent(child, newPadding);
  }
}

let out = "";
async function main() {
  Atspi.init();

  const desktop = Atspi.get_desktop(0);
  for (let i = 0, app; (app = desktop.get_child_at_index(i)); i++) {
    dumpNodeContent(app, "  ");
  }
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

main().then(async () => {
  try {
    const file = Gio.File.new_for_path("out.txt");
    const enc = new TextEncoder();
    const bytes = new GLib.Bytes(enc.encode(out));

    // Using the synchronous version for simplicity
    const [success, etag] = file.replace_contents(
      //@ts-ignore
      bytes.get_data(),
      null, // etag
      false, // make_backup
      Gio.FileCreateFlags.REPLACE_DESTINATION,
      null // cancellable
    );

    if (success) {
      print("File written successfully");
    }
  } catch (error) {
    print(`Error writing file: ${(error as Error).message}`);
  }
});
