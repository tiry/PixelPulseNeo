import cmath
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

def sequence(c, z=0):
    while True:
        yield z
        z = z ** 2 + c

def mandelbrot(candidate):
    return sequence(z=0, c=candidate)

def julia(candidate, parameter):
    return sequence(z=candidate, c=parameter)

def complex_matrix(xmin, xmax, ymin, ymax, pixel_density):
    re = np.linspace(xmin, xmax, int((xmax - xmin) * pixel_density))
    im = np.linspace(ymin, ymax, int((ymax - ymin) * pixel_density))
    return re[np.newaxis, :] + im[:, np.newaxis] * 1j

def is_stable(v, num_iterations):
    for n, z in enumerate(sequence(c=v)):
        if z > 2:
            return n
        if n>=num_iterations:
            return 0

Cx=-0.77568377
Cy= 0.13646737
 
Cx=-0.10109636
Cy= 0.95628651

Xmin=-2
Xmax=1
Ymin=-0.5
Ymax=1.0

Xmin=Cx-3/2
Xmax=Cx+3/2
Ymin=Cy-1.5/2
Ymax=Cy+1.5/2

def render(xmin,xmax,ymin,ymax, max):
    pixel_density=64/(ymax-ymin)
    c = complex_matrix(xmin, xmax, ymin, ymax, pixel_density)
    print(c.shape)
    w= c.shape[0]
    l= c.shape[1]
    res = np.arange(w*l).reshape((w, l))
    for x in range(0, w):
        for y in range(0, l):
            res[x][y]=is_stable(c[x][y], max) 
    return res

zoom = 1
decalX=0
decalY=0
itMax=64

res = render(Xmin*zoom,Xmax*zoom, Ymin*zoom, Ymax*zoom, itMax)

fig, ax = plt.subplots()
img = plt.matshow(res, 0)

def update(frameNum, img, res):

    global zoom
    global decalX
    global decalY
    global itMax
    
    zoom = zoom * 0.97
    #decalX+=0.005
    #decalY+=0.005
    itMax+=1

    new_res = render(Xmin*zoom+decalX,Xmax*zoom+decalX, Ymin*zoom+decalY, Ymax*zoom+decalY, itMax)
    img.set_data(new_res)
    return img,

ani = animation.FuncAnimation(fig, update, fargs=(img, res ),
								frames = 1000,
								interval=50)
plt.show()
