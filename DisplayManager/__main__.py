from threading import Event  # ruff: ignore[undocumented-public-module]

from .main import Bspwm, X11Vnc, Xfvb

xfvb = Xfvb()
xfvb.start()
Bspwm(xfvb.display_id).start()
X11Vnc(xfvb.display_id).start()

Event().wait()
