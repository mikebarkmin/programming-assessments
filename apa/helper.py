import pathlib
import shutil
import tempfile
import os
import subprocess
from distutils.dir_util import copy_tree


def editor_input(initial_message):
    EDITOR = os.environ.get("EDITOR", "vim")
    message = initial_message.encode("utf-8")

    with tempfile.NamedTemporaryFile(suffix=".tmp") as tf:
        tf.write(message)
        tf.flush()
        subprocess.call([EDITOR, tf.name])

        tf.seek(0)
        message = tf.read()

    return message.decode("utf-8")


def make_dir(path, clean=False):
    dir_path = pathlib.Path(path)
    if clean and dir_path.exists():
        shutil.rmtree(dir_path)
    dir_path.mkdir(parents=True, exist_ok=True)


def copy_dir(source, target):
    copy_tree(source, target)


def copy_file(source, target):
    shutil.copyfile(source, target)


def split_list(list, x):
    return [list[i: i + x] for i in range(0, len(list), x)]


def is_in_dict(path, d):
    keys = path.split(".")
    value = d
    try:
        for key in keys:
            value = value[key]
    except KeyError:
        return False
    return True


def get_in_dict(path, d):
    keys = path.split(".")
    value = d
    for key in keys:
        if value[key] is None:
            value[key] = {}
        value = value[key]
    return value


def count_leaves(d):
    if isinstance(d, dict) and len(d.keys()) > 0:
        if "_meta" in d:
            del d["_meta"]

        if "file" in d:
            del d["file"]

        return sum([count_leaves(n) for n in d.values()])
    return 1
