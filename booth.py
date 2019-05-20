#!/usr/bin/env python

import argparse
from photobooth import Factory

def cli():
    parser = argparse.ArgumentParser(description="Photobooth")
    parser.add_argument("-c", "--config", help="Path to config file")
    return parser.parse_args()

def main(args):
    factory = Factory(args.config)
    booth = factory.build_photobooth()
    booth.run()

if __name__ == "__main__":
    args = cli()
    main(args)
