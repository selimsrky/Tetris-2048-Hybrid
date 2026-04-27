"""
stddraw.py

The stddraw module defines functions that allow the user to create a
drawing.  A drawing appears on the canvas.  The canvas appears
in the window.  As a convenience, the module also imports the
commonly used Color objects defined in the color module.
"""

import time
import os
import sys

# Hide the Pygame welcome message
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
import pygame.gfxdraw
import pygame.font

import tkinter as Tkinter
import tkinter.messagebox as tkMessageBox
import tkinter.filedialog as tkFileDialog

#-----------------------------------------------------------------------
# GLOABAL DEĞİŞKENLER VE YARDIMCI FONKSİYONLAR (Hataları önlemek için en üstte)
#-----------------------------------------------------------------------

_DEFAULT_CANVAS_SIZE = 512
_xmin, _xmax = 0.0, 1.0
_ymin, _ymax = 0.0, 1.0
_canvasWidth = float(_DEFAULT_CANVAS_SIZE)
_canvasHeight = float(_DEFAULT_CANVAS_SIZE)
_penRadius = 1.0
_penColor = (0, 0, 0)
_fontFamily, _fontSize = 'Helvetica', 12
_windowCreated = False
_surface = None
_background = None
_keysTyped = []

def _pygameColor(c):
    """Color nesnelerini Pygame'in anlayacağı formata çevirir."""
    if isinstance(c, (tuple, list)):
        return c
    
    r, g, b = 0, 0, 0
    # Metodları veya attribute'ları kontrol et
    if hasattr(c, 'getRed'): r = c.getRed()
    elif hasattr(c, 'red'): r = c.red
    elif hasattr(c, 'r'): r = c.r
        
    if hasattr(c, 'getGreen'): g = c.getGreen()
    elif hasattr(c, 'green'): g = c.green
    elif hasattr(c, 'g'): g = c.g
        
    if hasattr(c, 'getBlue'): b = c.getBlue()
    elif hasattr(c, 'blue'): b = c.blue
    elif hasattr(c, 'b'): b = c.b
        
    return pygame.Color(int(r), int(g), int(b))

def _scaleX(x):
    return _canvasWidth * (x - _xmin) / (_xmax - _xmin)

def _scaleY(y):
    return _canvasHeight * (_ymax - y) / (_ymax - _ymin)

def _factorX(w):
    return w * _canvasWidth / abs(_xmax - _xmin)

def _factorY(h):
    return h * _canvasHeight / abs(_ymax - _ymin)

def _userX(x):
    return _xmin + x * (_xmax - _xmin) / _canvasWidth

def _userY(y):
    return _ymax - y * (_ymax - _ymin) / _canvasHeight

def _makeSureWindowCreated():
    global _windowCreated, _background, _surface
    if not _windowCreated:
        pygame.init()
        _background = pygame.display.set_mode([int(_canvasWidth), int(_canvasHeight)])
        pygame.display.set_caption('Tetris 2048')
        _surface = pygame.Surface((int(_canvasWidth), int(_canvasHeight)))
        _surface.fill((255, 255, 255))
        _windowCreated = True

#-----------------------------------------------------------------------
# ÇİZİM FONKSİYONLARI
#-----------------------------------------------------------------------

def setCanvasSize(w=_DEFAULT_CANVAS_SIZE, h=_DEFAULT_CANVAS_SIZE):
    global _canvasWidth, _canvasHeight, _windowCreated
    _canvasWidth, _canvasHeight = float(w), float(h)
    _makeSureWindowCreated()

def setXscale(min=0.0, max=1.0):
    global _xmin, _xmax
    _xmin, _xmax = float(min), float(max)

def setYscale(min=0.0, max=1.0):
    global _ymin, _ymax
    _ymin, _ymax = float(min), float(max)

def setPenRadius(r=0.005):
    global _penRadius
    _penRadius = r * _canvasWidth

def setPenColor(c=(0,0,0)):
    global _penColor
    _penColor = _pygameColor(c)

