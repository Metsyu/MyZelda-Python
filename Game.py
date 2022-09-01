import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import pygame
import time
import map

from pygame.locals import*
from time import sleep
from map import*

class Controller:
    def __init__(self, model):
        self.model = model
        self.keep_going = True
        self.key_right = False
        self.key_left = False
        self.key_up = False
        self.key_down = False

    def setView(self, view):
        self.view = view

    def update(self):
        self.model.link.savePrevLocation()

        for event in pygame.event.get():
            if event.type == QUIT:
                self.keep_going = False
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    self.keep_going = False
                elif event.key == K_RIGHT:
                    self.key_right = True
                    self.model.link.walking = True
                elif event.key == K_LEFT:
                    self.key_left = True
                    self.model.link.walking = True
                elif event.key == K_UP:
                    self.key_up = True
                    self.model.link.walking = True
                elif event.key == K_DOWN:
                    self.key_down = True
                    self.model.link.walking = True
            elif event.type == KEYUP:
                if event.key == K_RIGHT:
                    self.key_right = False
                    self.model.link.walking = False
                elif event.key == K_LEFT:
                    self.key_left = False
                    self.model.link.walking = False
                elif event.key == K_UP:
                    self.key_up = False
                    self.model.link.walking = False
                elif event.key == K_DOWN:
                    self.key_down = False
                    self.model.link.walking = False
                elif event.key == K_LCTRL:
                    self.model.addRemoveSprites()

        if self.key_right:
            self.model.link.direction = "RIGHT"
            self.model.link.x += self.model.link.speed
        if self.key_left:
            self.model.link.direction = "LEFT"
            self.model.link.x -= self.model.link.speed
        if self.key_down:
            self.model.link.direction = "DOWN"
            self.model.link.y += self.model.link.speed
        if self.key_up:
            self.model.link.direction = "UP"
            self.model.link.y -= self.model.link.speed
        if self.key_right or self.key_left or self.key_down or self.key_up:
            self.model.link.updateFrames()


class View:
    scroll_pos_x = 0
    scroll_pos_y = 0
    screen_width = 700
    screen_height = 500

    def __init__(self, controller, model):
        self.model = model
        self.controller = controller
        self.controller.setView(self)
        self.screen = pygame.display.set_mode([View.screen_width, View.screen_height], 32)

    def update(self):
        self.screen.fill([40, 40, 40])
        for sprite in self.model.sprites:
            sprite.drawYourself(self.screen)
        pygame.display.flip()

    @staticmethod
    def goRight():
        if View.scroll_pos_x < View.screen_width:
            View.scroll_pos_x += View.screen_width

    @staticmethod
    def goLeft():
        if View.scroll_pos_x > 0:
            View.scroll_pos_x -= View.screen_width

    @staticmethod
    def goUp():
        if View.scroll_pos_y > 0:
            View.scroll_pos_y -= View.screen_height

    @staticmethod
    def goDown():
        if View.scroll_pos_y < View.screen_height:
            View.scroll_pos_y += View.screen_height


class Model:
    def __init__(self):
        self.sprites = []
        self.link = Link(105, 105)
        self.sprites.append(self.link)

        for brick in bricks:
            self.sprites.append(Brick(brick[0], brick[1]))

        for pot in pots:
            self.sprites.append(Pot(pot[0], pot[1]))

    def update(self):
        for sprite1 in self.sprites:
            if not isinstance(sprite1, Link):
                if isinstance(sprite1, Dagger):
                    for sprite2 in self.sprites:
                        if not isinstance(sprite2, Dagger) and not isinstance(sprite2, Link):
                            if self.isThereACollision(sprite1, sprite2):
                                sprite1.collided(sprite2, sprite2.getDirection())
                                if isinstance(sprite2, Pot):
                                    sprite2.collided(sprite1, sprite1.getDirection())
                else:
                    if self.isThereACollision(self.link, sprite1):
                        if isinstance(sprite1, Brick):
                            self.link.getOutOfSprite(sprite1)
                        if isinstance(sprite1, Pot):
                            sprite1.collided(self.link, self.link.getDirection())
                    if isinstance(sprite1, Pot):
                        for sprite2 in self.sprites:
                            if self.isThereACollision(sprite1, sprite2):
                                if isinstance(sprite2, Brick):
                                    sprite1.collided(sprite2, sprite2.getDirection())

            if not sprite1.update():
                self.sprites.remove(sprite1)

    def isThereACollision(self, s, s1):
        if s.y + s.h < s1.y:
            return False
        if s.y > s1.y + s1.h:
            return False
        if s.x + s.w < s1.x:
            return False
        if s.x > s1.x + s1.w:
            return False
        else:
            return True

    def addRemoveSprites(self):
        self.sprites.append(Dagger(self.link.x + self.link.w/4, self.link.y + self.link.h/4, self.link.direction))


class Sprite:
    def __init__(self, x, y, w, h):
        self.x = x
        self.y = y
        self.w = w
        self.h = h

    def update(self):
        return True

    def drawYourself(self, screen):
        pass

    def collided(self, s, direction):
        pass

    def getDirection(self):
        pass


