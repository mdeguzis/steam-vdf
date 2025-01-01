#!/usr/bin/env python

import argparse
import json
import locale
import logging

from pathlib import Path

from steam_vdf import users
from steam_vdf import utils

# Initialize
report_filename = "/tmp/finance-buddy-report.json"
log_filename = "/tmp/finance-buddy.log"


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Steam VDF Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Info command and its options
    info_parser = subparsers.add_parser(
        "info", help="Display Steam library information"
    )
    info_parser.add_argument(
        "--analyze-storage",
        action="store_true",
        help="Analyze storage usage including non-Steam directories",
    )
    info_parser.set_defaults(info=True)

    # Other main commands
    add_parser = subparsers.add_parser(
        "add-shortcut", help="Add a new non-Steam game shortcut"
    )
    add_parser.set_defaults(add_shortcut=True)

    list_parser = subparsers.add_parser(
        "list-shortcuts", help="List existing non-Steam game shortcuts"
    )
    list_parser.set_defaults(list_shortcuts=True)

    delete_parser = subparsers.add_parser(
        "delete-shortcut", help="Delete an existing non-Steam game shortcut"
    )
    delete_parser.set_defaults(delete_shortcut=True)

    restart_parser = subparsers.add_parser("restart-steam", help="Restart Steam")
    restart_parser.set_defaults(restart_steam=True)

    # Optional flags
    parser.add_argument(
        "-v", "--dump-vdfs", action="store_true", help="Enable dumping of VDFs to JSON"
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        parser.exit()

    return args


def main():
    # Initialize logger
    logger = utils.setup_logging()

    # Parse arguments
    args = parse_arguments()

    logger.info("Starting Steam tool")
    # Initialize the matches attribute for the complete_path function
    utils.complete_path.matches = []

    # Find Steam libraries
    all_libraries = users.find_steam_library_folders(args)
    if not all_libraries:
        logger.error("No Steam libraries found")
        print("No Steam libraries found. Exiting.")
        exit(1)

    # Select library
    selected_library = users.choose_library(all_libraries)
    if not selected_library:
        logger.error("No Steam library selected")
        print("No library selected. Exiting.")
        exit(1)

    # Handle commands
    if args.command == "info":
        users.display_steam_info(args, selected_library)
    elif args.command == "list-shortcuts":
        users.list_shortcuts(args, selected_library)
    elif args.command == "delete-shortcut":
        users.delete_shortcut(args, selected_library)
        utils.restart_steam()
    elif args.command == "restart-steam":
        utils.restart_steam()
    elif args.command == "add-shortcut":
        users.add_shortcut(args, selected_library)

    logger.info("Exiting Steam VDF tool")
    logger.info("Make sure you restart steam for any changes to take effect")


if __name__ == "__main__":
    main()
