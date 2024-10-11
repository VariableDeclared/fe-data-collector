#!/bin/env python3

import subprocess
import json


def main():
    ip_payload = json.loads(
        subprocess.check_output("ip -j l".split(" ")).decode("utf-8")
    )
    ethstats = {}
    for inf in [nic["ifname"] for nic in ip_payload]:
        inf_stats = subprocess.run(f"ethtool --json -S {inf}".split(" "), check=False, capture_output=True).stdout.decode("utf-8")
        if "no stats available" not in inf_stats and inf_stats != "":
           json.loads(inf_stats)
        inf_module = ""
        try:
            inf_module = json.loads(subprocess.run(f"ethtool --json -m {inf}".split(" "), check=False, capture_output=True).stdout.decode("utf-8"))
        except:
            inf_module = "Exception occured"
        ethstats.update({inf: {"stats": inf_stats, "module_info": inf_module}})

    return json.dumps(ethstats)


if __name__ == "__main__":
    main()
