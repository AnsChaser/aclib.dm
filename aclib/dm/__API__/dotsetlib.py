from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from typing import Self

from typing import overload

from .dotset import DmDotset


class DmDotsetLib(object):

    def __new__(cls) -> Self:
        return cls.__new(())

    @classmethod
    def __new(cls, libdata: tuple[DmDotset, ...]) -> Self:
        self = super().__new__(cls)
        self.__init(libdata)
        return self

    def __init(self, libdata: tuple[DmDotset, ...]):
        self.__libdata = libdata
        self.__groups = {}
        for dotset in libdata:
            self.__groups[dotset.name] = self.__groups.get(dotset.name, ()) + (dotset,)

    def __repr__(self) -> str:
        return f'<{self.__class__.__name__}({self.ngroup}/{self.ndotset}) at {hex(id(self))}>'

    def __len__(self) -> int:
        return self.__libdata.__len__()

    def __getitem__(self, item: int) -> DmDotset:
        return self.__libdata[item]


    @classmethod
    def fromfile(cls, filepath: str) -> Self:
        with open(filepath, 'r') as f:
            datas = f.read().strip().split('\n')
        return cls.__new(tuple(filter(lambda item:item, (DmDotset.fromdata(data) for data in datas))))


    @property
    def ndotset(self):
        return self.__libdata.__len__()

    @property
    def ngroup(self):
        return self.__groups.__len__()

    def group(self, name: str) -> tuple[DmDotset, ...]:
        return self.__groups.get(name, ())

    def groups(self) -> dict[str, tuple[DmDotset, ...]]:
        return self.__groups.copy()


    @overload
    def scale(self, scale: int | float) -> Self: ...

    @overload
    def scale(self, scaleX: int | float, scaleY: int | float) -> Self: ...

    def scale(self, scaleX: int | float, scaleY: int | float = None) -> Self:
        return self.__class__.__new(tuple(dotset.scale(scaleX, scaleY) for dotset in self.__libdata))

    def list(self) -> None:
        maxLabelLen = (self.ndotset-1).__str__().__len__()
        seperator = "=" * 60
        print(f'\n{seperator}')
        for i, dotset in enumerate(self.__libdata):
            print(f'{i:{maxLabelLen}}: {dotset}')
        print(f'{seperator}\n')
