import os

import requests


def check_archive(url):
    r = requests.get(os.path.join(url, "archive"))
    return not (("PAGE NOT FOUND" in r.text) and ("404" in r.text))
