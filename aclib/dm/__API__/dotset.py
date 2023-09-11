from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from typing import overload
from aclib.builtins import Str

from .color import *


class DotsetInfo(object):

    def __init__(self, size: tuple[int, int], startpos: tuple[int, int], startcolor: str):
        self.size = size
        self.startpos = startpos
        self.startcolor = startcolor


class DmDotset(object):

    def __new__(cls, name: str, tmpl: str) -> Self:
        startcolor = Str(tmpl).rematch(r'\D?0\|0\|([^,]+)').group(1)
        poses = [[int(x), int(y)] for x, y, color in (xycolor.split('|') for xycolor in tmpl.split(','))]
        poses.sort()
        l, r = poses[0][0], poses[-1][0]
        poses.sort(key=lambda _pos: _pos[1])
        t, b = poses[0][1], poses[-1][1]
        startpos = -l, -t
        tmplsize = r - l + 1, b - t + 1
        return cls.__new(name, tmpl, DotsetInfo(tmplsize, startpos, startcolor))

    @classmethod
    def __new(cls, name: str, tmpl: str, info: DotsetInfo) -> Self:
        self = super().__new__(cls)
        self.__init(name, tmpl, info)
        return self

    def __init(self, name: str, tmpl: str, info: DotsetInfo):
        self.__name = name
        self.__tmpl = tmpl
        self.__size = info.size
        self.__startpos = info.startpos
        self.__matchcolor = info.startcolor

    def __repr__(self) -> str:
        return f'<DmDotset:{self.name} {self.matchcolor}|{self.width}x{self.height}={self.npixel}>'

    @classmethod
    def fromdata(cls, data: str) -> Self | None:
        try:
            def getbinim(zippedhexim: Str):
                return zippedhexim.unzip('GHIJKLMNOP').toBin(16).toStr()[-w*h:]
            b64name, b64color, strw, strh, hextmpl, hexmask = tuple(Str(data).split('|'))   # to tuple to get type hint
            name, tmplcolor = b64name.base64decode().tostr(), b64color.base64decode().tostr()
            w, h = strw.toint(), strh.toint()
            tmplcolor = cvcolor2dmcolor(tmplcolor)
            maskcolor = get_inverse_color(tmplcolor)
            bintmpl, binmask = getbinim(hextmpl), getbinim(hexmask)
            startx, starty = bintmpl.index('1') % w, bintmpl.index('1') // w
            dmim = ','.join(
                f'{i%w - startx}|{i//w - starty}|{(maskcolor, tmplcolor)[int(num)]}' 
                for i,num in enumerate(bintmpl) 
                if not binmask or binmask[i]=='1' or num=='1')
            return cls.__new(name, dmim, DotsetInfo((w, h), (startx, starty), tmplcolor))
        except: return None


    @property
    def name(self) -> str:
        return self.__name

    @property
    def tmpl(self) -> str:
        return self.__tmpl

    @property
    def matchcolor(self) -> str:
        return self.__matchcolor

    @property
    def size(self) -> tuple[int, int]:
        return self.__size

    @property
    def width(self) -> int:
        return self.__size[0]

    @property
    def height(self) -> int:
        return self.__size[1]

    @property
    def npixel(self) -> int:
        return len(self.__tmpl.split(','))


    def asname(self, name: str) -> Self:
        return self.__class__.__new(name, self.tmpl, DotsetInfo(self.size, self.__startpos, self.matchcolor))

    def asmatchcolor(self, rgbmatchcolor: str) -> Self:
        if not rgbmatchcolor or rgbmatchcolor == self.matchcolor:
            return self
        check_dmcolor(rgbmatchcolor)
        tmpl = self.tmpl \
            .replace(f'|{self.matchcolor}', f'|{rgbmatchcolor}') \
            .replace(f'|{get_inverse_color(self.matchcolor)}', f'|{get_inverse_color(rgbmatchcolor)}')
        return self.__class__.__new(self.name, tmpl, DotsetInfo(self.size, self.__startpos, rgbmatchcolor))


    @overload
    def scale(self, scale: int | float) -> Self: ...

    @overload
    def scale(self, scaleX: int | float, scaleY: int | float) -> Self: ...

    def scale(self, scaleX: int | float, scaleY: int | float = None) -> Self:
        poscolormap = {}
        if scaleY is None:
            scaleY = scaleX
        if scaleX == scaleY == 1:
            return self
        for x, y, color in (xycolor.split('|') for xycolor in self.tmpl.split(',')):
            pos = round(int(x) * scaleX), round(int(y) * scaleY)
            poscolormap[pos] = poscolormap.get(pos, color)
        scaledtmpl = ','.join([f'{x}|{y}|{color}' for (x, y), color in poscolormap.items()])
        return self.__class__(self.name, scaledtmpl)


    def print(self):
        displaymat = [['  ']*self.width for i in range(self.height)]
        for x, y, color in (xycolor.split('|') for xycolor in self.tmpl.split(',')):
            x, y = self.getrealpos((x, y))
            displaymat[y][x] = ['··', '##'][color == self.matchcolor]
        print(self)
        sep = '==' * (self.width + 1)
        print(sep)
        for line in displaymat: print('|' + "".join(["".join(color) for color in line]) + '|')
        print(f'{sep}\n')

    def getrealpos(self, tmplpos: tuple[int|str, int|str]) -> tuple[int, int]:
        return tuple( int(tmplpos[i]) + self.__startpos[i] for i in range(2))

