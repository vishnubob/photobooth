#!/usr/bin/env python

import argparse
from photobooth import load_config

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
    presence_parser.add_argument("-m", "--mode", dest="driver", choices=["dummy", "pir"], default="pir", help="presence driver")

    # stt
    stt_parser = services_parser.add_parser("stt", help="speech to text help")

    # audio
    audio_parser = services_parser.add_parser("audio", help="audio help")

    # camera
    camera_parser = services_parser.add_parser("camera", help="camera help")

    # photolab
    photolab_parser = services_parser.add_parser("photolab", help="photolab help")

    # log reader
    logreader_parser = services_parser.add_parser("log", help="log reader help")
    logreader_parser.add_argument("-w", "--watch", action="store_true", default=False, help="watch log file")

    # log reader
    projector_parser = services_parser.add_parser("projector", help="projector control help")

    return parent_parser.parse_args()

def main(args):
    load_config(args.config)
    if args.service == "photobooth":
        from photobooth import photobooth
        photobooth.run()
    elif args.service == "display":
        from photobooth.service import display
        display.run(dummy=args.dummy)
    elif args.service == "presence":
        from photobooth.service import presence
        presence.run(driver=args.driver)
    elif args.service == "camera":
        from photobooth.service import camera
        camera.run()
    elif args.service == "photolab":
        from photobooth.service import photolab
        photolab.run()
    elif args.service == "stt":
        from photobooth.service import stt
        stt.run()
    elif args.service == "audio":
        from photobooth.service import audio
        audio.run()
    elif args.service == "log":
        from photobooth.logger import LogReader
        lr = LogReader()
        lr.run()
    elif args.service == "projector":
        from photobooth.service import projector
        projector.run()

if __name__ == "__main__":
    args = cli()
    main(args)
