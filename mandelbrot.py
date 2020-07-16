import pygame   as pg
import datetime as dt
import math     as mt
from numba import jit

# (-Xaxis/5.5) # 1280x1000
rescale = 1; itscale = 8; highresmult = 4
it = round(500*itscale);Xwin = round(1280*rescale); Ywin = round(1000*rescale)
escrad = 100; zoom = 1
Xaxis = 3; Yaxis = (Xaxis*Ywin)/Xwin
xd = (-Xaxis/5.5); yd = 0; size = 4
kill = 0; b = 0; drawn = 1; lru = 1/45
screen = pg.display.set_mode([Xwin,Ywin])
screen.fill((200, 200, 200))
color = pg.Color(0); cphase = 18; ncolor = 36

@jit
def mandelbrot(coord,it):
    c = complex(coord[0], coord[1])
    z = complex(0,0); esc = 0
    for i in range(it):
        z = z*z + c
        if abs(z) > escrad:
            esc = i
            break
    return esc, z
@jit
def translate(x,y,step,xd,yd,xax,yax,zoom):
    xtransform = -xax/(2*zoom); ytransfrom = -yax / (2*zoom)
    xstep = (step*((2*x)+1))/2; ystep = (step*((2*y)+1))/2
    return xtransform+xd+xstep, ytransfrom+yd+ystep
@jit
def colors(esc,z):
    mu = esc + 1 - mt.log(abs(mt.log(abs(z))), 2)
    color.hsva = (360 - (360 / ncolor) * ((mu + cphase) % ncolor), 100, 100, 0)
    return color
@jit
def drawquick(it,size):
    Xwinl = int(Xwin / size); Ywinl = int(Ywin / size); step = Xaxis/(Xwinl*zoom)
    canvas = pg.Surface([Xwinl,Ywinl])
    print("Real: " + str(xd) + " Im: " + str(yd) + " Zoom: " + str(zoom))
    for y in range(int(Ywinl)):
        for x in range(int(Xwinl)):
            (esc, z) = mandelbrot(translate(x, y, step, xd, yd, Xaxis, Yaxis,zoom), it)
            if not abs(z) < escrad:
                #mu = esc + 1 - mt.log(abs(mt.log(abs(z))), 2)
                color.hsva = (360-(360/ncolor)*((esc+cphase) % ncolor), 100, 100, 0)
                canvas.set_at((x, y), color)
            else:
                canvas.set_at((x, y), (0, 0, 0))
        print(str(round((y/Ywinl) * 100)) + " %, line " + str(y+1) + " of " + str(Ywinl))
        frame = pg.transform.scale(canvas, [Xwin,Ywin])
        screen.blit(frame, frame.get_rect())
        pg.display.flip()
    print("Real: " + str(xd) + " Im: " + str(yd) + " Zoom: " + str(zoom))
@jit
def drawhighres():
    global screen, b
    Xwinl = int(Xwin * highresmult); Ywinl = int(Ywin * highresmult); step = Xaxis/(Xwinl*zoom)
    canvas = pg.Surface([Xwinl,Ywinl])
    print("Real: " + str(xd) + " Im: " + str(yd) + " Zoom: " + str(zoom))
    for y in range(int(Ywinl)):
        for x in range(int(Xwinl)):
            (esc, z) = mandelbrot(translate(x, y, step, xd, yd, Xaxis, Yaxis,zoom), it * highresmult)
            if not abs(z) < escrad:
                canvas.set_at((x, y), colors(esc,z))
            else:
                canvas.set_at((x, y), (0, 0, 0))
        print(str(round((y/Ywinl) * 100)) + " %, line " + str(y+1) + " of " + str(Ywinl))
        frame = pg.transform.scale(canvas, [Xwin,Ywin])
        screen.blit(frame, frame.get_rect())
        pg.display.flip()
        if y % round(Ywinl / 2) == 0 and y != 0:
            pg.image.save(canvas, str("highres/mandelhigres" + ".R(" + str(xd) + ").I(" + str(yd) + ").Z(" + str(zoom) + ").D_" + str(dt.date.today()) + ".png"))
    frame = pg.transform.scale(canvas, [Xwin, Ywin])
    screen.blit(frame, frame.get_rect())
    print("Real: " + str(xd) + " Im: " + str(yd) + " Zoom: " + str(zoom))
    pg.image.save(canvas, str("highres/mandelhigresfinal" + ".R(" + str(xd) + ").I(" + str(yd) + ").Z(" + str(zoom) + ").D_" + str(dt.date.today()) + ".png"))
    pg.display.flip()
@jit
def drawnormal():
    step = Xaxis / (Xwin * zoom)
    print("Real: " + str(xd) + " Im: " + str(yd) + " Zoom: " + str(zoom))
    for y in range(int(Ywin)):
        for x in range(int(Xwin)):
            (esc, z) = mandelbrot(translate(x, y, step, xd, yd, Xaxis, Yaxis,zoom), it)
            if not abs(z) < escrad:
                screen.set_at((x, y), colors(esc,z))
            else:
                screen.set_at((x, y), (0, 0, 0))
        print(str(round((y / Ywin) * 100)) + " %, line " + str(y+1) + " of " + str(Ywin))
        pg.display.flip()
    print("Real: " + str(xd) + " Im: " + str(yd) + " Zoom: " + str(zoom))
    pg.display.flip()
    pg.image.save(screen,"draw/mandel" + ".R(" + str(xd) + ").I(" + str(yd) + ").Z(" + str(zoom) + ").D_" + str(dt.date.today()) + ".png")

def events():
    global drawn, kill, xd, yd, zoom, step, b
    for event in pg.event.get():
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE: start = b = drawnormal()
        if event.type == pg.KEYDOWN and event.key == pg.K_TAB: drawhighres()
        if event.type == pg.KEYDOWN and event.key == pg.K_BACKSPACE: b = 1
        if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE: kill = 1
        if event.type == pg.KEYDOWN and event.key == pg.K_RETURN: drawquick(int(zoom/lru),size)
        if event.type == pg.KEYDOWN and event.key == pg.K_UP:
            yd = yd - Xaxis/(zoom*10)
            drawquick(int(zoom/lru),size)
        if event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
            yd = yd + Xaxis/(zoom*10)
            drawquick(int(zoom/lru),size)
        if event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
            xd = xd - Xaxis/(zoom*10)
            drawquick(int(zoom/lru),size)
        if event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
            xd = xd + Xaxis/(zoom*10)
            drawquick(int(zoom/lru),size)
        if event.type == pg.KEYDOWN and event.key == pg.K_KP_PLUS:
            zoom = zoom*1.2
            drawquick(int(zoom/lru),size)
        if event.type == pg.KEYDOWN and event.key == pg.K_KP_MINUS:
            zoom = zoom/1.2
            drawquick(int(zoom/lru),size)

drawquick(round(it/4),size-1)

while not kill:
    events()