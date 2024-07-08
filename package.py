#!/usr/bin/env python3
import argparse
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
            if 'walkable' not in tile:
                tile['walkable'] = tile.get('walkabilityOverriden', True)
                tile['overall_walkable'] = tile['walkable'] # TODO what is this
            if 'walkabilityOverriden' in tile:
                del tile['walkabilityOverriden']
            if 'minimapColor' not in tile and 'color' in tile:
                tile['minimapColor'] = tile['color']
            if 'buildings' in tile and 'level1' in tile['buildings'] and 'roof' in tile['buildings']['level1']:
                tile['indoor'] = True
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


def package(w, output):
    # items = workspace_json(w, "items")
    # npcs = workspace_json(w, "npcs")
    mesh = workspace_json(w, "mesh")
    objects = workspace_json(w, "objects")
    unique = workspace_json(w, "unique")
    combined = combine(mesh, objects, unique)
    json.dump(combined, open(output, "w"), indent=2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("workspace", type=str)
    parser.add_argument("--output", type=str, required=False, default="combined.json")
    args = parser.parse_args()

    package(args.workspace, args.output)

