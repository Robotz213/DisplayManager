# ruff: file-ignore[undocumented-public-method, undocumented-public-module, undocumented-public-init, undocumented-public-function, undocumented-public-class]
# pyright: reportMissingModuleSource=false
from contextlib import suppress
from os import environ
from pathlib import Path
from subprocess import CalledProcessError
from typing import Literal

from psutil import Popen, Process, ZombieProcess, process_iter


def load_env(display: str = "20") -> dict[str, str]:

    env = environ.copy()
    env["DISPLAY"] = f":{display}"
    env["XDG_SESSION_TYPE"] = "x11"
    env.pop("WAYLAND_DISPLAY", None)
    return env


class Xfvb:
    screen_width: str = "1600"
    screen_height: str = "900"
    screen_depth: str = "24"
    display_id: str = "20"
    EXECUTABLE = "/usr/bin/Xvfb"

    def __init__(
        self,
        screen_width: str = "1600",
        screen_height: str = "900",
        screen_depth: str = "24",
        display_id: str = "20",
    ) -> None:

        self.screen_width = screen_width
        self.screen_height = screen_height
        self.screen_depth = screen_depth
        self.display_id = display_id

        self.f = Path("xfvb.log").open("w", encoding="utf-8")  # ruff: ignore[open-file-with-context-handler]
        procs = process_iter()

        def filter_proc(i: Process) -> bool:
            v = f"Xvfb :{self.display_id}"
            try:
                return v in " ".join(i.cmdline())

            except ZombieProcess:
                return False

        try:
            process = next(iter(filter(filter_proc, procs)), None)

            if process:
                with suppress(Exception):
                    Process(process.pid).kill()
            return
        except CalledProcessError as e:
            _ = e

    def start(self) -> None:

        geometry = (
            f"{self.screen_width}x"
            f"{self.screen_height}x"
            f"{self.screen_depth}"
        )

        self.__process = Popen(
            [
                self.EXECUTABLE,
                f":{self.display_id}",
                "-screen",
                "0",
                geometry,
            ],
            env=load_env(),
            start_new_session=True,
            stderr=self.f,
        )

    def stop(self) -> None:

        with suppress(Exception):
            self.__process.kill()

        with suppress(Exception):
            self.f.close()


class Xfce4:
    def __init__(self, display: str) -> None:

        self.display = display
        self.f = Path("xfce4.log").open("w", encoding="utf-8")  # ruff: ignore[open-file-with-context-handler]

    def start(self) -> None:

        env = load_env()
        env["DISPLAY"] = self.display
        self.__process = Popen(
            executable="/usr/bin/startxfce4",
            args=[""],
            env=env,
            start_new_session=True,
            stderr=self.f,
        )

    def stop(self) -> None:

        with suppress(Exception):
            self.__process.kill()

        with suppress(Exception):
            self.f.close()


class X11Vnc:
    EXECUTABLE = "/usr/bin/x11vnc"

    def __init__(self, display: str) -> None:

        self.display = display
        self.vnc_port = f"41{display.zfill(3)}"
        self.f = Path("x11vnc.log").open("w", encoding="utf-8")  # ruff: ignore[open-file-with-context-handler]

    def start(self) -> None:

        cmd = (
            "x11vnc",
            "-rfbport",
            f"{self.vnc_port}",
            "-forever",
            "-shared",
            "-display",
            f":{self.display}",
            "-nopw",
        )

        env = load_env()
        env.pop("WAYLAND_DISPLAY", None)
        self.__process = Popen(
            executable=self.EXECUTABLE,
            args=cmd,
            start_new_session=True,
            env=env,
            stderr=self.f,
        )

    def stop(self) -> None:

        with suppress(Exception):
            self.__process.kill()

        with suppress(Exception):
            self.f.close()


def main() -> Literal["ok"]:

    from .main import X11Vnc, Xfce4, Xfvb

    xfvb = Xfvb()
    xfvb.start()
    xfce4 = Xfce4(xfvb.display_id)
    xfce4.start()
    x11 = X11Vnc(xfvb.display_id)
    x11.start()

    input("Pressione ENTER para fechar")

    x11.stop()
    xfce4.stop()
    xfvb.stop()

    return "ok"
