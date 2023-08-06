import tomli


settings = {}


def load(filename: str, prefix: str):
    with open(filename, "rb") as f:
        settings[prefix] = tomli.load(f)


# simple api to get nested toml keys
def config(key: str, default=None):
    keys = key.split(".")
    r = settings
    for k in keys:
        if type(r) == dict:
            r = r.get(k, default)
        else:
            return r
    return r


def get_args(class_: str, fn: str, param: str):
    return config(f"{class_}.flows.{fn}.{param}", {})


print(get_args("FuzzTest", "flow3", "amounts"))
