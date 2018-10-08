# A library file for simplifying pygame interaction.  You MUST place this file in the same directory as your game py files.

'''This code is the original work of Luther Tychonievich, who releases it
into the public domain.

As a courtesy, Luther would appreciate it if you acknowledged him in any work
that benefited from this code.'''

from __future__ import division
import pygame, sys
import urllib, os.path

if 'urlretrieve' not in dir(urllib):
    from urllib.request import urlretrieve as _urlretrieve
else:
    _urlretrieve = urllib.urlretrieve

pygame.init()

# a cache to avoid loading images many time
_known_images = {}
_known_sounds = {}


def _image(key, flip=False, w=0, h=0, angle=0):
    '''A method for loading images, caching them, and flipping them'''
    if '__hash__' not in dir(key):
        key = id(key)
    angle, w, h = int(angle), int(w), int(h)
    ans = None
    if (key, flip, w, h, angle) in _known_images:
        ans = _known_images[(key, flip, w, h, angle)]
    elif angle != 0:
        base = _image(key, flip, w, h)
        img = pygame.transform.rotozoom(base, angle, 1)
        _known_images[(key, flip, w, h, angle)] = img
        ans = img
    elif w != 0 or h != 0:
        base = _image(key, flip)
        img = pygame.transform.smoothscale(base, (w, h))
        _known_images[(key, flip, w, h, angle)] = img
        ans = img
    elif flip:
        base = _image(key)
        img = pygame.transform.flip(base, True, False)
        _known_images[(key, flip, w, h, angle)] = img
        ans = img
    else:
        img, _ = _get_image(key)
        _known_images[(key, flip, w, h, angle)] = img
        ans = img
    if w == 0 and h == 0:
        if angle != 0:
            tmp = _image(key, flip, w, h)
        else:
            tmp = ans
        _known_images[(key, flip, tmp.get_width(), tmp.get_height(), angle)] = ans
    return ans


def _image_from_url(url):
    '''a method for loading images from urls by first saving them locally'''
    filename = os.path.basename(url)
    if not os.path.exists(filename):
        if '://' not in url: url = 'http://' + url
        _urlretrieve(url, filename)
    image, filename = _image_from_file(filename)
    return image, filename


def _image_from_file(filename):
    '''a method for loading images from files'''
    image = pygame.image.load(filename).convert_alpha()
    _known_images[filename] = image
    _known_images[(image.get_width(), image.get_height(), filename)] = image
    return image, filename


def _get_image(thing):
    '''a method for loading images from cache, then file, then url'''
    if thing in _known_images: return _known_images[thing], thing
    sid = '__id__' + str(id(thing))
    if sid in _known_images: return _known_images[sid], sid
    if type(thing) is str:
        if os.path.exists(thing): return _image_from_file(thing)
        return _image_from_url(thing)
    _known_images[sid] = thing
    _known_images[(thing.get_width(), thing.get_height(), sid)] = thing
    return thing, sid


def load_sprite_sheet(url_or_filename, rows, columns):
    '''Loads a sprite sheet. Assumes the sheet has rows-by-columns evenly-spaced images and returns a list of those images.'''
    sheet, key = _get_image(url_or_filename)
    height = sheet.get_height() / rows
    width = sheet.get_width() / columns
    frames = []
    for row in range(rows):
        for col in range(columns):
            clip = pygame.Rect(col * width, row * height, width, height)
            frame = sheet.subsurface(clip)
            frames.append(frame)
    return frames


__all__ = ['load_sprite_sheet']


def from_image(x, y, filename_or_url):
    '''Creates a SpriteBox object at the given location from the provided filename or url'''
    image, key = _get_image(filename_or_url)
    return SpriteBox(x, y, image, None)


__all__.append('from_image')


def from_color(x, y, color, width, height):
    '''Creates a SpriteBox object at the given location with the given color, width, and height'''
    return SpriteBox(x, y, None, color, width, height)


__all__.append('from_color')


def from_text(x, y, text, fontname, fontsize, color, bold=False, italic=False):
    '''Creates a SpriteBox object at the given location with the given text as its content'''
    font = pygame.font.match_font(fontname.replace(" ", "").lower())
    if font is None:
        sys.stderr.write("ERROR: no font named " + fontname + "; using default font instead")
    font = pygame.font.Font(font, fontsize)
    font.set_bold(bold)
    font.set_italic(italic)
    if type(color) is str: color = pygame.Color(color)
    return from_image(x, y, font.render(text, True, color))


