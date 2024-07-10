#!/usr/bin/env python3
import argparse
import pathlib
import zipfile
import json
import os


def workspace_json(workspace, filename):
    return json.load(open(os.path.join("tmp", workspace, filename) + ".json"))


def preprocess_objects(objs):
    return objs


def preprocess_mesh(mesh):
    # blend_colors
    # buildings
    # encounter_background
    # music
    # shadow
    # texture1
    # texture2
    for row in mesh:
        for tile in row:
            if "walkable" not in tile:
                tile["walkable"] = tile.get("walkabilityOverriden", True)
                tile["overall_walkable"] = tile["walkable"] # TODO what is this
            if "walkabilityOverriden" in tile:
                del tile["walkabilityOverriden"]
            if "minimapColor" not in tile and "color" in tile:
                tile["minimapColor"] = tile["color"]
            if "buildings" in tile and "level1" in tile["buildings"] and "roof" in tile["buildings"]["level1"]:
                tile["indoor"] = True
    return mesh


def preprocess_unique(unique):
    return unique


def combine(mesh, objects, unique):
    return {
        "effects": [],
        "objects": preprocess_objects(objects),
        "mesh": preprocess_mesh(mesh),
        "uniqueObjects": preprocess_unique(unique),
        "pointsOfInterest": [],
    }


def pack_workspace(w, output):
    # items = workspace_json(w, "items")
    # npcs = workspace_json(w, "npcs")
    mesh = workspace_json(w, "mesh")
    objects = workspace_json(w, "objects")
    unique = workspace_json(w, "unique")
    combined = combine(mesh, objects, unique)
    json.dump(combined, open(output, "w"), indent=2)


def pack_attached(root, output):
    mapsdir = os.path.join(root, "maps")
    layers = os.listdir(mapsdir)
    for layer in layers:
        layerdir = os.path.join(mapsdir, layer)
        chunks = os.listdir(layerdir)
        for chunk in chunks:
            chunkdir = os.path.join(layerdir, chunk)

            mesh = json.load(open(os.path.join(chunkdir, "new_mesh", "mesh.json")))

            objects = {}
            objsdir = os.path.join(chunkdir, "objects")
            if os.path.exists(objsdir):
                for category in os.listdir(objsdir):
                    for filename in os.listdir(os.path.join(objsdir, category)):
                        if filename.endswith(".json"):
                            data = json.load(open(os.path.join(objsdir, category, filename)))
                            key = f'{layer}:{data["gx"]},{data["gy"]}'
                            objects[key] = data

            batchdir = os.path.join(chunkdir, "batch_objects")
            if os.path.exists(batchdir):
                for batchfile in os.listdir(batchdir):
                    if not batchfile.endswith(".json"):
                        continue
                    data = json.load(open(os.path.join(batchdir, batchfile)))
                    for k, v in data.items():
                        objects[k] = v

            unique = {}
            uniquesdir = os.path.join(chunkdir, "unique")
            if os.path.exists(uniquesdir):
                for filename in os.listdir(uniquesdir):
                    if filename.endswith(".json"):
                        filepath = os.path.join(uniquesdir, filename)
                        data = json.load(open(filepath))
                        pos = data["position"]
                        key = f'{pos["x"]},{pos["z"]}-{data["scenery_key"]}'
                        unique[key] = data

            combined = combine(mesh, objects, unique)

            x, y = chunk.split('_')
            outdir = pathlib.Path(output) / layer
            outdir.mkdir(parents=True, exist_ok=True)

            outfile = outdir / f'{x}_{y}.zip'
            with zipfile.ZipFile(str(outfile), "w") as zf:
                zf.writestr("combined.json", json.dumps(combined, indent=2))

            # filename = f'{layer}_{x}_{y}.combined.json'
            # output_path = os.path.join(output, filename)
            # json.dump(combined, open(output_path, "w"), indent=2)


def unpack_attached(filepath, output):

    def write(content, *filepath):
        path = pathlib.Path(os.path.join(output, *filepath))
        path.parent.mkdir(parents=True, exist_ok=True)
        json.dump(content, open(str(path), "w"), indent=2)

    def generic_write(obj, *dir):
        if obj is not None:
            for i, (k, v) in enumerate(obj.items()):
                write(v, *dir, f'{i:004}.json')

    combined = json.load(open(filepath))
    write(combined["mesh"], "new_mesh", "mesh.json")

    batches = {
        "trees": [],
    }

    for i, (k, v) in enumerate(combined["objects"].items()):
        # TODO: something better here, from workspace.writeObjects
        if k.startswith("skill-tree"):
            batches["trees"].append(v)
        else:
            category = v["object"].split("-")[0]
            filename = f'{i:04},{v["object"]}.json'
            write(v, "objects", category, filename)

    for batch, objects in batches.items():
        write(dict(enumerate(objects)), "batch_objects", f'{batch}.json')

    generic_write(combined["uniqueObjects"], "unique")
    generic_write(combined.get("items"), "items")
    generic_write(combined.get("npcs"), "npcs")


def parse_args():
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers()

    p = subparsers.add_parser("pack")
    p.add_argument("workspace", type=str)
    p.add_argument("--temporary", action='store_true')
    p.add_argument("--output", type=str, default=".")
    p.set_defaults(func=cmd_pack)

    p = subparsers.add_parser("unpack")
    p.add_argument("combined", type=str)
    p.add_argument("output", type=str)
    p.set_defaults(func=cmd_unpack)

    args = parser.parse_args()
    if not hasattr(args, "func"):
        parser.print_help()
        exit()
    return args


def cmd_pack(args):
    if args.temporary:
        pack_workspace(args.workspace, args.output)
    else:
        pack_attached(args.workspace, args.output)


def cmd_unpack(args):
    unpack_attached(args.combined, args.output)


if __name__ == "__main__":
    args = parse_args()
    args.func(args)

