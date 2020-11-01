import pathlib


def make_dir(path):
    pathlib.Path(path).mkdir(parents=True, exist_ok=True)


def split_list(list, x):
    return [list[i : i + x] for i in range(0, len(list), x)]


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