__all__.append('from_text')


def load_sound(url_or_filename):
    '''Reads a sound file from a given filename or url'''
    if url_or_filename in _known_images: return _known_sounds[url_or_filename]
    if not os.path.exists(url_or_filename):
        filename = os.path.basename(url_or_filename)
        if not os.path.exists(filename):
            _urlretrieve(url_or_filename, filename)
        url_or_filename = filename
    sound = pygame.mixer.Sound(url_or_filename)
    _known_sounds[url_or_filename] = sound
    return sound


__all__.append('load_sound')


class Camera(object):
    '''A camera defines what is visible. It has a width, height, full screen status,
    and can be moved. Moving a camera changes what is visible.
    '''
    is_initialized = False

    #    __slots__ = ["_surface", "x", "y", "speedx", "speedy"]
    def __init__(self, width, height, full_screen=False):
        '''Camera(pixelsWide, pixelsTall, False) makes a window; using True instead makes a full-screen display.'''
        if Camera.is_initialized: raise Exception("You can only have one Camera at a time")
        # if height > 768: raise Exception("The Game Expo screens will only be 768 pixels tall")
        # if width > 1366: raise Exception("The Game Expo screens will only be 1366 pixels wide")
        if full_screen:
            self.__dict__['_surface'] = pygame.display.set_mode([width, height], pygame.FULLSCREEN)
        else:
            self.__dict__['_surface'] = pygame.display.set_mode([width, height])
        self.__dict__['_x'] = 0
        self.__dict__['_y'] = 0
        Camera.is_initialized = True

    def move(self, x, y=None):
        '''camera.move(3, -7) moves the screen's center to be 3 more pixels to the right and 7 more up'''
        if y is None: x, y = x
        self.x += x
        self.y += y

    def draw(self, thing, *args):
        '''camera.draw(box) draws the provided SpriteBox object
        camera.draw(image, x, y) draws the provided image centered at the provided coordinates
        camera.draw("Hi", "Arial", 12, "red", x, y) draws the text Hi in a red 12-point Arial font at x,y'''
        if isinstance(thing, SpriteBox):
            thing.draw(self)
        elif isinstance(thing, pygame.Surface):
            try:
                if len(args) == 1:
                    x, y = args[0]
                else:
                    x, y = args[:2]
                self._surface.blit(thing, [x - thing.get_width() / 2, y - thing.get_height() / 2])
            except e:
                raise Exception("Wrong arguments; try .draw(surface, [x,y])")
        elif type(thing) is str:
            try:
                font = pygame.font.match_font(args[0].replace(" ", "").lower())
                if font is None:
                    sys.stderr.write("ERROR: no font named " + fontname + "; using default font instead")
                size = args[1]
                color = args[2]
                if type(color) is str: color = pygame.Color(color)
                self.draw(pygame.font.Font(font, size).render(thing, True, color), *args[3:])
            except e:
                raise Exception("Wrong arguments; try .draw(text, fontName, fontSize, color, [x,y])")
        else:
            raise Exception("I don't know how to draw a ", type(thing))

    def display(self):
        '''Causes what has been drawn recently by calls to draw(...) to be displayed on the screen'''
        pygame.display.flip()

    def clear(self, color):
        '''Erases the screen by filling it with the given color'''
        if type(color) is str: color = pygame.Color(color)
        self._surface.fill(color)

    def __getattr__(self, name):
        if name in self.__dict__: return self.__dict__[name]
        x, y, w, h = self._x, self._y, self._surface.get_width(), self._surface.get_height()
        if name == 'left': return x
        if name == 'right': return x + w
        if name == 'top': return y
        if name == 'bottom': return y + h
        if name == 'x': return x + w / 2
        if name == 'y': return y + h / 2
        if name == 'center': return x + w / 2, y + h / 2
        if name == 'topleft': return x, y
        if name == 'topright': return x + w, y
        if name == 'bottomleft': return x, y + h
        if name == 'bottomright': return x + w, y + h
        if name == 'width': return w
        if name == 'height': return h
        if name == 'size': return w, h
        if name == 'mousex': return pygame.mouse.get_pos()[0] + self._x
        if name == 'mousey': return pygame.mouse.get_pos()[1] + self._y
        if name == 'mouse': return pygame.mouse.get_pos()[0] + self._x, pygame.mouse.get_pos()[1] + self._y
        if name == 'mouseclick': return any(pygame.mouse.get_pressed())
        raise Exception("There is no '" + name + "' in a Camera object")

    def __setattr__(self, name, value):
        if name in self.__dict__:
            self.__dict__[name] = value
            return
        w, h = self._surface.get_width(), self._surface.get_height()
        if name == 'left':
            self._x = value
        elif name == 'right':
            self._x = value - w
        elif name == 'top':
            self._y = value
        elif name == 'bottom':
            self._y = value - h
        elif name == 'x':
            self._x = value - w / 2
        elif name == 'y':
            self._y = value - h / 2
        elif name == 'center':
            self._x, self._y = value[0] - w / 2, value[1] - h / 2
        elif name == 'topleft':
            self._x, self._y = value[0], value[1]
        elif name == 'topright':
            self._x, self._y = value[0] - w, value[1]
        elif name == 'bottomleft':
            self._x, self._y = value[0], value[1] - h
        elif name == 'bottomright':
            self._x, self._y = value[0] - w, value[1] - h
        elif name in ['width', 'height', 'size', 'mouse', 'mousex', 'mousey', 'mouseclick']:
            raise Exception("You cannot change the '" + name + "' of a Camera object")
        else:
            sys.stderr.write("creating field named " + name)
            self.__dict__[name] = value

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%dx%d Camera centered at %d,%d' % (self.width, self.height, self.x, self.y)


