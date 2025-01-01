import logging
import subprocess
import os
import time

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


def restart_steam():
    """
    Prompt user to restart Steam and handle the restart process
    """
    try:
        restart = (
            input("\nWould you like to restart Steam now? (y/N): ").strip().lower()
        )
        if restart == "y":
            print("\nRestarting Steam...")
            logger.info("User requested Steam restart")

            # Kill existing Steam process
            try:
                subprocess.run(["killall", "steam"], check=True)
                logger.info("Successfully terminated Steam process")
            except subprocess.CalledProcessError:
                logger.warning("No Steam process found to terminate")
            except Exception as e:
                logger.error(f"Error terminating Steam: {str(e)}")
                return False

            # Wait a moment for Steam to fully close
            time.sleep(2)

            # Start Steam in background
            try:
                subprocess.Popen(
                    ["steam"],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    start_new_session=True,
                )
                logger.info("Successfully started Steam")
                print("Steam is restarting...")
                return True
            except Exception as e:
                logger.error(f"Error starting Steam: {str(e)}")
                print("Error starting Steam. Please restart manually.")
                return False
        else:
            print("\nPlease restart Steam manually for changes to take effect.")
            return False
    except (KeyboardInterrupt, EOFError):
        logger.info("\nRestart operation cancelled by user")
        print("\nPlease restart Steam manually for changes to take effect.")
        return False


def setup_logging():
    """
    Configure logging for the application.
    Creates a logs directory if it doesn't exist.
    """
    # Create logs directory if it doesn't exist
    log_dir = "/tmp/"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # Configure logger
    logger = logging.getLogger("steam_library_finder")
    logger.setLevel(logging.DEBUG)

    # Create file handler
    file_handler = logging.FileHandler(os.path.join(log_dir, "steam_library.log"))
    file_handler.setLevel(logging.DEBUG)

    # Create console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    # Create formatter
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

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
