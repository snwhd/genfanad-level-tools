#!/usr/bin/env python3
import argparse
import pprint
import json
import shutil
import os

ROOT_DIR = '../old/GenfanadClient/resources/app/static-files/'
MODELS_JSON = os.path.join(ROOT_DIR, 'models.json')
MODELS_DIR = os.path.join(ROOT_DIR, 'models')

OUTDIR = "models"
DEFNS_DIR = os.path.join(OUTDIR, 'definitions')


def model_path(model):
    return os.path.join(MODELS_DIR, model)


def copy_model(name, data):
    dollar = name.startswith('$')
    if dollar:
        name = name[1:]

    parts = name.split('-')
    if name.endswith('_placeholder'):
        return False
    assert len(parts) > 1, name

    directory = os.path.join(DEFNS_DIR, *parts[:-1])
    os.makedirs(directory, exist_ok=True)
    filename = parts[-1]

    defn = dict(data)
    texture_to_copy = None
    if 'texture' in defn:
        # TODO: check if sharedTexture != texture
        value = defn['texture']
        if value.startswith('imported/'):
            defn['texture'] = value.split('/', 1)[1]
            texture_to_copy = os.path.join(MODELS_DIR, value);
    elif 'sharedTexture' in defn:
        defn['texture'] = 'shared-textures/' + data['sharedTexture']

    if dollar:
        defn['dollar'] = True

    ext = data['model'].split('.')[-1]
    modelname = filename + '.' + ext
    defn['model'] = modelname

    source_model = os.path.join(MODELS_DIR, data['model'])
    modelpath = os.path.join(directory, modelname)

    if not os.path.exists(source_model):
        return

    # os.symlink(source_model, modelpath)
    shutil.copy2(source_model, modelpath)

    if texture_to_copy is not None:
        texture_dest = os.path.join(directory, defn['texture'])
        if not os.path.exists(texture_dest):
            shutil.copy2(texture_to_copy, texture_dest)

    defn_path = os.path.join(directory, filename) + '.json'
    json.dump(defn, open(defn_path, 'w'), indent=2)
    return True


def main():
    os.makedirs(OUTDIR, exist_ok=True)
    defns = json.load(open(MODELS_JSON))
    for k, v in defns.items():
        try:
            copy_model(k, v)
        except Exception as e:
            print(f'error on {k}')
            pprint.pprint(v)
            raise e


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=False, default='models')
    args = parser.parse_args()

    OUTDIR = args.output
    DEFNS_DIR = os.path.join(OUTDIR, 'definitions')

    main()
