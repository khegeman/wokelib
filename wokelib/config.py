"""

Load settings for for flows from a toml file. 

"""


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
    """_summary_

    Args:
        class_ (str): FuzzTest name
        fn (str): Function name
        param (str): parameter name

    Returns:
        Any : value saved in the config file for that parameter
    """
    return config(f"{class_}.flows.{fn}.{param}", {})
