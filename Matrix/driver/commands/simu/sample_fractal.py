import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation


def sequence(c, z=0):
    while True:
        yield z
        z = z**2 + c


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
        if n >= num_iterations:
            return 0


Xmin = -2
Xmax = 1
Ymin = -0.5
Ymax = 1.0


def render(xmin, xmax, ymin, ymax):
    pixel_density = 64 / (ymax - ymin)
    c = complex_matrix(xmin, xmax, ymin, ymax, pixel_density)
    print(c.shape)
    width, height = c.shape

    res = np.arange(width * height).reshape((width, height))
    # print(res.shape)

    for x in range(0, width):
        for y in range(0, height):
            res[x][y] = is_stable(c[x][y], 32)
    return res


zoom = 1
decalX = 0
decalY = 0

res = render(Xmin * zoom, Xmax * zoom, Ymin * zoom, Ymax * zoom)

fig, ax = plt.subplots()
img = plt.matshow(res, 0)

# print(type(img))
# print(dir(img))


def update(frameNum, img, res):
    global zoom
    global decalX
    global decalY

    zoom = zoom * 0.97
    decalX += 0.005
    decalY += 0.005

    new_res = render(
        Xmin * zoom + decalX,
        Xmax * zoom + decalX,
        Ymin * zoom + decalY,
        Ymax * zoom + decalY,
    )

    img.set_data(new_res)
    # res[:]=new_res[:]
    # plt.matshow(res, 0)
    return (img,)


ani = animation.FuncAnimation(fig, update, fargs=(img, res), frames=1000, interval=50)

plt.show()
# print(res)
