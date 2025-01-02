import subprocess
import time
import readline
import json
import sys
import psutil
import logging
import vdf
import os

logger = logging.getLogger("cli")


def complete_path(text, state):
    """
    Tab completion function for file paths
    """

    if "~" in text:
        text = os.path.expanduser(text)

    # Get the dirname and basename of the path
    dirname = os.path.dirname(text) if text else "."
    basename = os.path.basename(text)

    if not dirname:
        dirname = "."

    try:
        # Get all matching files/directories
        if state == 0:
            if dirname == ".":
                complete_path.matches = [
                    f for f in os.listdir(dirname) if f.startswith(basename)
                ]
            else:
                if not os.path.exists(dirname):
                    complete_path.matches = []
                else:
                    complete_path.matches = [
                        os.path.join(os.path.dirname(text), f)
                        for f in os.listdir(dirname)
                        if f.startswith(os.path.basename(text))
                    ]

        # Return match or None if no more matches
        if state < len(complete_path.matches):
            return complete_path.matches[state]
        else:
            return None
    except (OSError, AttributeError):
        complete_path.matches = []
        return None


def is_steam_running():
    """Check if Steam process is running"""
    for proc in psutil.process_iter(["name"]):
        try:
            # Check for both 'steam' and 'Steam' process names
            if proc.info["name"].lower() == "steam":
                logger.debug("Found running Steam process")
                logger.debug(f"Process details: {proc.info}")
                return True
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    return False


def restart_steam():
    """
    Restart Steam and wait for it to fully start up
    Returns True if successful, False otherwise
    """
    MAX_WAIT_TIME = 60  # Maximum seconds to wait for Steam to start
    CHECK_INTERVAL = 1  # Seconds between checks

    logger.info("Attempting to restart Steam...")
    try:
        # Check if Steam is running first
        if is_steam_running():
            logger.info("Stopping Steam...")
            logger.debug("Terminating existing Steam process")

            # Kill existing Steam process
            try:
                subprocess.run(["killall", "steam"], check=True)
                logger.debug("Successfully terminated Steam process")
            except subprocess.CalledProcessError:
                logger.warning("No Steam process found to terminate")
            except Exception as e:
                logger.error(f"Error terminating Steam: {str(e)}")
                return False

            # Wait for Steam to fully close
            wait_time = 0
            while is_steam_running() and wait_time < 10:
                time.sleep(1)
                wait_time += 1

        # Start Steam in background
        logger.info("Starting Steam...")
        try:
            subprocess.Popen(
                ["steam"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                start_new_session=True,
            )
            logger.debug("Steam start command issued")
        except Exception as e:
            logger.error("Error starting Steam. Please restart manually.")
            exit(1)

        # Wait for Steam to start
        logger.debug("Waiting for Steam to start...")
        wait_time = 0
        while wait_time < MAX_WAIT_TIME:
            if is_steam_running():
                logger.debug("Steam has successfully restarted!")
                logger.debug("Steam successfully restarted")
                return True

            time.sleep(CHECK_INTERVAL)
            wait_time += CHECK_INTERVAL

            # Show a progress indicator
            if wait_time % 5 == 0:
                logger.debug(f"Still waiting... ({wait_time}s)")

        # If we get here, Steam didn't start in time
        logger.error(f"Steam did not start within {MAX_WAIT_TIME} seconds")
        logger.info("Please check Steam manually.")
        exit(1)

    except KeyboardInterrupt:
        logger.info("Restart operation cancelled by user")
        logger.info("Restart cancelled by user.")
        return False
    except Exception as e:
        logger.error(f"Unexpected error during Steam restart: {str(e)}")
        exit(1)


def setup_logging(debug=False):
    """
    Configure logging for the application.
    Args:
        debug (bool): If True, sets logging level to DEBUG, otherwise INFO
    """

    # Only configure if handlers haven't been set up
    if not logger.handlers:
        # Set base logging level
        base_level = logging.DEBUG if debug else logging.INFO
        logger.setLevel(base_level)

        # Create console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(base_level)

        # Create file handler for debug logging
        log_dir = "/tmp/"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)

        file_handler = logging.FileHandler(os.path.join(log_dir, "steam_vdf.log"))
        file_handler.setLevel(logging.DEBUG)  # Always keep debug logging in file

        # Create formatters
        console_fmt = "%(levelname)s - %(message)s"
        file_fmt = "%(asctime)s - %(levelname)s - %(message)s"

        console_formatter = logging.Formatter(console_fmt)
        file_formatter = logging.Formatter(file_fmt)

        # Apply formatters
        console_handler.setFormatter(console_formatter)
        file_handler.setFormatter(file_formatter)

        # Add handlers
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)

    return logger


def steam64_to_steam32(steam64_id):
    """Convert Steam64 ID to Steam32 ID"""
    try:
        return str(int(steam64_id) - 76561197960265728)
    except (ValueError, TypeError):
        return None


def steam32_to_steam64(steam32_id):
    """Convert Steam32 ID to Steam64 ID"""
    try:
        return str(int(steam32_id) + 76561197960265728)
    except (ValueError, TypeError):
        return None


def prompt_path(prompt_text, is_file=True, default_path=None):
    """
    Prompt for a path with autocompletion
    """
    readline.set_completer_delims(" \t\n;")
    readline.parse_and_bind("tab: complete")
    readline.set_completer(complete_path)

    while True:
        try:
            path = input(prompt_text).strip()

            # Handle empty input - use default if provided
            if not path:
                if default_path:
                    logger.info(f"Using default path: {default_path}")
                    return default_path
                else:
                    logger.warning("Empty path provided")
                    logger.info("Please enter a valid path")
                    continue

            # Expand user path if needed
            if "~" in path:
                path = os.path.expanduser(path)

            # Convert to absolute path
            path = os.path.abspath(path)

            if is_file:
                if os.path.isfile(path):
                    return path
                else:
                    logger.warning(f"Invalid file path: {path}")
                    logger.info("Please enter a valid file path")
            else:
                if os.path.isdir(path):
                    return path
                else:
                    logger.warning(f"Invalid directory path: {path}")
                    logger.info("Please enter a valid directory path")
        except (KeyboardInterrupt, EOFError):
            logger.info("\nOperation cancelled by user")
            return None
        except Exception as e:
            logger.error(f"Error processing path: {str(e)}")
            logger.info("Please enter a valid path")


def view_vdf(vdf_file, output_type):
    """
    View the contents of a VDF file
    Args:
        vdf_file (str): Path to the VDF file
        output_type (str): Type of output (json or raw)
    """
    logger.debug(f"Viewing VDF file: {vdf_file}")
    try:
        with open(vdf_file, "r", encoding="utf-8") as f:
            vdf_content = f.read()

        if output_type == "json":
            parsed = vdf.loads(vdf_content)
            print(json.dumps(parsed, indent=2))
        else:
            print(vdf_content)
    except FileNotFoundError:
        logger.error(f"File not found: {args.file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading VDF file: {e}")
        sys.exit(1)


def find_steam_libraries(args):
    """
    Find Steam libraries based on the provided arguments
    Args:
        args: Parsed command-line arguments
    Returns:
        list: List of Steam library paths
    """
    logger.debug("Finding Steam libraries")

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

    return selected_library
