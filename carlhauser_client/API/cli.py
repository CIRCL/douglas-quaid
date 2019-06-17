#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import logging.config
# ==================== ------ STD LIBRARIES ------- ====================
import os
import pathlib
import sys

# ==================== ------ PERSONAL LIBRARIES ------- ====================
sys.path.append(os.path.abspath(os.path.pardir))
from carlhauser_client.Helpers.environment_variable import get_homedir
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_server.Helpers.json_import_export import save_json, load_json

# from . import helpers

# ==================== ------ PREPARATION ------- ====================
# load the logging configuration
logconfig_path = (get_homedir() / pathlib.Path("carlhauser_client", "logging.ini")).resolve()
logging.config.fileConfig(str(logconfig_path))


# ==================== ------ LAUNCHER ------- ====================

class CLI():
    # Command line interface for client side

    def __init__(self):
        self.ext_api = Extended_API.get_api()

    def ping(self, args):
        self.ext_api.ping_server()

    def upload(self, args):
        print(f"Uploading pictures from {args.path}")
        mapping, nb = self.ext_api.add_pictures_to_db(args.path)
        print(f"{nb} pictures uploaded.")
        save_json(mapping, args.mapfile)
        print(f"Mapping file_name / Server ID saved to {args.mapfile}.")

    def request(self, args):
        results = self.ext_api.request_similar_and_wait(args.path, args.waittime)

        if args.mapfile:
            print(f"Mapping file detected. Reversing the ids ... ")
            mapping = load_json(args.mapfile)
            revert_mapping = self.ext_api.revert_mapping(mapping)
            results = self.ext_api.apply_revert_mapping(results, revert_mapping)

        save_json(results, args.resultfile)

    def dump(self, args):
        print(f"Requesting server to dump its database")
        graphe_struct = self.ext_api.get_db_dump_as_graph()
        db = graphe_struct.export_as_dict()
        # TODO : Handle it properly with graphe structure ? For now, only operation on dict
        if args.mapfile:
            print(f"Mapping file detected. Reversing the ids ... ")
            mapping = load_json(args.mapfile)
            revert_mapping = self.ext_api.revert_mapping(mapping)
            # graphe_struct.replace_id_from_mapping(mapping)
            db = self.ext_api.apply_revert_mapping(db, revert_mapping)
        if args.copyids:
            print(f"ID to image copy option detected. Copying ... ")
            db = self.ext_api.copy_id_to_image(db)
            # graphe_struct.copy_ids_to_image()
        save_json(db, args.dbfile)


def main():
    # Handle CLI calls. Define parameters for each calls, and the function to be called as reference.
    cli = CLI()

    # Top level parser
    parser = argparse.ArgumentParser(description='CLI tool to interact with douglas-quaid server')
    subparsers = parser.add_subparsers(help='help for subcommands')

    # create the parser for the "ping" command
    parser_ping = subparsers.add_parser('ping', help='Ping server')
    parser_ping.add_argument('ping', action='store_true')
    parser_ping.set_defaults(func=cli.ping)

    # create the parser for the "upload" command
    parser_upload = subparsers.add_parser('upload', help='Upload pictures to server')
    parser_upload.add_argument('upload', action='store_true')
    parser_upload.add_argument('-p', dest='path', type=lambda p: pathlib.Path(p).absolute(), action='store', help='Pictures path')
    parser_upload.add_argument('-o', dest='mapfile', type=lambda p: pathlib.Path(p).absolute(), action='store', default='./mapping', help='Mapping file path (output)')
    parser_upload.set_defaults(func=cli.upload)

    # create the parser for the "request" command
    parser_request = subparsers.add_parser('request', help='Request similar pictures to server')
    parser_request.add_argument('request', action='store_true')
    parser_request.add_argument('-p', dest='path', type=lambda p: pathlib.Path(p).absolute(), action='store', help='Picture path')
    parser_request.add_argument('-t', dest='waittime', type=int, action='store', default='60', help='Max waiting time for an answer')
    parser_request.add_argument('-m', dest='mapfile', type=lambda p: pathlib.Path(p).absolute(), action='store', help='Mapping file path (intput) for name conversion')
    parser_request.add_argument('-o', dest='resultfile', type=lambda p: pathlib.Path(p).absolute(), action='store', default='./result', help='Result file path (output)')
    parser_request.set_defaults(func=cli.request)

    # create the parser for the "dump" command
    parser_dump = subparsers.add_parser('dump', help='Ask server to dump its database')
    parser_dump.add_argument('dump', action='store_true')
    parser_dump.add_argument('-m', dest='mapfile', type=lambda p: pathlib.Path(p).absolute(), action='store', help='Mapping file path (intput) for name conversion')
    parser_dump.add_argument('-o', dest='dbfile', type=lambda p: pathlib.Path(p).absolute(), action='store', default='./db_dump', help='Database file path (output)')
    parser_dump.add_argument('-c', dest='copyids', action='store_true', help='Copy ids in "image" field. Useful if mapping is used and ids are filenames.')
    parser_dump.set_defaults(func=cli.dump)

    parser.add_argument('--version', action='version', version='douglas-quaid client cli %s' % ("1.0.0"))

    # Parse argument, fetch the reference to the function to call, and call it
    args = parser.parse_args()

    try:
        func = args.func
    except AttributeError:
        parser.error("too few arguments")

    func(args)


if __name__ == "__main__":
    main()
