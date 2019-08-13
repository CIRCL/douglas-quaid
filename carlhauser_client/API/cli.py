#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import pathlib
from typing import Dict

# ==================== ------ PERSONAL LIBRARIES ------- ====================
from carlhauser_client.API.extended_api import Extended_API
from carlhauser_client.Helpers.dict_utilities import apply_revert_mapping
from common.ImportExport.json_import_export import save_json, load_json
from common.environment_variable import load_client_logging_conf_file
from carlhauser_client.Helpers.dict_utilities import copy_id_to_image
load_client_logging_conf_file()


# ==================== ------ LAUNCHER ------- ====================

class CLI:
    """
    Command line interface for client side
    """

    def __init__(self):
        self.ext_api :Extended_API = Extended_API.get_api()

    def ping(self, args) -> bool:
        '''
        Ping the server to check if he is alive.
        :param args: Not needed
        :return: True if the server is alive, False if the server is not
        '''
        return self.ext_api.ping_server()

    def upload(self, args) -> Dict[str, str]:
        '''
        Perform the upload of all picture in the provided folder (args.path)
        and save the mapping (original_file_name)->(id_given_by_server)
        in provided file (args.mapfile)
        :param args: arguments as described
        :return: Mapping filename to id
        '''
        print(f"Uploading pictures from {args.path}")
        mapping, nb = self.ext_api.add_many_pictures_no_wait(args.path)
        print(f"{nb} pictures uploaded.")
        save_json(mapping, args.mapfile)
        print(f"Mapping file_name / Server ID saved to {args.mapfile}.")
        return mapping

    def request(self, args) -> Dict:
        '''
        Request the similar pictures of the provided picture (args.path)
        if we get an answer before timeout (args.waittime). Translate back the provided ids
        of the server with the filenames to id mapping saved previously (args.mapfile)
        :param args: arguments as described
        :return: A dict of results # TODO : Add an example of dict of results
        '''
        results = self.ext_api.request_one_picture_and_wait(args.path, args.waittime)

        # If mapfile is provided, reverse the id. Otherwise, do nothing
        if args.mapfile:
            print(f"Mapping file detected. Reversing the ids ... ")
            mapping = load_json(args.mapfile)
            results = apply_revert_mapping(results, mapping)

        save_json(results, args.resultfile)
        return results

    def dump(self, args):
        '''
        Dump the database and transmit it to the client, and save it in a file(args.dbfile)
        Translate back the provided ids of the server with the filenames to id mapping
        saved previously (args.mapfile). Can duplicate id of picture to their "image" and "shape" attributes. Allows to visualize the database with visjs-classificator (args.copyids)
        :param args: arguments as described
        :return: The database as a Dict of a graphe (visjs-classificator style)
        '''
        print(f"Requesting server to dump its database")
        graphe_struct = self.ext_api.get_db_dump_as_graph()
        db = graphe_struct.export_as_dict()

        # TODO : Handle it properly with graphe structure calls ? For now, only operation on dict
        # If mapfile is provided, reverse the id. Otherwise, do nothing
        if args.mapfile:
            print(f"Mapping file detected. Reversing the ids ... ")
            mapping = load_json(args.mapfile)
            db = apply_revert_mapping(db, mapping)
            # TODO : graphe_struct.replace_id_from_mapping(mapping) # Cleaner

        # If Copy_ids is true, we copy the value of the picture's ids
        # to their image and shape attributes
        if args.copyids:
            print(args.copyids)
            print(f"ID to image copy option detected. Copying ... ")
            db = copy_id_to_image(db)
            # TODO : graphe_struct.copy_ids_to_image() # Cleaner

        save_json(db, args.dbfile)
        return db


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

    parser.add_argument('--version', action='version', version='douglas-quaid client cli %s' % "1.0.0")

    # Parse argument, fetch the reference to the function to call, and call it
    args = parser.parse_args()

    try:
        func = args.func
        func(args)
    except AttributeError:
        parser.error("too few arguments")


if __name__ == "__main__":
    main()
