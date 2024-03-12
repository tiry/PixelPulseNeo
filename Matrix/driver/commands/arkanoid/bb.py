import random
from typing import Any
from PIL import ImageDraw

COLORS = [(255,0,0), (0,255,0), (0,0,255), (255,0,255)]
FRICTION:float = 0.9
SPEED_IMPULSION:float = 1.0

def darker(color:tuple, pct:int) -> tuple:
    return tuple([int(c*pct/100) for c in color])

def lighter(color:tuple, pct:int) -> tuple:
    
    return tuple([int((pct/100)*255) if c==0 else min(int(c*(1+pct/100)), 255) for c in color])

class Actor():
    
    def draw(self, draw:ImageDraw.ImageDraw):
        pass

class Ball(Actor):
   
    def __init__(self, x:int, y:int, color:tuple, r:int) -> None:
        super().__init__()
        self.color = color
        self.x:float =x
        self.y:float =y
        self.r: int=r
        
        vx:float = random.randint(-10, 10)
        if vx == 0:
            vx +=1
        vx = 1.0 / vx
        self.speed:tuple[float, float] =(vx, -1.7)
    
    def draw(self, draw:ImageDraw.ImageDraw):
        draw.ellipse((self.x-self.r, self.y-self.r, self.x+self.r, self.y+self.r ), fill=self.color, outline=darker(self.color, 70))

    def move(self):
        self.x += self.speed[0]
        self.y += self.speed[1]

        
class Paddle(Actor):
   

    def __init__(self, x:int, y:int, width:int) -> None:
        super().__init__()
        
        self.x =x
        self.y =y
        self.width: int=width
        self.x_speed:float =0
    
    def draw(self, draw:ImageDraw.ImageDraw):
        color = (200,200,200)
        draw.rectangle((self.x-  self.width/2, self.y,self.x + self.width/2 , self.y+4), fill=color, outline=darker(color, 50))
        color = (255,0,0)
        draw.rectangle((self.x-  self.width/2+1, self.y-1,self.x -  self.width/2+5 , self.y+5), fill=color, outline=darker(color, 50))
        draw.rectangle((self.x+  self.width/2-5, self.y-1,self.x +  self.width/2-1 , self.y+5), fill=color, outline=darker(color, 50))

        self.x += self.x_speed
        self.x_speed = FRICTION * self.x_speed

    
    def bounce(self, ball:Ball) -> bool:
        if ball.speed[1] >0 and self.x - self.width/2 < ball.x < self.x + self.width/2:
            if abs(self.y - ball.y) <= ball.r:
                # XXX take velocity into account
                ball.speed = (ball.speed[0], -ball.speed[1])
                return True
        return False
    
    def input(self, direction:str):
        if direction=="LEFT":
            self.x_speed -= SPEED_IMPULSION
        elif direction=="RIGHT":
            self.x_speed += SPEED_IMPULSION
        
    
        
class Block(Actor):

    def __init__(self, color:tuple, xy:tuple) -> None:
        super().__init__()
        self.color = color
        self.xy = xy
        self.broken:bool =False
        
    def draw(self, draw:ImageDraw.ImageDraw) -> None:
        if self.broken:
            return
        draw.rectangle(self.xy, fill=self.color, outline=darker(self.color, 70))
        draw.line((self.xy[0], self.xy[1], self.xy[2], self.xy[1]), fill=lighter(self.color, 30))
        draw.line((self.xy[2], self.xy[1], self.xy[2], self.xy[3]), fill=lighter(self.color, 30))

    def bounce(self, ball:Ball) -> bool:
        
        # bound from below the block
        if ball.speed[1] < 0 and self.xy[0] <= ball.x <= self.xy[2] and abs(self.xy[3] - ball.y) < ball.r:
            ball.speed = (ball.speed[0], -ball.speed[1])
            self.broken = True
        
        # bound from the top the block
        if ball.speed[1] > 0 and self.xy[0] <= ball.x <= self.xy[2] and abs(self.xy[1] - ball.y) < ball.r:
            ball.speed = (ball.speed[0], -ball.speed[1])
            self.broken = True
            
        # bound from left the block
        if ball.speed[0] < 0 and self.xy[1] <= ball.y <= self.xy[3] and abs(self.xy[2] - ball.x) < ball.r:
            ball.speed = (-ball.speed[0], ball.speed[1])
            self.broken = True
        
        # bound from right the block
        if ball.speed[0] > 0 and self.xy[1] <= ball.y <= self.xy[3] and abs(self.xy[0] - ball.x) < ball.r:
            ball.speed = (-ball.speed[0], ball.speed[1])
            self.broken = True
        
        return self.broken
    
