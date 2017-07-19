from math import floor

from .coords import Drawable


class MetaSet(type):

    def __new__(cls, name, bases, attrs):

        tiles = [(key, val) for key, val in attrs.items()
                  if not key.startswith('_') and
                  isinstance(val, (Drawable,))]

        new_attrs = [(key, val) for key, val in attrs.items()
                      if (key, val) not in tiles]

        tile_list = []

        # For each tile
        for key, val in tiles:
            tile_list.append(val)

        # Add the list of tiles to the new class
        new_attrs.append(('_tiles', tile_list))

        return super().__new__(cls, name, bases, dict(new_attrs))


class TileSet(metaclass=MetaSet):
    """
    A tileset funnily enough is the counterpart to a tiled image,
    it's how you define what it is you are going to draw onto said
    image.

    NOTE: You do not use TileSet directly! Instead create a class
    which inherits from this one!
    """

    def __init__(self, FPS=25):
        self._FPS = FPS

    def __getitem__(self, key):

        if isinstance(key, (int,)):
            frame = key
            time = key / self._FPS

        if isinstance(key, (float,)):
            frame = floor(key * self._FPS)
            time = key

        layout = self.layout(frame, time)

        return (self._tiles, layout)

    def layout(self, frame, time):
        raise NotImplementedError('Tilesets must define a layout!')
