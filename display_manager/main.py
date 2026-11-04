"""Forneca recursos do modulo base."""

# ruff: file-ignore[builtin-attribute-shadowing]

import json
from contextlib import suppress
from logging import getLogger
from os import environ as env
from pathlib import Path
from platform import system
from typing import TYPE_CHECKING, Protocol

from dotenv import dotenv_values

from display_manager import X11Vnc, Xfvb

if TYPE_CHECKING:

    class Managed(Protocol):  # ruff: ignore[undocumented-public-class]
        id_execucao: str


EMPTY_DICT: dict[int, str] = {}
"""Coleção inicial usada pelo fluxo de base."""
WORKDIR = Path.cwd()
"""Caminho de arquivos usado pelo fluxo de base."""

ArgumentsList = []
logger = getLogger(__name__)


class DisplayManager:
    """Represente display manager."""

    def __init__(self, managed: Managed) -> None:
        """Inicialize display manager.

        Args:
            managed (Managed): managed.

        """
        self.managed = managed
        self.id_execucao = managed.id_execucao
        if not self.__check():
            d_ = env.get("DISPLAY", "5")
            id_ = int(d_.replace(":", ""))
            self.id = id_
            self.display = id_
            return

        displays = self.load_displays()
        display = len(displays.keys()) + 20

        displays[display] = managed.id_execucao
        self.save_displays(displays)

        self.id = display
        self.width = 1536
        self.height = 864
        self.display = display

    @property
    def id(self) -> int:
        """Obtenha id.

        Returns:
            int: Resultado de obtenha id.

        """
        if not hasattr(self, "_id"):
            self._id = 10

        return self._id

    @id.setter
    def id(self, id_: int) -> None:
        """Atualize id.

        Args:
            id_ (int): Numero inteiro de id.

        """
        self._id = id_

    def load_displays(self) -> dict[int, str]:
        """Carregue load displays.

        Returns:
            dict[int, str]: Resultado de carregue load displays.

        """
        displays: dict[int, str] = {}
        path = WORKDIR.joinpath("tmp", "displays.json")
        if not path.exists():
            path.parent.mkdir(exist_ok=True)

        if path.exists():
            displays = json.loads(path.read_text())

        self._displays_dict = displays

        return displays

    def save_displays(self, displays: dict[int, str]) -> None:
        """Grave save displays.

        Args:
            displays (dict[int, str]): Dicionario de displays.

        """
        _ = self
        path = WORKDIR.joinpath("tmp", "displays.json")
        if not path.exists():
            path.parent.mkdir(exist_ok=True)
        path.write_text(json.dumps(displays))

    def start(self) -> None:
        """Inicie start."""
        if not self.__check():
            return

        self.xfvb = Xfvb(
            str(self.width),
            str(self.height),
            "24",
            str(self.display),
        )

        self.x11 = X11Vnc(str(self.display))
        self.xfvb.start()
        self.x11.start()

        return

    def stop(self) -> None:
        """Encerre stop."""
        if not self.__check():
            return

        with suppress(Exception):
            self.x11.stop()

        with suppress(Exception):
            self.xfvb.stop()

        displays = self.load_displays()
        display = self.get_display()
        displays.pop(display)
        self.save_displays(displays)

    def get_display(self) -> int:
        """Obtenha get display.

        Returns:
            int: Resultado de obtenha get display.

        """
        pid = self.id_execucao
        displays = self.load_displays()
        display = list(filter(lambda x: x[1] == pid, displays.items()))

        return display[0][0]

    def __check(self) -> bool:
        _ = self

        def __is_wsl() -> bool:
            val = dotenv_values(".env").get("IS_WSL", "False") or ""
            return (val or "").lower() != "true"

        if system() == "Linux":
            return __is_wsl()

        if system() == "Windows":
            logger.warning("Este módulo só funciona no linux!")

            return False

        return __is_wsl()