class Zone():
    
    def __init__(self, x:int, y:int, size:int) -> None:
        self.x: int = x
        self.y: int = y
        self.size: int = size
        self.actors:list[Actor]=[]
    
    def add_actor(self, actor:Actor):
        self.actors.append(actor)
    
    def get_actors(self):
        return self.actors
    
    def inside(self, x:int, y:int) -> bool:
        return self.x <= x < self.x + self.size and self.y <= y < self.y + self.size
    
    def inside_r(self, x:int, y:int, r:int) -> bool:
        return self.inside(x+r, y+r) or self.inside(x-r, y+r) or self.inside(x+r, y-r) or self.inside(x-r, y-r)
    
    def inside_xy(self, xy:tuple) -> bool:
        return self.inside(xy[0], xy[1]) or self.inside(xy[2], xy[3])

    def draw(self, draw:ImageDraw.ImageDraw) -> None:
        draw.rectangle((self.x, self.y, self.x+self.size, self.y+ self.size), outline=(200,200,200))
    
        
class Grid():
    
    def __init__(self, width:int, height:int, size:int) -> None:
        self.width = width
        self.height = height
        self.size = size
        
        self.zones:list[Zone] = []
        
        for x in range(int(width/size) +1):
            for y in range(int(height/size) +1):
                zone = Zone(x*size, y*size, size)
                self.zones.append(zone)
    
    def add_block(self, block:Block):
        for zone in self.zones:
            if zone.inside_xy(block.xy):
                zone.add_actor(block)
    
    def find_blocks(self, x:int, y:int, r:int) -> list[Block]:
        blocks: list[Block] = []
        for zone in self.zones:
            if zone.inside_r(x, y, r):
                blocks.extend(zone.get_actors()) # type: ignore
        return blocks
    
    def draw(self, draw:ImageDraw.ImageDraw, x:int, y:int, r:int) -> None:
        for zone in self.zones:
            if zone.inside_r(x, y, r):
                zone.draw(draw)
    
class Stage(Actor):
    
    def __init__(self, width:int, height:int) -> None:
        super().__init__()
        self.width = width
        self.height = height
        self.blocks: list[Block] = []
        self.grid:Grid = Grid(width, height, 16)

        self.setup_level()
        self.ball = Ball(int(width/2), int(height*0.85), (240,240,200), 2)      
        self.paddle = Paddle(int(width/2), int(height*0.90), 26)
    
    def setup_level(self):    
    
        b_width = 16
        b_height = 4
        b_margin = 2
        
        x_steps = int(self.width / (b_width + b_margin))
        
        decal_x: int = (self.width - (x_steps * (b_width + b_margin))) // 2
    
        for y in range(4):
            color = COLORS[y]
            for x in range(x_steps):
                x0: int = decal_x + x * (b_width + b_margin)
                y0: int = b_margin + y * (b_height + b_margin)
                x1: int = x0+b_width
                y1: int = y0+b_height
                xy = (x0,y0,x1,y1)
                block = Block(color, xy)
                self.blocks.append(block)
                self.grid.add_block(block)
                

    def draw(self, draw:ImageDraw.ImageDraw) -> None:
        for actor in self.blocks:
            actor.draw(draw)
        self.ball.draw(draw)
        self.paddle.draw(draw)
        #self.grid.draw(draw, int(self.ball.x), int(self.ball.y), int(self.ball.r)) 
    
    def reset(self):
        self.ball = Ball(int(self.width/2), int(self.height*0.85), (240,240,200), 2)      
    
    def play(self):
        self.ball.move()    
        
        # borders
        if self.ball.y < self.ball.r:
            self.ball.speed = (self.ball.speed[0], -self.ball.speed[1])
        elif self.ball.y > self.height - self.ball.r:
            self.reset()
            #self.ball.speed = (self.ball.speed[0], -self.ball.speed[1])
        if self.ball.x < self.ball.r:
            self.ball.speed = (-self.ball.speed[0], self.ball.speed[1])
        elif self.ball.x > self.width - self.ball.r:
            self.ball.speed = (-self.ball.speed[0], self.ball.speed[1])

        # blocks
        blocks: list[Block] = self.grid.find_blocks(int(self.ball.x), int(self.ball.y), int(self.ball.r)) 
        if len(blocks) > 0:
            for block in blocks:
                if not block.broken and  block.bounce(self.ball):
                    break
        
        # paddle
        self.paddle.bounce(self.ball)

    def input(self, input_str:str):
        self.paddle.input(input_str)