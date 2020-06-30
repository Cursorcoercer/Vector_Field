import pyglet
from pyglet.window import key
from ctypes import pointer, sizeof
import random
from math import *
sign = lambda x: copysign(1, x)

class field:

    def __init__(self, dots, func, speed, lifespan, realSize, screenSize, theta=0, shift=(0, 0), imag=False, norm=False):
        self.num = dots
        self.F = func
        self.speed = speed
        self.ar = lifespan # 0 indicates particles are immortal
        self.rlsz = (realSize*scsz[0]/scsz[1], realSize)
        self.scsz = screenSize
        self.rrat = (self.scsz[0]/self.rlsz[0]/2, self.scsz[0]/self.rlsz[0]/2) # real ratio
        self.fast = False # double time
        self.theta = theta # use linear transfrom to rotate vector field function
        self.shift = shift # just a standard translation
        self.imag = imag # true if the function returns a complex
        self.norm = norm # true to normalize the vector field
        if self.theta:
            self.c = cos(theta)
            self.s = sin(theta)
            self.F = lambda x, y: self.rotate(*func(*self.protate(x-self.shift[0], y-self.shift[1])))
        elif shift[0] or shift[1]:
            self.F = lambda x, y: func(x-self.shift[0], y-self.shift[1])
        self.reset()
        # Now create a vertex buffer object. For speeed
        self.vbo_id = pyglet.gl.GLuint()
        pyglet.gl.glGenBuffers(1, pointer(self.vbo_id))
        pyglet.gl.glBindBuffer(pyglet.gl.GL_ARRAY_BUFFER, self.vbo_id)
        pyglet.gl.glBufferData(pyglet.gl.GL_ARRAY_BUFFER, sizeof(self.data), 0, pyglet.gl.GL_STATIC_DRAW)

    def rotate(self, x, y):
        # rotate a point by the angle specified in initialization
        return (self.c*x - self.s*y, self.s*x + self.c*y)

    def protate(self, x, y):
        # rotate a point by the negative of the angle specified in initialization
        return (self.c*x + self.s*y, -self.s*x + self.c*y)

    def reset(self):
        self.pts = []
        self.age = []
        # generate all particles within the field of the screen
        # origin as center and rlsz as coordinate of top
        for f in range(self.num):
            self.pts.append(self.new())
            self.age.append(0)
        self.flatten()

    def new(self):
##        p = (self.rlsz[0]*(2*random.random()-1), self.rlsz[1]*(2*random.random()-1))
##        for f in range(3):
##            if 2 < abs(p[0])+abs(p[1]) and 2 < abs(p[0]-12)+abs(p[1]) and 2 < abs(p[0]+12)+abs(p[1]) :
##                p = (self.rlsz[0]*(2*random.random()-1), self.rlsz[1]*(2*random.random()-1))
##        return p
        return (self.rlsz[0]*(2*random.random()-1), self.rlsz[1]*(2*random.random()-1))

    def update(self):
        for f in range(self.num):
            self.age[f] += 1
            try:
                force = self.F(*self.pts[f])
                if self.imag:
                    force = (force.real, force.imag)
                if self.norm:
                    temp = hypot(*force)
                    force = (force[0]/temp, force[1]/temp)
            except: # In case of math error, send dot to the shadow realm.
                force = (0, -3*self.rlsz[1]/(self.speed+self.fast*self.speed))
            self.pts[f] = (self.pts[f][0]+(self.speed+self.fast*self.speed)*force[0],
                           self.pts[f][1]+(self.speed+self.fast*self.speed)*force[1])
            if (self.rlsz[0] < self.pts[f][0] or self.pts[f][0] < -self.rlsz[0] or
                self.rlsz[1] < self.pts[f][1] or self.pts[f][1] < -self.rlsz[1]):
                # oops, we're out of bounds, regenerate the dot
                self.pts[f] = self.new()
                self.age[f] = 0
            elif self.ar and self.ar*2*random.random() < self.age[f]:
                # the dot has reached the end of its lifespan, regenerate the dot
                self.pts[f] = self.new()
                self.age[f] = 0
        self.flatten()

    def flatten(self):
        # transforms data into screen coordinates
        # then puts it in proper opengl type
        lis = []
        for f in range(self.num):
            lis.append(self.rrat[0]*(self.pts[f][0]+self.rlsz[0]))
            lis.append(self.rrat[1]*(self.pts[f][1]+self.rlsz[1]))
        self.data = (pyglet.gl.GLfloat*(self.num*2))(*lis)

    def draw(self):
