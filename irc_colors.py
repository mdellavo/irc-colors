import sys
import math
import random
from cStringIO import StringIO

try:
    from PIL import Image
except ImportError:
    Image = None

try:
    import requests
except ImportError:
    requests = None

FORMAT_BOLD = "\x02"
FORMAT_COLOR = "\x03"
FORMAT_ITALIC = "\x1d"
FORMAT_UNDERLINE = "\x1f"
FORMAT_REVERSE = "\x16"
FORMAT_RESET = "\0f"


class Color(object):
    def __init__(self, name, index, rgb):
        self.name = name
        self.index = index
        self.rgb = rgb

    def __repr__(self):
        return "<Color({}:{})>".format(self.index, self.name)

    @property
    def title(self):
        return self.name.replace("_", " ").title()

    @property
    def color_code(self):
        return "{:02d}".format(self.index)

COLORS = [
    Color("white", 0, (255, 255, 255)),
    Color("black", 1, (0, 0, 0)),
    Color("blue", 2, (0, 0, 127)),
    Color("green", 3, (0, 147, 0)),
    Color("light_red", 4, (255, 0, 0)),
    Color("brown", 5, (127, 0, 0)),
    Color("purple", 6, (156, 0, 156)),
    Color("orange", 7, (252, 127, 0)),
    Color("yellow", 8, (255, 255, 0)),
    Color("light_green", 9, (0, 252, 0)),
    Color("cyan", 10, (0, 147, 147)),
    Color("light_cyan", 11, (0, 255, 255)),
    Color("light_blue", 12, (0, 0, 255)),
    Color("pink", 13, (255, 0, 255)),
    Color("grey", 14, (127, 127, 127)),
    Color("light grey", 15, (210, 210, 210)),
]

COLOR_MAP = {c.name: c for c in COLORS}


class ColorsHelper(object):
    def __getattr__(self, k):
        if k in COLOR_MAP:
            return COLOR_MAP[k]
        return super(ColorsHelper, self).__getattr__(k)

Colors = ColorsHelper()
C = Colors


def colored(fg, bg, s, *args, **kwargs):
    return FORMAT_COLOR + fg.color_code + ("," + bg.color_code if bg else "") + s.format(*args, **kwargs) + FORMAT_COLOR


def random_color():
    return random.choice(COLORS)


def compare_color(color, rgb):
    return math.sqrt(((color.rgb[0]-rgb[0])*0.3)**2 + ((color.rgb[1]-rgb[1])*0.59)**2 + ((color.rgb[2]-rgb[2])*0.11)**2)


def find_nearest_color(rgb):
    scores = sorted([(compare_color(color, rgb), color) for color in COLORS], key=lambda s: s[0])
    return scores[0][1]


if __name__ == "__main__":

    def words():
        words = sys.argv[2:]
        colored_words = [colored(random_color(), random_color(), word) for word in words]
        print " ".join(colored_words)

    def swatch():
        for fg in COLORS:
            for bg in COLORS:
                s = "{},{} - {} on {}".format(fg.color_code, bg.color_code, fg.title, bg.title)
                print colored(fg, bg, "{:^80}", s)

    def dump():
        c = lambda f, b: colored(f, b, "{:^8}", str(f.color_code) + "," + str(b.color_code))

        for fg in COLORS:
            print "".join(c(fg, bg) for bg in COLORS)

    def _pixel(im, x, y):
        c = find_nearest_color(im.getpixel((x,y)))
        return colored(C.black, c, " ")

    def bitmap():
        url = sys.argv[2]
        res = requests.get(url)
        size = 20
        im = Image.open(StringIO(res.content)).convert("RGB")
        im.thumbnail((size, size))

        for y in range(im.height):
            row = [_pixel(im, x, y) for x in range(im.width)]
            print "".join(row)

    commands = [words, dump, swatch, bitmap]

    command_map = {f.__name__: f for f in commands}
    if len(sys.argv) > 1 and sys.argv[1] in command_map:
        command_map[sys.argv[1]]()