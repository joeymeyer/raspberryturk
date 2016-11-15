#!/usr/bin/env python

import argparse
import os
import raspberryturk

def _raspberryturkd(subcommand):
    command = "python -m raspberryturk.embedded.raspberryturkd {}".format(subcommand)
    os.system(command)

def _start(args):
    _raspberryturkd('start')

def _stop(args):
    _raspberryturkd('stop')

def _restart(args):
    _raspberryturkd('restart')

def _status(args):
    path = raspberryturk.lib_path('status.txt')
    if args.watch:
        command = "watch -d -t -n 0.5 cat {}".format(path)
        os.system(command)
    else:
        with open(path, 'r') as f:
            print f.read()


def _get_args():
    desc = "Utility for starting and stopping the raspberryturk daemon (raspberryturkd)."
    parser = argparse.ArgumentParser(prog='raspberryturk', description=desc)
    parsers = parser.add_subparsers()
    start_parser = parsers.add_parser('start')
    start_parser.set_defaults(func=_start)
    stop_parser = parsers.add_parser('stop')
    stop_parser.set_defaults(func=_stop)
    restart_parser = parsers.add_parser('restart')
    restart_parser.set_defaults(func=_restart)
    status_parser = parsers.add_parser('status')
    status_parser.add_argument('-w', '--watch', action='store_true', \
                               help='Watch status in real time instead of just \
                               printing it once.')
    status_parser.set_defaults(func=_status)
    parser.add_argument('-v', '--version', action='version', \
                        version="%(prog)s {}".format(raspberryturk.__version__))
    return parser.parse_args()

def main():
    args = _get_args()
    assert raspberryturk.is_running_on_raspberryturk(), "Must be running on raspberryturk"
    args.func(args)

if __name__ == '__main__':
    main()
