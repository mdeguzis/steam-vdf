#!/usr/bin/env python

import argparse

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
    parent_parser.add_argument(
        "-o",
        "--output",
        choices=["json", "text"],
        default="text",
        help="Output type format",
    )

    # Add parent parser arguments to main parser
    for action in parent_parser._actions:
        parser._add_action(action)

    # Create subparsers with parent
    subparsers = parser.add_subparsers(dest="command")

    # View
    info_parser = subparsers.add_parser(
        "info", help="Display Steam library information", parents=[parent_parser]
    )
    info_parser.add_argument(
        "--analyze-storage",
        action="store_true",
        help="Analyze storage usage including non-Steam directories",
    )
    info_parser.add_argument(
        "--all",
        action="store_true",
        help="Show all information (e.g. all games)",
    )
    list_parser = subparsers.add_parser(
        "list-shortcuts",
        help="List existing non-Steam game shortcuts",
        parents=[parent_parser],
    )
    view_parser = subparsers.add_parser(
        "view", help="View contents of a VDF file", parents=[parent_parser]
    )
    view_parser.add_argument("file", type=str, help="Path to VDF file to view")

    # Add
    add_parser = subparsers.add_parser(
        "add-shortcut",
        help="Add a new non-Steam game shortcut",
        parents=[parent_parser],
    )

    # Deletion  / Manipulation
    delete_parser = subparsers.add_parser(
        "delete-shortcut",
        help="Delete an existing non-Steam game shortcut",
        parents=[parent_parser],
    )

    # System
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

    logger.debug("Starting Steam tool")
    # Initialize the matches attribute for the complete_path function
    utils.complete_path.matches = []

    # Handle commands from parsers
    if args.command == "info":
        selected_library = users.find_steam_library(args)
        utils.display_steam_info(args, selected_library)
    elif args.command == "view":
        utils.view_vdf(args.file, args.output)
    elif args.command == "list-shortcuts":
        selected_library = users.find_steam_library(args)
        users.list_shortcuts(args, selected_library)
    elif args.command == "delete-shortcut":
        selected_library = users.find_steam_library(args)
        users.delete_shortcut(args, selected_library)
        utils.restart_steam()
    elif args.command == "restart-steam":
        utils.restart_steam()
    elif args.command == "add-shortcut":
        selected_library = users.find_steam_library(args)
        users.add_shortcut(args, selected_library)
        utils.restart_steam()

    logger.info("Exiting Steam VDF tool")
    logger.info("Make sure you restart steam for any changes to take effect")


if __name__ == "__main__":
    main()