__all__.append('Camera')


class SpriteBox(object):
    '''Intended to represent a sprite (i.e., an image that can be drawn as part of a larger view) and the box that contains it. Has various collision and movement methods built in.'''

    #    __slots__ = ["x","y","speedx","speedy","_w","_h","_key","_image","_color"]
    def __init__(self, x, y, image, color, w=None, h=None):
        '''You should probably use the from_image, from_text, or from_color method instead of this one'''
        self.__dict__['x'] = x
        self.__dict__['y'] = y
        self.__dict__['speedx'] = 0
        self.__dict__['speedy'] = 0
        if image is not None:
            self._set_key(image, False, 0, 0, 0)
            if w is not None:
                if h is not None:
                    self.size = w, h
                else:
                    self.width = w
            elif h is not None:
                self.height = h
        elif color is not None:
            if w is None or h is None: raise Exception("must supply size of color box")
            self.__dict__['_key'] = None
            self.__dict__['_image'] = None
            self.__dict__['_w'] = w
            self.__dict__['_h'] = h
            self.color = color
        pass

    def _set_key(self, name, flip, width, height, angle):
        width = int(width + 0.5)
        height = int(height + 0.5)
        angle = ((int(angle) % 360) + 360) % 360
        unrot = _image(name, flip, width, height)
        if width == 0 and height == 0:
            width = unrot.get_width()
            height = unrot.get_height()
        self.__dict__['_key'] = (name, flip, width, height, angle)
        self.__dict__['_image'] = _image(*self.__dict__['_key'])
        self.__dict__['_color'] = None
        self.__dict__['_w'] = self.__dict__['_image'].get_width()
        self.__dict__['_h'] = self.__dict__['_image'].get_height()

    def __getattr__(self, name):
        x, y, w, h = self.x, self.y, self._w, self._h
        if name == 'xspeed': name = 'speedx'
        if name == 'yspeed': name = 'speedy'
        if name == 'left': return x - w / 2
        if name == 'right': return x + w / 2
        if name == 'top': return y - h / 2
        if name == 'bottom': return y + h / 2
        if name == 'center': return x, y
        if name == 'topleft': return x - w / 2, y - h / 2
        if name == 'topright': return x + w / 2, y - h / 2
        if name == 'bottomleft': return x - w / 2, y + h / 2
        if name == 'bottomright': return x + w / 2, y + h / 2
        if name == 'width': return w
        if name == 'height': return h
        if name == 'width': return w
        if name == 'height': return h
        if name == 'size': return w, h
        if name == 'speed': return self.speedx, self.speedy
        if name == 'rect': return pygame.Rect(self.topleft, self.size)
        if name == 'image': return self.__dict__['_image']
        if name in self.__dict__:
            return self.__dict__[name]
        raise Exception("There is no '" + name + "' in a SpriteBox object")

    def __setattr__(self, name, value):
        w, h = self._w, self._h
        if name == 'xspeed': name = 'speedx'
        if name == 'yspeed': name = 'speedy'
        if name in self.__dict__:
            self.__dict__[name] = value
        elif name == 'left':
            self.x = value + w / 2
        elif name == 'right':
            self.x = value - w / 2
        elif name == 'top':
            self.y = value + h / 2
        elif name == 'bottom':
            self.y = value - h / 2
        elif name == 'center':
            self.x, self.y = value[0], value[1]
        elif name == 'topleft':
            self.x, self.y = value[0] + w / 2, value[1] + h / 2
        elif name == 'topright':
            self.x, self.y = value[0] - w / 2, value[1] + h / 2
        elif name == 'bottomleft':
            self.x, self.y = value[0] + w / 2, value[1] - h / 2
        elif name == 'bottomright':
            self.x, self.y = value[0] - w / 2, value[1] - h / 2
        elif name == 'width':
            self.scale_by(value / w)
        elif name == 'height':
            self.scale_by(value / h)
        elif name == 'size':
            if self.__dict__['_image'] is not None:
                key = self.__dict__['_key']
                self._set_key(key[0], key[1], value[0], value[1], key[4])
            else:
                self.__dict__['_w'] = value[0]
                self.__dict__['_h'] = value[1]
        elif name == 'speed':
            self.speedx, self.speedy = value[0], value[1]
        elif name == 'color':
            self.__dict__['_image'] = None
            self.__dict__['_key'] = None
            if type(value) is str: value = pygame.Color(value)
            self.__dict__['_color'] = value
        elif name == 'image':
            self.__dict__['_color'] = None
            if self.__dict__['_key'] is None:
                self._set_key(value, False, w, h, 0)
            else:
                key = self.__dict__['_key']
                self._set_key(value, *key[1:])
        else:
            sys.stderr.write("creating filed named " + name)
            self.__dict__[name] = value

    def overlap(self, other, padding=0, padding2=None):
        '''b1.overlap(b1) returns a list of 2 values such that self.move(result) will cause them to not overlap
        Returns [0,0] if there is no overlap (i.e., if b1.touches(b2) returns False
        b1.overlap(b2, 5) adds a 5-pixel padding to b1 before computing the overlap
        b1.overlap(b2, 5, 10) adds a 5-pixel padding in x and a 10-pixel padding in y before computing the overlap'''
        if padding2 is None: padding2 = padding
        l = other.left - self.right - padding
        r = self.left - other.right - padding
        t = other.top - self.bottom - padding2
        b = self.top - other.bottom - padding2
        m = max(l, r, t, b)
        if m >= 0:
            return [0, 0]
        elif m == l:
            return [l, 0]
        elif m == r:
            return [-r, 0]
        elif m == t:
            return [0, t]
        else:
            return [0, -b]

    def touches(self, other, padding=0, padding2=None):
        '''b1.touches(b1) returns True if the two SpriteBoxes overlap, False if they do not
        b1.touches(b2, 5) adds a 5-pixel padding to b1 before computing the touch
        b1.touches(b2, 5, 10) adds a 5-pixel padding in x and a 10-pixel padding in y before computing the touch'''
        if padding2 is None: padding2 = padding
        l = other.left - self.right - padding
        r = self.left - other.right - padding
        t = other.top - self.bottom - padding2
        b = self.top - other.bottom - padding2
        return max(l, r, t, b) <= 0

    def bottom_touches(self, other, padding=0, padding2=None):
        '''b1.bottom_touches(b2) returns True if both b1.touches(b2) and b1's bottom edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other, padding + 1, padding2 + 1)[1] < 0

    def top_touches(self, other, padding=0, padding2=None):
        '''b1.top_touches(b2) returns True if both b1.touches(b2) and b1's top edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other, padding + 1, padding2 + 1)[1] > 0

    def left_touches(self, other, padding=0, padding2=None):
        '''b1.left_touches(b2) returns True if both b1.touches(b2) and b1's left edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other, padding + 1, padding2 + 1)[0] > 0

    def right_touches(self, other, padding=0, padding2=None):
        '''b1.right_touches(b2) returns True if both b1.touches(b2) and b1's right edge is the one causing the overlap.'''
        if padding2 is None: padding2 = padding
        return self.overlap(other, padding + 1, padding2 + 1)[0] < 0

    def contains(self, x, y=None):
        '''checks if the given point is inside this SpriteBox's bounds or not'''
        if y is None: x, y = x
        return abs(x - self.x) * 2 < self._w and abs(y - self.y) * 2 < self._h

    def move_to_stop_overlapping(self, other, padding=0, padding2=None):
        '''b1.move_to_stop_overlapping(b2) makes the minimal change to b1's position necessary so that they no longer overlap'''
        o = self.overlap(other, padding, padding2)
        if o != [0, 0]:
            self.move(o)
            if o[0] * self.speedx < 0: self.speedx = 0
            if o[1] * self.speedy < 0: self.speedy = 0

    def move_both_to_stop_overlapping(self, other, padding=0, padding2=None):
        '''b1.move_both_to_stop_overlapping(b2) changes both b1 and b2's positions so that they no longer overlap'''
        o = self.overlap(other, padding, padding2)
        if o != [0, 0]:
            self.move(o[0] / 2, o[1] / 2)
            other.move(-o[0] / 2, -o[1] / 2)
            if o[0] != 0:
                self.speedx = (self.speedx + other.speedx) / 2
                other.speedx = self.speedx
            if o[1] != 0:
                self.speedy = (self.speedy + other.speedy) / 2
                other.speedy = self.speedy

    def move(self, x, y=None):
        '''change position by the given amount in x and y. If only x given, assumed to be a point [x,y]'''
        if y is None: x, y = x
        self.x += x
        self.y += y

    def move_speed(self):
        '''change position by the current speed field of the SpriteBox object'''
        self.move(self.speedx, self.speedy)

    def full_size(self):
        '''change size of this SpriteBox to be the original size of the source image'''
        if self.__dict__['_key'] is None: return
        key = self.__dict__['_key']
        self._set_key(key[0], key[1], 0, 0, key[4])

    def __repr__(self):
        return str(self)

    def __str__(self):
        return '%dx%d SpriteBox centered at %d,%d' % (self._w, self._h, self.x, self.y)

    def copy_at(self, newx, newy):
        '''Make a new SpriteBox just like this one but at the given location instead of here'''
        return SpriteBox(newx, newy, self._image, self._color, self._w, self._h)

    def copy(self):
        '''Make a new SpriteBox just like this one and in the same location'''
        return self.copy_at(self.x, self.y)

    def scale_by(self, multiplier):
        '''Change the size of this SpriteBox by the given factor
        b1.scale_by(1) does nothing; b1.scale_by(0.4) makes b1 40% of its original width and height.'''
        if self.__dict__['_key'] is None:
            self._w *= multiplier
            self._h *= multiplier
        else:
            key = self.__dict__['_key']
            self._set_key(key[0], key[1], key[2] * multiplier, key[3] * multiplier, key[4])

    def draw(self, surface):
        '''b1.draw(camera) is the same as saying camera.draw(b1)
        b1.draw(image) draws a copy of b1 on the image proivided'''
        if isinstance(surface, Camera):
            if self.__dict__['_color'] is not None:
                region = self.rect.move(-surface._x, -surface._y)
                region = region.clip(surface._surface.get_rect())
                surface._surface.fill(self._color, region)
            elif self.__dict__['_image'] is not None:
                surface._surface.blit(self._image, [self.left - surface._x, self.top - surface._y])
        else:
            if self.__dict__['_color'] is not None:
                surface.fill(self._color, self.rect)
            elif self.__dict__['_image'] is not None:
                surface.blit(self._image, self.topleft)

    def flip(self):
        '''mirrors the SpriteBox left-to-right.
        Mirroring top-to-bottom can be accomplished by
            b1.rotate(180)
            b1.flip()'''
        if self.__dict__['_key'] is None: return
        key = self.__dict__['_key']
        self._set_key(key[0], not key[1], *key[2:])

    def rotate(self, angle):
        '''Rotates the SpriteBox by the given angle (in degrees).'''
        if self.__dict__['_key'] is None: return
        key = self.__dict__['_key']
        self._set_key(key[0], key[1], key[2], key[3], key[4] + angle)


