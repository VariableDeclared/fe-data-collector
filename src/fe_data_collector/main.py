#!/bin/env python3

#### FE Data collector - the process improvement tool : - )
import argparse
import json
import paramiko
import subprocess

import os
this_dir, this_filename = os.path.split(__file__)
DATA_PATH = os.path.join(this_dir, "templates")
SSH_USER = "ubuntu"

def parse_args():
    parser = argparse.ArgumentParser("Collect data on deployments for analysis")
    parser.add_argument(
        "--hosts",
        action="store",
        required=False,
        default={},
        help="JSON file containing targets to scrape. Must have SSH key imported.",
    )
    parser.add_argument("--debug", action="store_true")

    return parser.parse_args()


class Command(object):
    def __init__(self, cmd_string, name) -> None:
        self._cmd = cmd_string
        self._cmdname = name

    @property
    def payload(self):
        return self._cmd

    @property
    def name(self):
        return self._cmdname


class CommandWithScript(Command):
    def __init__(self, script_payload, name) -> None:
        super().__init__(script_payload, name)

    @property
    def payload(self):
        return super().payload


SCRAPE_COMMANDS = [
    Command("lsblk -J", "lslbk"),
    # NIC Metrics
    CommandWithScript(open(os.path.join(DATA_PATH, "get_ethtool.py"), "r").read(), "ethtool"),
    Command("lshw -json", "lshw"),
]


def put_file(host, username, dirname, filename, data):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username)
    sftp = ssh.open_sftp()
    try:
        sftp.mkdir(dirname)
    except IOError:
        pass
    f = sftp.open(dirname + "/" + filename, "w")
    f.write(data)
    f.chmod(0o700)
    f.close()
    ssh.close()


def ssh(host, command):
    return subprocess.check_output(f"ssh {SSH_USER}@{host} -- {command}".split(" ")).decode('utf-8')


def main():
    args = parse_args()
    data_payload = {}
    if args.hosts:
        loaded_h = json.loads(open(args.hosts).read())
        for host in loaded_h:
            # TODO: Host could be a dictionary, in the future.
            host_payload = {host: {}}
            # TODO: Hosts should be an object on which we execute commands.
            result = ""
            for cmd in SCRAPE_COMMANDS:
                if not isinstance(cmd, CommandWithScript):
                    result = ssh(host, cmd.payload)
                else:
                    put_file(host, SSH_USER, "/tmp", f"{cmd.name}.py", cmd.payload)
                    result = ssh(host, f"/tmp/{cmd.name}.py")
                host_payload[host].update({cmd.name: result})
            data_payload.update(host_payload)
    with open("scrape.result.txt", "w") as fh:
        fh.write(json.dumps(data_payload))


if __name__ == "__main__":
    parse_args()
    main()
