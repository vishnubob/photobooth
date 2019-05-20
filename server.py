#!/usr/bin/env python

import argparse
from photobooth.gfx import server
from photobooth import Factory

def cli():
    parser = argparse.ArgumentParser(description="Photobooth")
    parser.add_argument("-c", "--config", help="Path to config file")
    return parser.parse_args()

def main(args):
    factory = Factory(args.config)
    server.run()

if __name__ == "__main__":
    args = cli()
    main(args)