_timeron = False
_timerfps = 0


def timer_loop(fps, callback):
    '''Requests that pygame call the provided function fps times a second
    fps: a number between 1 and 60
    callback: a function that accepts a set of keys pressed since the last tick
    ----
    seconds = 0
    def tick(keys):
        seconds += 1/30
        if pygame.K_DOWN in keys:
            print 'down arrow pressed'
        if not keys:
            print 'no keys were pressed since the last tick'
        camera.draw(box)
        camera.display()

    gamebox.timer_loop(30, tick)
    ----'''
    global _timeron, _timerfps
    keys = set([])
    if fps > 1000: fps = 1000
    _timerfps = fps
    _timeron = True
    pygame.time.set_timer(pygame.USEREVENT, int(1000 / fps))
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT: break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: break
        if event.type == pygame.KEYDOWN:
            keys.add(event.key)
        if event.type == pygame.KEYUP and event.key in keys:
            keys.remove(event.key)
        if event.type == pygame.USEREVENT:
            pygame.event.clear(pygame.USEREVENT)
            callback(keys)
    pygame.time.set_timer(pygame.USEREVENT, 0)
    _timeron = False


def pause():
    '''Pauses the timer; an error if there is no timer to pause'''
    if not _timeron: raise Exception("Cannot pause a timer before calling timer_loop(fps, callback)")
    pygame.time.set_timer(pygame.USEREVENT, 0)