def setFontFamily(f='Helvetica'):
    global _fontFamily
    _fontFamily = f

def setFontSize(s=12):
    global _fontSize
    _fontSize = s

def clear(c=(255, 255, 255)):
    _makeSureWindowCreated()
    _surface.fill(_pygameColor(c))

def point(x, y):
    _makeSureWindowCreated()
    pygame.draw.circle(_surface, _penColor, (int(_scaleX(x)), int(_scaleY(y))), int(_penRadius))

def line(x0, y0, x1, y1):
    _makeSureWindowCreated()
    pygame.draw.line(_surface, _penColor, (_scaleX(x0), _scaleY(y0)), (_scaleX(x1), _scaleY(y1)), max(1, int(_penRadius)))

def filledRectangle(x, y, w, h):
    _makeSureWindowCreated()
    rect = pygame.Rect(_scaleX(x), _scaleY(y + h), _factorX(w), _factorY(h))
    pygame.draw.rect(_surface, _penColor, rect)

def rectangle(x, y, w, h):
    _makeSureWindowCreated()
    # Bu fonksiyon dikdörtgenin sadece dış çerçevesini çizer
    rect = pygame.Rect(_scaleX(x), _scaleY(y + h), _factorX(w), _factorY(h))
    pygame.draw.rect(_surface, _penColor, rect, max(1, int(_penRadius)))

def filledSquare(x, y, r):
    _makeSureWindowCreated()
    rect = pygame.Rect(_scaleX(x - r), _scaleY(y + r), _factorX(2 * r), _factorY(2 * r))
    pygame.draw.rect(_surface, _penColor, rect)

def square(x, y, r):
    _makeSureWindowCreated()
    rect = pygame.Rect(_scaleX(x - r), _scaleY(y + r), _factorX(2 * r), _factorY(2 * r))
    pygame.draw.rect(_surface, _penColor, rect, max(1, int(_penRadius)))

def text(x, y, s):
    _makeSureWindowCreated()
    font = pygame.font.SysFont(_fontFamily, _fontSize)
    surf = font.render(str(s), True, _penColor)
    _surface.blit(surf, surf.get_rect(center=(_scaleX(x), _scaleY(y))))

def boldText(x, y, s):
    _makeSureWindowCreated()
    font = pygame.font.SysFont(_fontFamily, _fontSize, bold=True)
    surf = font.render(str(s), True, _penColor)
    _surface.blit(surf, surf.get_rect(center=(_scaleX(x), _scaleY(y))))

def picture(pic, x, y):
    _makeSureWindowCreated()
    img_surface = pic._surface 
    rect = img_surface.get_rect(center=(_scaleX(x), _scaleY(y)))
    _surface.blit(img_surface, rect)

def show(msec=0):
    _makeSureWindowCreated()
    _background.blit(_surface, (0, 0))
    pygame.display.flip()
    global _keysTyped
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            # Converting the key codes into texts
            if event.key == pygame.K_LEFT: 
                _keysTyped.append('left')
            elif event.key == pygame.K_RIGHT: 
                _keysTyped.append('right')
            elif event.key == pygame.K_UP: 
                _keysTyped.append('up')
            elif event.key == pygame.K_DOWN: 
                _keysTyped.append('down')
            elif event.key == pygame.K_SPACE: 
                _keysTyped.append('space')
            elif event.key == pygame.K_RETURN:
                _keysTyped.append('enter')    
            else: 
                _keysTyped.append(event.key)
    if msec > 0:
        time.sleep(msec / 1000.0)

def mousePressed():
    return pygame.mouse.get_pressed()[0]

def mouseX():
    return _userX(pygame.mouse.get_pos()[0])

def mouseY():
    return _userY(pygame.mouse.get_pos()[1])

def hasNextKeyTyped():
    return len(_keysTyped) > 0

def nextKeyTyped():
    if len(_keysTyped) > 0:
        return _keysTyped.pop(0)
    return None

def clearKeysTyped():
    global _keysTyped
    _keysTyped = []