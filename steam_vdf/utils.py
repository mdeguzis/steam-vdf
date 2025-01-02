import subprocess
import time
import readline
import datetime
import json
import sys
import psutil
import logging
import vdf
import os

logger = logging.getLogger("cli")

from steam_vdf import users
from steam_vdf import storage


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


def is_binary_file(file_path):

    logger.debug("Checking if file is binary")
    try:
        with open(file_path, "rb") as file:
            chunk = file.read(1024)  # Read a small chunk of the file
            if b"\0" in chunk:  # Null bytes are common in binary files
                return True
            # Check for non-ASCII characters
            if any(byte > 127 for byte in chunk):
                logger.debug(f"File {file_path} is not ASCII, treating as binary.")
                return True
        logger.debug(f"Treating as non-binary file")
        return False
    except Exception as e:
        print(f"Error reading file: {e}")
        return False


def view_vdf(vdf_file, output_type):
    """
    View the contents of a VDF file
    Args:
        vdf_file (str): Path to the VDF file
        output_type (str): Type of output (json or raw)
    """
    logger.debug(f"Viewing VDF file: {vdf_file}")
    try:
        # First check if it's binary
        if is_binary_file(vdf_file):
            logger.debug("File is binary")
            try:
                with open(vdf_file, "rb") as f:
                    content = f.read()
                    try:
                        parsed = vdf.binary_loads(content)
                        if output_type == "json":
                            print(json.dumps(parsed, indent=2))
                        else:
                            print(vdf.dumps(parsed, pretty=True))
                    except Exception as e:
                        logger.debug(f"Could not parse as VDF binary: {e}")
                        # If we can't parse it, just show hex dump for binary files
                        print("Binary file contents (hex dump):")
                        for i in range(0, len(content), 16):
                            chunk = content[i : i + 16]
                            hex_values = " ".join(f"{b:02x}" for b in chunk)
                            ascii_values = "".join(
                                chr(b) if 32 <= b <= 126 else "." for b in chunk
                            )
                            print(f"{i:08x}  {hex_values:<48}  |{ascii_values}|")
            except Exception as e:
                logger.error(f"Error reading binary file: {e}")
                sys.exit(1)
        else:
            logger.debug("File is text")
            try:
                with open(vdf_file, "r", encoding="utf-8") as f:
                    content = f.read()
                if output_type == "json":
                    parsed = vdf.loads(content)
                    print(json.dumps(parsed, indent=2))
                else:
                    print(content)
            except Exception as e:
                logger.error(f"Error reading text file: {e}")
                sys.exit(1)

    except FileNotFoundError:
        logger.error(f"File not found: {vdf_file}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Error reading VDF file: {e}")
        sys.exit(1)


def get_steam_client_version():
    """
    Get Steam client version from manifest file.
    Returns a tuple of (version, is_beta, timestamp)
    """
    logger.debug("Getting Steam client version from manifest file")

    # Expand paths for both regular and beta files
    base_path = os.path.expanduser("~/.steam/steam/package")
    manifest_path = os.path.join(base_path, "steam_client_ubuntu12.manifest")
    beta_manifest_path = os.path.join(
        base_path, "steam_client_publicbeta_ubuntu12.manifest"
    )

    version = None
    is_beta = False
    timestamp = None

    # First check for beta version
    if os.path.exists(beta_manifest_path):
        logger.debug(f"Found beta manifest: {beta_manifest_path}")
        try:
            with open(beta_manifest_path, "r") as f:
                for line in f:
                    if '"version"' in line:
                        version = line.split('"')[3]  # Get the version between quotes
                        is_beta = True
                        timestamp = datetime.datetime.fromtimestamp(int(version))
                        logger.debug(f"Found beta version: {version} from {timestamp}")
                        break
        except Exception as e:
            logger.error(f"Error reading beta manifest: {e}")

    # If no beta version found, check regular version
    if not version and os.path.exists(manifest_path):
        logger.debug(f"Found regular manifest: {manifest_path}")
        try:
            with open(manifest_path, "r") as f:
                for line in f:
                    if '"version"' in line:
                        version = line.split('"')[3]  # Get the version between quotes
                        timestamp = datetime.datetime.fromtimestamp(int(version))
                        logger.debug(
                            f"Found regular version: {version} from {timestamp}"
                        )
                        break
        except Exception as e:
            logger.error(f"Error reading manifest: {e}")

    if not version:
        logger.error("No Steam client version found in manifest files")
        return None, False, None

    return version, is_beta, timestamp


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


def display_steam_info(args, this_steam_library):
    """
    Display Steam library and account information
    """
    logger.info("Displaying Steam information")

    # Display Steam info
    version, is_beta, timestamp = get_steam_client_version()
    if version:
        print("\nSteam Client Information:")
        print(f"\t- Steam Client Version: {version}")
        if timestamp:
            print(f"\t- Last Updated: {timestamp}")
            # Calculate how long ago this was
            age = datetime.datetime.now() - timestamp
            if age.days > 0:
                print(f"\t- Age: {age.days} days old")
            else:
                hours = age.seconds // 3600
                print(f"\t- Age: {hours} hours old")
        else:
            logger.info("Could not determine update timestamp")
        print(f"\t- Is Beta: {is_beta}")
    else:
        logger.error("Could not determine Steam client version")

    # Display user info
    users.get_user_info(args, this_steam_library)

    # Display storage information
    if args.analyze_storage:
        storage.analyze_storage(args, this_steam_library)
