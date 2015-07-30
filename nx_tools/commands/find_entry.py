import click
import os

from .. import utils
from ..constants import HISTORY_PATH


@click.command('find_entry', short_help="Used internally by the Identifier.")
@click.argument('pid', nargs=1, type=click.INT)
def cli(pid):
    records = utils.load_json(HISTORY_PATH)
    for entry in records.itervalues():
        try:
            entry_pid = entry["PID"]
        except TypeError:
            continue
        if int(entry_pid) == pid:
            break
    else:
        print("Could not find entry with PID %s" % pid)
        return

    ret = {}
    ret["BUILD"] = os.path.basename(entry["build"])
    ret["PATCH"] = os.path.basename(entry["patch"])
    ret["NX VERSION"] = entry["nx_version"]
    name = entry["name"]
    if name:
        ret["NAME"] = name

    for k, v in ret.iteritems():
        print("%s: %s" % (k, v))