##        pyglet.gl.glBindBuffer(pyglet.gl.GL_ARRAY_BUFFER, self.vbo_id) # don't need this since only one vbo
        pyglet.gl.glBufferSubData(pyglet.gl.GL_ARRAY_BUFFER, 0, sizeof(self.data), self.data)
##        pyglet.gl.glColor3f(255, 255, 255) # set color of points
        pyglet.gl.glVertexPointer(2, pyglet.gl.GL_FLOAT, 0, 0)
        pyglet.gl.glDrawArrays(pyglet.gl.GL_POINTS, 0, self.num)


if __name__ == "__main__":
    config = pyglet.gl.Config(double_buffer=False)
    window = pyglet.window.Window(caption='vector field', fullscreen=True, config=config, vsync=0)
    window.set_exclusive_mouse()
    fps_display = pyglet.window.FPSDisplay(window=window)
    scsz = window.get_size()

    # various cool vector fields
    ##dots = field(10000, lambda x, y:(sin(y), sin(x)), 1/45, 0, 12, scsz) # cinnamon roll
    ##dots = field(5000, lambda x, y:(sin(y)**2, sin(x)), 1/5, 0, 10, scsz) # snake
    ##dots = field(10000, lambda x, y:(x, y/sin(sqrt(x**2+y**2))), 1/600, 0, 10, scsz) # eye
    ##dots = field(10000, lambda x, y:(x**2-y**2, 2*x*y), 1/60, 600, 10, scsz) # z^2
    ##dots = field(5000, lambda x, y:(1+(y**2-x**2)/(x**2+y**2)**2, -2*x*y/(x**2+y**2)**2), 1/300, 0, 2, scsz) # cylinder flow
    ##dots = field(5000, lambda x, y:((y**2-x**2)/(x**2+y**2)**2, -2*x*y/(x**2+y**2)**2), 1/300, 0, 2, scsz) # dipole
    ##dots = field(5000, lambda x, y:(cos(exp(x+10)), sin((x+10)**2)/y), 1/60, 0, 10, scsz) # chaotic strings
    ##dots = field(10000, lambda x, y:(-sign(y%12-6)*cos(2**(abs(y%12-6)+0.65)), sign(x%12-6)*cos(2**(abs(x%12-6)+0.65))), 1/60, 0, 10, scsz) # bubble frame
    ##dots = field(10000, lambda x, y:((2*x**3-2*x)/(2*y**3-y), (2*y**3-2*y)/(2*x**3-x)), 1/3000, 0, 2, scsz, theta=pi/4, shift=(0, 0.25)) # the fish
    ##dots = field(10000, lambda x, y:(sin(2*y), cos(x**2+y**2+1/(3*y**2+0.3)-3/(atan((x**2-y**2+13)/2)+pi/2))), 1/120, 0, 5, scsz) # balance
    dots = field(10000, lambda x, y:(1)/(x+y*1j), 1/800, 0, 2, scsz, shift=(0, 0), imag=True, norm=True)

    # using a function allows for more complicated calculations on the vector field
    ##def F(x, y):
    ####    x = x%12-6 # modular repeat x
    ####    y = y%12-6 # modular repeat y
    ##    return (x, y)
    ##
    ##dots = field(10000, F, 1/600, 0, 1, scsz)


    pause = False
    stain = False
    fpshow = False


    @window.event
    def on_key_press(symbol, modifiers):
        global dots, pause, stain, fpshow
        if symbol == key.SPACE:
            # press space to pause
            pause = not pause
        elif symbol == key.N:
            # press N to go forward one frame
            dots.update()
        elif symbol == key.S:
            # press S to toggle stain
            stain = not stain
        elif symbol == key.P:
            # press P to toggle fps reading
            fpshow = not fpshow
        elif symbol == key.R:
            # press R to reset field
            dots.reset()
        elif symbol == key.F:
            # press F to toggle fast mode
            dots.fast = 30*(not dots.fast)
        elif symbol == key.ESCAPE:
            # press escape to exit
            pyglet.app.exit()

    def update(dt):
        global dots, pause, stain, fpshow
        if not pause:
            dots.update()
        if not stain:
            pyglet.gl.glClear(pyglet.gl.GL_COLOR_BUFFER_BIT)
        dots.draw()
        if fpshow:
            fps_display.draw()


    FPS = 60
    pyglet.clock.schedule_interval(update, 1/FPS)

    ##pyglet.gl.glClearColor(0.2, 0.4, 0.5, 1.0) # set the color that clears the screen
    ##pyglet.gl.glPointSize(1) # set the size of the points
    pyglet.gl.glEnableClientState(pyglet.gl.GL_VERTEX_ARRAY)

    pyglet.app.run()