def unpause():
    '''Unpauses the timer; an error if there is no timer to unpause'''
    if not _timeron: raise Exception("Cannot pause a timer before calling timer_loop(fps, callback)")
    pygame.time.set_timer(pygame.USEREVENT, int(1000 / _timerfps))


def stop_loop():
    '''Completely quits one timer_loop or keys_loop, usually ending the program'''
    pygame.event.post(pygame.event.Event(pygame.QUIT))


def keys_loop(callback):
    '''Requests that pygame call the provided function each time a key is pressed
    callback: a function that accepts the key pressed
    ----
    def onPress(key):
        if pygame.K_DOWN == key:
            print 'down arrow pressed'
        if pygame.K_a in keys:
            print 'A key pressed'
        camera.draw(box)
        camera.display()

    gamebox.keys_loop(onPress)
    ----'''
    while True:
        event = pygame.event.wait()
        if event.type == pygame.QUIT: break
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE: break
        if event.type == pygame.KEYDOWN:
            callback(event.key)


if __name__ == "__main__":
    camera = Camera(400, 400)

    camera.x = 10

    b = from_text(40, 50, "Blue", "Arial", 40, "red", italic=True, bold=True)
    b.speedx = 3
    b.left += 2
    b.y = 100
    b.move_speed()

    camera.draw(b)
    camera.display()

    smurfs = load_sprite_sheet("http://www.flashpulse.com/moho/smurf_sprite.PNG", 4, 4)


    def tick(keys):
        if keys:
            if pygame.K_0 in keys:
                b.image = smurfs[0]
            elif pygame.K_1 in keys:
                b.image = smurfs[1]
            elif pygame.K_2 in keys:
                b.image = smurfs[2]
            elif pygame.K_3 in keys:
                b.image = smurfs[3]
            elif pygame.K_4 in keys:
                b.image = smurfs[4]
            elif pygame.K_5 in keys:
                b.image = smurfs[5]
            elif pygame.K_6 in keys:
                b.image = smurfs[6]
            elif pygame.K_7 in keys:
                b.image = smurfs[7]
            elif pygame.K_8 in keys:
                b.image = smurfs[8]
            elif pygame.K_9 in keys:
                b.image = smurfs[9]
            elif pygame.K_a in keys:
                stop_loop()
            elif keys:
                b.image = "http://www.pygame.org/docs/_static/pygame_tiny.png"
            b.full_size()
        b.rotate(-5)
        b.center = camera.mouse
        b.bottom = camera.bottom
        camera.draw(b)
        camera.display()


    timer_loop(30, tick)

