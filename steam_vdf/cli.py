#!/usr/bin/env python

import argparse

from pathlib import Path

from steam_vdf import users
from steam_vdf import utils


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="Steam VDF Tool")

    # Create parent parser for common arguments
    parent_parser = argparse.ArgumentParser(add_help=False)
    parent_parser.add_argument(
        "-d", "--debug", action="store_true", help="Enable debug output"
    )
    parent_parser.add_argument(
        "-v", "--dump-vdfs", action="store_true", help="Enable dumping of VDFs to JSON"
    )

    # Add parent parser arguments to main parser
    for action in parent_parser._actions:
        parser._add_action(action)

    # Create subparsers with parent
    subparsers = parser.add_subparsers(dest="command")

    # Info command and its options
    info_parser = subparsers.add_parser(
        "info", help="Display Steam library information", parents=[parent_parser]
    )
    info_parser.add_argument(
        "--analyze-storage",
        action="store_true",
        help="Analyze storage usage including non-Steam directories",
    )

    # Other commands with shared parent
    add_parser = subparsers.add_parser(
        "add-shortcut",
        help="Add a new non-Steam game shortcut",
        parents=[parent_parser],
    )

    list_parser = subparsers.add_parser(
        "list-shortcuts",
        help="List existing non-Steam game shortcuts",
        parents=[parent_parser],
    )

    delete_parser = subparsers.add_parser(
        "delete-shortcut",
        help="Delete an existing non-Steam game shortcut",
        parents=[parent_parser],
    )

    restart_parser = subparsers.add_parser(
        "restart-steam", help="Restart Steam", parents=[parent_parser]
    )

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        parser.exit()

    return args


def main():
    # Parse arguments
    args = parse_arguments()

    # Initialize logger
    logger = utils.setup_logging(args.debug)

    logger.info("Starting Steam tool")
    # Initialize the matches attribute for the complete_path function
    utils.complete_path.matches = []

    # Find Steam libraries
    if not args.command == "restart-steam":
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
