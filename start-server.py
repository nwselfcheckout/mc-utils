"""
Launch Minecraft server and restart it every 24 hours.
Place script
"""

import time
import os
import json
import schedule
from mcrcon import MCRcon

SERVER_FOLDER = "."
LAUNCH_ARGS = "-Xms16G -Xmx16G -XX:+UseG1GC -XX:+ParallelRefProcEnabled -XX:MaxGCPauseMillis=200 -XX:+UnlockExperimentalVMOptions -XX:+DisableExplicitGC -XX:+AlwaysPreTouch -XX:G1NewSizePercent=30 -XX:G1MaxNewSizePercent=40 -XX:G1HeapRegionSize=8M -XX:G1ReservePercent=20 -XX:G1HeapWastePercent=5 -XX:G1MixedGCCountTarget=4 -XX:InitiatingHeapOccupancyPercent=15 -XX:G1MixedGCLiveThresholdPercent=90 -XX:G1RSetUpdatingPauseTimePercent=5 -XX:SurvivorRatio=32 -XX:+PerfDisableSharedMem -XX:MaxTenuringThreshold=1"

START_TIME = time.time()

RCON_PASSWORD = os.environ["MC_RCON_PASSWORD"]
RCON_PORT = int(os.environ["MC_RCON_PORT"])

YELLOW = "#FAA61A"
RED = "#F04747"


def get_launch_args(folder):
    """
    Get Java launch args for the server.

    Checks if the server folder contains additional launch arguments
    and appends them to the "usual" launch args.
    """
    try:
        with open(os.path.join(folder, "mp_args.txt"), "r") as f:
            mp_args = f.read().strip()
            return f"{LAUNCH_ARGS} {mp_args}"
    except Exception:
        return LAUNCH_ARGS


def start_server():
    """Open a new terminal window and start the server."""
    launch_args = get_launch_args(SERVER_FOLDER)
    cmd = (
        f"screen -S mc_server -dm bash -c"
        f" \"cd '{os.path.abspath(SERVER_FOLDER)}';"
        f' java {launch_args} -jar server.jar nogui"'
    )

    print()
    print("> " + cmd)

    os.system(cmd)


def send_command(cmd):
    with MCRcon(
        host="localhost", password=RCON_PASSWORD, port=RCON_PORT, timeout=10
    ) as mc:
        print("[CONSOLE] " + mc.command(cmd))


def warn_server(color, time):
    """Send a message to warn players that the server is restarting."""
    tellraw_arg = [
        "",
        {"text": "⚠ ", "color": color},
        {"text": "Warning    ", "bold": True, "color": color},
        {"text": f"The server will restart in {time}.", "color": color},
    ]

    send_command("tellraw @a " + json.dumps(tellraw_arg))
    print(f"Sent a warning that the server will restart in {time}.")


def stop_and_start_server():
    send_command("kick @a The server is restarting. Service will resume momentarily.")
    send_command("stop")
    print("Sent a request to stop the server. Will relaunch in 60 seconds.")
    time.sleep(60)
    start_server()


schedule.every().day.at("01:00").do(warn_server, YELLOW, "an hour")
schedule.every().day.at("01:30").do(warn_server, YELLOW, "30 minutes")
schedule.every().day.at("01:45").do(warn_server, RED, "15 minutes")
schedule.every().day.at("01:55").do(warn_server, RED, "5 minutes")
schedule.every().day.at("01:59").do(warn_server, RED, "60 seconds")
schedule.every().day.at("02:00").do(warn_server, RED, "10 seconds")
schedule.every().day.at("02:01").do(stop_and_start_server)


if __name__ == "__main__":
    start_server()
    while True:
        schedule.run_pending()
        time.sleep(5)
