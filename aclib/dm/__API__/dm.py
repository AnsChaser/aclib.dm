from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Literal, Self

import os, sys, time
import comtypes
import comtypes.client
from aclib.winlib import winapi

from .dll import dmdll


if sys.maxsize > 2 ** 32:
    raise RuntimeError(
        'can not use dm plugin in 64-bit python.')


class DM(object):

    def __new__(cls) -> Self | None:
        try:
            winapi.CoInitialize()
            self = super().__new__(cls)
            self.__dmobj = comtypes.client.CreateObject('dm.dmsoft')
            return self
        except OSError:
            return None

    def __getattr__(self, item):
        return getattr(self.__dmobj, item)

    @classmethod
    def regDM(cls, regpath='C://Windows/SysWOW64/') -> Literal[-1, 0, 1]:
        """-1: registered before; 0: register fail; 1: register success"""

        dmpath = os.path.join(regpath, 'dm.dll')
        if cls() is None:
            if not winapi.IsUserAdmin():
                raise PermissionError('administrator required')
            if os.path.isfile(regpath):
                raise FileExistsError('Please give a directory which be used to store "dm.dll" rather than a existed file')
            if not os.path.exists(dmpath):
                os.makedirs(regpath or os.getcwd(), exist_ok=True)
                with open(dmpath, 'wb') as f:
                    f.write(dmdll)
            os.system('regsvr32 ' + dmpath)
            t = time.time()
            while not cls() and time.time() - t < 3:
                time.sleep(0.5)
            if cls():
                return 1
            return 0
        else: return -1

    @classmethod
    def unRegDM(cls) -> Literal[-1, 0, 1]:
        """-1: not register yet; 0: unregister fail; 1: unregister success"""

        dm = cls()
        if dm:
            if not winapi.IsUserAdmin():
                raise PermissionError('administrator required')
            os.system(f'regsvr32 {dm.GetBasePath()}{os.path.sep}dm.dll /u')
            if cls() is None:
                return 1
            return 0
        else: return -1
