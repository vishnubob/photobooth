#!/usr/bin/env python

import argparse
from photobooth.service import display, presence
from photobooth import Factory, load_config

def cli():
    parent_parser = argparse.ArgumentParser(description="Photobooth")
    #parent_parser.add_argument("service", help="which service to use")
    parent_parser.add_argument("-c", "--config", default="photobooth.json", help="Path to config file")
    services_parser = parent_parser.add_subparsers(help="services help", dest="service")

    # photobooth
    photobooth_parser = services_parser.add_parser("photobooth", help="photobooth help")

    # display
    display_parser = services_parser.add_parser("display", help="display help")
    display_parser.add_argument("-d", "--dummy", action="store_true", default=False, help="Use dummy mode")

    # presence
    presence_parser = services_parser.add_parser("presence", help="presence help")
    presence_parser.add_argument("-m", "--mode", dest="driver", choices=["dummy", "pir"], help="Use dummy mode")

    return parent_parser.parse_args()

def main(args):
    load_config(args.config)
    print(args)
    if args.service == "photobooth":
        factory = Factory()
        booth = factory.build_photobooth()
        booth.run()
    elif args.service == "display":
        display.run(dummy=args.dummy)
    elif args.service == "presence":
        presence.run(driver=args.driver)

if __name__ == "__main__":
    args = cli()
    main(args)
