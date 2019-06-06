#!/usr/bin/env python

import argparse
from photobooth.service import display, presence, camera, photolab
from photobooth import photobooth, load_config

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

    # camera
    camera_parser = services_parser.add_parser("camera", help="camera help")

    # photolab
    photolab_parser = services_parser.add_parser("photolab", help="photolab help")

    return parent_parser.parse_args()

def main(args):
    load_config(args.config)
    if args.service == "photobooth":
        photobooth.run()
    elif args.service == "display":
        display.run(dummy=args.dummy)
    elif args.service == "presence":
        presence.run(driver=args.driver)
    elif args.service == "camera":
        camera.run()
    elif args.service == "photolab":
        photolab.run()

if __name__ == "__main__":
    args = cli()
    main(args)
