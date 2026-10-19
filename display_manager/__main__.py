# ruff: file-ignore[undocumented-public-module, undocumented-public-function]
from typing import Literal

if __name__ == "__main__":

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

    main()
