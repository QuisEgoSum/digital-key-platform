import ctypes
import sys

if sys.platform == "linux":
    _LIBC = ctypes.CDLL("libc.so.6", use_errno=True)
else:
    _LIBC = None

_PR_SET_NAME = 15


def set_linux_proc_name(name: str) -> None:
    if _LIBC is None:
        return
    buf = ctypes.c_char_p(name[:15].encode("utf-8"))
    _LIBC.prctl(_PR_SET_NAME, buf, 0, 0, 0)
