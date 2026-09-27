"""Scheduler — runs flash_offers at 7 AM via systemd timer."""
import sys
import os
from pathlib import Path

WORK_DIR = Path(__file__).parent.resolve()
PYTHON_BIN = sys.executable

SERVICE = f"""[Unit]
Description=Meena Flash Offers 7 AM Sender

[Service]
Type=oneshot
WorkingDirectory={WORK_DIR}
ExecStart={PYTHON_BIN} {WORK_DIR}/flash_offers.py --schedule
StandardOutput=append:{WORK_DIR}/flash_scheduler.log
StandardError=append:{WORK_DIR}/flash_scheduler.log
"""

TIMER = """[Unit]
Description=Run Meena Flash Offers daily at 7 AM

[Timer]
OnCalendar=*-*-* 07:00:00
Persistent=true

[Install]
WantedBy=timers.target
"""


def install():
    user_dir = Path.home() / ".config" / "systemd" / "user"
    user_dir.mkdir(parents=True, exist_ok=True)

    (user_dir / "meena-flash-offers.service").write_text(SERVICE)
    (user_dir / "meena-flash-offers.timer").write_text(TIMER)

    os.system("systemctl --user daemon-reload")
    os.system("systemctl --user enable meena-flash-offers.timer")
    os.system("systemctl --user start meena-flash-offers.timer")

    print("✅ Scheduler installed. Runs daily at 7:00 AM.")
    print(f"   Service: {user_dir}/meena-flash-offers.service")
    print(f"   Timer:   {user_dir}/meena-flash-offers.timer")
    os.system("systemctl --user list-timers | grep meena")


def uninstall():
    os.system("systemctl --user disable meena-flash-offers.timer")
    os.system("systemctl --user stop meena-flash-offers.timer")
    print("✅ Scheduler removed")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python3 flash_offers_scheduler.py [install|uninstall]")
    elif sys.argv[1] == "install":
        install()
    elif sys.argv[1] == "uninstall":
        uninstall()