class Link(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 45, 58)
        self.prev_x = self.x
        self.prev_y = self.y
        self.walking = False
        self.direction = "DOWN"
        self.walking_image_cycle = 0
        self.speed = 6
        self.walking_max_images = 10

        self.standing_forward = pygame.image.load("assets/link_images/link_standing/link_standing_forward.png")
        self.standing_backward = pygame.image.load("assets/link_images/link_standing/link_standing_backward.png")
        self.standing_left = pygame.image.load("assets/link_images/link_standing/link_standing_left.png")
        self.standing_right = pygame.image.load("assets/link_images/link_standing/link_standing_right.png")

        self.walking_forward = []
        for i in range(self.walking_max_images):
            self.walking_forward.append(pygame.image.load("assets/link_images/link_walking/link_walking_forward/link_walking_forward{}.png".format(i)))

        self.walking_backward = []
        for i in range(self.walking_max_images):
            self.walking_backward.append(pygame.image.load("assets/link_images/link_walking/link_walking_backward/link_walking_backward{}.png".format(i)))

        self.walking_left = []
        for i in range(self.walking_max_images):
            self.walking_left.append(pygame.image.load("assets/link_images/link_walking/link_walking_left/link_walking_left{}.png".format(i)))

        self.walking_right = []
        for i in range(self.walking_max_images):
            self.walking_right.append(pygame.image.load("assets/link_images/link_walking/link_walking_right/link_walking_right{}.png".format(i)))

    def update(self):
        if self.x >= View.screen_width:
            View.goRight()
        if self.y >= View.screen_height:
            View.goDown()
        if self.x <= View.screen_width:
            View.goLeft()
        if self.y <= View.screen_height:
            View.goUp()
        return True

    def getOutOfSprite(self, s):
        #Walking right
        if self.x + self.w >= s.x and self.prev_x + self.w <= s.x:
            self.x = self.prev_x
        #Walking left
        elif self.x <= s.x + s.w and self.prev_x >= s.x + s.w:
            self.x = self.prev_x
        #Walking down
        elif self.y + self.h >= s.y and self.prev_y + self.h <= s.y:
            self.y = self.prev_y
        #Walking up
        elif self.y <= s.y + s.h and self.prev_y >= s.y + s.h:
            self.y = self.prev_y

    def savePrevLocation(self):
        self.prev_x = self.x
        self.prev_y = self.y

    def getDirection(self):
        return self.direction

    def updateFrames(self):
        self.walking_image_cycle += 1

        if self.walking_image_cycle == self.walking_max_images:
            self.walking_image_cycle = 0

    def drawYourself(self, screen):
        if self.walking:
            match self.direction:
                case "RIGHT":
                    screen.blit(self.walking_right[self.walking_image_cycle], (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
                case "LEFT":
                    screen.blit(self.walking_left[self.walking_image_cycle], (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
                case "DOWN":
                    screen.blit(self.walking_forward[self.walking_image_cycle], (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
                case "UP":
                    screen.blit(self.walking_backward[self.walking_image_cycle], (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
        else:
            match self.direction:
                case "RIGHT":
                    screen.blit(self.standing_right, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
                case "LEFT":
                    screen.blit(self.standing_left, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
                case "DOWN":
                    screen.blit(self.standing_forward, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
                case "UP":
                    screen.blit(self.standing_backward, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))


class Brick(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 50, 50)
        self.image = pygame.image.load("assets/brick.jpg")

    def drawYourself(self, screen):
        screen.blit(self.image, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))


class Pot(Sprite):
    def __init__(self, x, y):
        super().__init__(x, y, 35, 35)
        self.dagger_collision = False
        self.link_collision = False
        self.brick_collision = False
        self.frames_broken = 0
        self.speed = 12
        self.max_frames_broken = 4
        self.direction = ""

        self.image = pygame.image.load("assets/pot.png")
        self.image_broken = pygame.image.load("assets/pot_broken.png")

    def update(self):
        if self.dagger_collision or self.brick_collision:
            self.frames_broken += 1
        elif self.link_collision:
            match self.direction:
                case "RIGHT":
                    self.x += self.speed
                case "LEFT":
                    self.x -= self.speed
                case "DOWN":
                    self.y += self.speed
                case "UP":
                    self.y -= self.speed

        return self.frames_broken != self.max_frames_broken

    def collided(self, s, direction):
        if isinstance(s, Dagger):
            self.dagger_collision = True
        elif isinstance(s, Link):
            self.direction = direction
            self.link_collision = True
        elif isinstance(s, Brick):
            self.brick_collision = True

    def getDirection(self):
        return self.direction

    def drawYourself(self, screen):
        if self.dagger_collision or self.brick_collision:
            screen.blit(self.image_broken, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
        else:
            screen.blit(self.image, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))


class Dagger(Sprite):
    def __init__(self, x, y, direction):
        super().__init__(x, y, 27, 27)
        self.speed = 12
        self.direction = direction
        self.isActive = True

        self.image_right = pygame.image.load("assets/dagger_right.png")
        self.image_left = pygame.image.load("assets/dagger_left.png")
        self.image_up = pygame.image.load("assets/dagger_up.png")
        self.image_down = pygame.image.load("assets/dagger_down.png")

    def update(self):
        match self.direction:
            case "RIGHT":
                self.x += self.speed
            case "LEFT":
                self.x -= self.speed
            case "DOWN":
                self.y += self.speed
            case "UP":
                self.y -= self.speed

        return self.isActive

    def collided(self, s, direction):
        self.isActive = False

    def getDirection(self):
        return self.direction

    def drawYourself(self, screen):
        match self.direction:
            case "RIGHT":
                screen.blit(self.image_right, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
            case "LEFT":
                screen.blit(self.image_left, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
            case "DOWN":
                screen.blit(self.image_down, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))
            case "UP":
                screen.blit(self.image_up, (self.x - View.scroll_pos_x, self.y - View.scroll_pos_y))

pygame.init()
model = Model()
controller = Controller(model)
view = View(controller, model)
while controller.keep_going:
    controller.update()
    model.update()
    view.update()
    sleep(0.04)
