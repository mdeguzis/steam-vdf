import logging
import shutil
import vdf
import os
from pathlib import Path
from humanize import naturalsize  # Add this import

logger = logging.getLogger("cli")


def analyze_storage(args, steam_library):
    storage_info = get_library_storage_info(steam_library)
    if storage_info:
        print("\nStorage Information:")
        print(f"Total: {storage_info['total']}")
        print(f"Used: {storage_info['used']}")
        print(f"Free: {storage_info['free']}")

    installed_games = get_installed_games(steam_library)
    if installed_games:
        # Sort the games list by size in descending order
        sorted_games = sorted(
            installed_games, key=lambda x: x["raw_size"], reverse=True
        )

        # Only take top 20 if --all is not specified
        if not args.all:
            sorted_games = sorted_games[:20]
            print("\nInstalled Games (Top 20 by size):")
        else:
            print(f"\nInstalled Games (All {len(sorted_games)} games):")

        total_size = sum(game["raw_size"] for game in installed_games)

        # Find the longest game name for padding
        max_name_length = max(len(game["name"]) for game in sorted_games)
        max_size_length = max(len(game["size"]) for game in sorted_games)

        # Print header with extra spacing
        print(f"{'Size':>12}    {'Game Name':<{max_name_length}}    {'(ID)':<12}")
        print("-" * (12 + 4 + max_name_length + 4 + 12))  # Separator line

        # Print each game with aligned columns and extra spacing
        for game in sorted_games:
            print(
                f"{game['size']:>12}    {game['name']:<{max_name_length}}    (ID: {game['app_id']})"
            )

        print("-" * (12 + 4 + max_name_length + 4 + 12))  # Separator line
        print(f"\nTotal space used by all games: {naturalsize(total_size)}")
    else:
        print("No games installed")

    # Add the non-Steam usage display
    print("\nLargest Non-Steam Directories (Top 20):")
    print("-" * 70)  # Increased separator length
    sizes = get_non_steam_usage(steam_library)
    if sizes:
        total_non_steam = sum(item["raw_size"] for item in sizes)
        for item in sizes[:20]:  # Always show top 20 for non-Steam directories
            # Get relative path from home directory if possible
            home = str(Path.home())
            display_path = item["path"].replace(home, "~")
            print(f"{item['size']:>12}    {display_path}")
        print("-" * 70)  # Increased separator length
        print(
            f"Total size of all non-Steam directories: {naturalsize(total_non_steam)}"
        )
    else:
        print("No accessible non-Steam directories found")


def get_installed_games(library_path):
    apps_path = os.path.join(library_path, "steamapps")
    installed_games = []

    if os.path.exists(apps_path):
        for file in os.listdir(apps_path):
            if file.startswith("appmanifest_"):
                manifest_path = os.path.join(apps_path, file)
                try:
                    with open(manifest_path, "r", encoding="utf-8") as f:
                        manifest = vdf.load(f)
                        app_data = manifest.get("AppState", {})
                        size_on_disk = int(app_data.get("SizeOnDisk", 0))
                        installed_games.append(
                            {
                                "name": app_data.get("name", "Unknown"),
                                "app_id": app_data.get("appid", "Unknown"),
                                "size": naturalsize(size_on_disk),
                                "raw_size": size_on_disk,
                            }
                        )
                except Exception as e:
                    logger.error(f"Error reading manifest {file}: {str(e)}")

    return installed_games


def get_non_steam_usage(steam_path):
    """Get sizes of directories on same drive as Steam, excluding Steam directory"""
    steam_path = os.path.abspath(steam_path)
    home_dir = str(Path.home())
    parent_dir = os.path.dirname(steam_path)
    sizes = []

    for entry in os.scandir(parent_dir):
        if entry.is_dir() and entry.path != steam_path:
            try:
                total = 0
                for dirpath, dirnames, filenames in os.walk(entry.path):
                    try:
                        for f in filenames:
                            fp = os.path.join(dirpath, f)
                            if not os.path.islink(fp):
                                total += os.path.getsize(fp)
                    except (PermissionError, FileNotFoundError):
                        continue

                if total > 0:  # Only include if it has size
                    sizes.append(
                        {
                            "path": entry.path,
                            "size": naturalsize(total),
                            "raw_size": total,
                        }
                    )
            except (PermissionError, FileNotFoundError):
                continue

    return sorted(sizes, key=lambda x: x["raw_size"], reverse=True)


def get_library_storage_info(library_path):
    try:
        total, used, free = shutil.disk_usage(library_path)
        return {
            "total": naturalsize(total),
            "used": naturalsize(used),
            "free": naturalsize(free),
        }
    except Exception as e:
        logger.error(f"Error getting storage info: {str(e)}")
        return None
