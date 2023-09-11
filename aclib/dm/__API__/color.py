
def check_dmcolor(color: str):
    if color.count('|'):
        raise TypeError(
            f'The color range of "DmDotset" does not support multiple colors seperated by "|", got "{color}"')
    if color in ['0', '1']:
        raise TypeError(
            f'The color range of "DmDotset" does not support adaptive colors ("0"/"1"), got "{color}"')

def cvcolor2dmcolor(clrrange: str) -> str:
    check_dmcolor(clrrange)
    if clrrange.count('--'):
        mincolor, maxcolor = clrrange[-14:-8], clrrange[-6:]
        minrgb = [int(mincolor[i*2:i*2+2], 16) for i in range(3)]
        maxrgb = [int(maxcolor[i*2:i*2+2], 16) for i in range(3)]
        midcolor = ''.join(hex(int(maxrgb[i]/2 + minrgb[i]/2))[2:].zfill(2) for i in range(3))
        diffcolor = ''.join(hex(int(maxrgb[i]/2 - minrgb[i]/2 + 0.5))[2:].zfill(2) for i in range(3))
        return f'{clrrange[-15:-14]}{midcolor}-{diffcolor}'
    return clrrange

def get_inverse_color(rawcolor: str) -> str:
    return f'-{rawcolor}'.removeprefix('--')
