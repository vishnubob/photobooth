#!/usr/bin/env python

import argparse
from photobooth.display import service
from photobooth import Factory

def cli():
    parser = argparse.ArgumentParser(description="Photobooth")
    parser.add_argument("-c", "--config", help="Path to config file")
    parser.add_argument("-d", "--dummy", action="store_true", default=False, help="Use dummy mode")
    return parser.parse_args()

def main(args):
    factory = Factory(args.config)
    service.run(dummy=args.dummy)

if __name__ == "__main__":
    args = cli()
    main(args)
