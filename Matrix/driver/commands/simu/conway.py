import numpy as np

# taken from https://www.geeksforgeeks.org/conways-game-life-python-implementation/

ON = 255
OFF = 0
vals = [ON, OFF]


def randomGrid(W, H):
    """returns a grid of NxN random values"""
    return np.random.choice(vals, W * H, p=[0.2, 0.8]).reshape(W, H)


def runStep(grid):
    W, H = grid.shape
    # copy grid since we require 8 neighbors
    # for calculation and we go line by line
    newGrid = grid.copy()

    for i in range(W):
        for j in range(H):
            # compute 8-neighbor sum
            # using toroidal boundary conditions - x and y wrap around
            # so that the simulation takes place on a toroidal surface.
            total = int(
                (
                    grid[i, (j - 1) % H]
                    + grid[i, (j + 1) % H]
                    + grid[(i - 1) % W, j]
                    + grid[(i + 1) % W, j]
                    + grid[(i - 1) % W, (j - 1) % H]
                    + grid[(i - 1) % W, (j + 1) % H]
                    + grid[(i + 1) % W, (j - 1) % H]
                    + grid[(i + 1) % W, (j + 1) % H]
                )
                / 255
            )

            # apply Conway's rules
            if grid[i, j] == ON:
                if (total < 2) or (total > 3):
                    newGrid[i, j] = OFF
            else:
                if total == 3:
                    newGrid[i, j] = ON

    # return updated data
    return newGrid[:]
