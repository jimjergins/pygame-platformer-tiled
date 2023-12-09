import os
import random
import math
from typing import Tuple

import pygame
from os import listdir
from os.path import isfile, join
from pytmx.util_pygame import load_pygame

pygame.init()

pygame.display.set_caption("Platformer")

WIDTH, HEIGHT = (1000, 960)
FPS = 60
PLAYER_VEL = 3.5
FLAGS = pygame.DOUBLEBUF | pygame.RESIZABLE
window = pygame.display.set_mode((WIDTH, HEIGHT), FLAGS, 16)


def flip(sprites):
    return [pygame.transform.flip(sprite, True, False) for sprite in sprites]


def load_sprite_sheets(dir1, dir2, width, height, direction=False):
    path = join("assets", dir1, dir2)
    images = [f for f in listdir(path) if isfile(join(path, f))]

    all_sprites = {}

    for image in images:
        sprite_sheet = pygame.image.load(join(path, image)).convert_alpha()

        sprites = []
        for i in range(sprite_sheet.get_width() // width):
            surface = pygame.Surface((width, height), pygame.SRCALPHA, 32)
            rect = pygame.Rect(i * width, 0, width, height)
            surface.blit(sprite_sheet, (0, 0), rect)
            # 64x64 now
            # sprites.append(pygame.transform.scale2x(surface))
            sprites.append(surface)

        if direction:
            # remove .png, append "_left" or "_right"
            all_sprites[image.replace(".png", "") + "_right"] = sprites
            all_sprites[image.replace(".png", "") + "_left"] = flip(sprites)
        else:
            all_sprites[image.replace(".png", "")] = sprites

    return all_sprites


def get_block(size):
    path = join("assets", "Terrain", "Terrain.png")
    image = pygame.image.load(path).convert_alpha()
    surface = pygame.Surface((size, size), pygame.SRCALPHA, 32)
    rect = pygame.Rect(96, 0, size, size)
    surface.blit(image, (0, 0), rect)
    return pygame.transform.scale2x(surface)


class Player(pygame.sprite.Sprite):
    COLOR = (255, 0, 0)
    GRAVITY = 1
    SPRITES = load_sprite_sheets("MainCharacters", "MaskDude", 32, 32, True)
    ANIMATION_DELAY = 3

    def __init__(self, x, y, width, height, id, sprite_id=0):
        super().__init__()
        sprite_name = PLAYER_SPRITE_DICTIONARY[sprite_id]
        self.SPRITES = load_sprite_sheets("MainCharacters", sprite_name, 32, 32, True)

        self.rect = pygame.Rect(x, y, width, height)
        # how fast we are going
        self.x_vel = 0
        self.y_vel = 0
        self.mask = None
        self.direction = "left"
        self.animation_count = 0
        self.fall_count = 0
        self.jump_count = 0
        self.hit = False
        self.hit_count = 0
        self.death_count = 3
        self.times_hit = 0
        self.id = id
        self.controller = None
        self.did_die = False
        self.apply_hit = 0

    def jump(self):
        self.y_vel = -self.GRAVITY * 5
        self.animation_count = 0
        self.jump_count += 1
        if self.jump_count == 1:
            self.fall_count = 0
        if self.jump_count == 2:
            self.y_vel *= 2
        if self.jump_count == 3:
            self.y_vel *= 3

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def make_hit(self):
        print("make hit", self.hit)
        self.hit = True
        self.hit_count = 0
        self.apply_hit += 2

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def loop(self, fps):
        # falling based on how long we have been in free-fall
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)

        # move slower if we are hit by 50%
        if self.hit:
            self.move(self.x_vel * 0.5, self.y_vel * 0.5)
        else:
            self.move(self.x_vel, self.y_vel)

        if self.times_hit > 2:
            self.times_hit = 0
            self.death_count -= 1
            self.did_die = True
            print("hit 3 times - death!")

        if self.hit:
            if self.apply_hit % 4 == 0 and self.hit_count == 0:
                self.apply_hit = 0
                self.times_hit += 1
                # bounces back the player when hit so we don't hit more than one time
                if self.direction == "left":
                    self.rect.x += 35
                else:
                    self.rect.x -= 35

                if self.fall_count > 0:
                    self.rect.y -= 32

            self.hit_count += 1

        if self.hit_count > FPS * 2:
            self.hit = False
            self.hit_count = 0

        # +1 fall count per fps
        self.fall_count += 1
        self.update_sprite()

    def landed(self):
        self.fall_count = 0
        self.y_vel = 0
        self.jump_count = 0

    def hit_head(self):
        self.count = 0
        self.y_vel *= -1

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel < 0:
            if self.jump_count == 1:
                sprite_sheet = "jump"
            elif self.jump_count >= 2:
                sprite_sheet = "double_jump"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()

    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.sprite, (self.rect.x - offset_x, self.rect.y - offset_y))


class Object(pygame.sprite.Sprite):
    def __init__(self, x, y, screen_x, screen_y, image, width, height, name=None):
        super().__init__()
        self.width = width
        self.height = height
        self.name = name
        self.x = screen_x
        self.y = screen_y
        self.rect = pygame.Rect(screen_x, screen_y, width, height)
        self.image = None

        if image is not None:
            image.blit(image, (0, 0), self.rect)
            self.image = image  # pygame.Surface((width, height), pygame.SRCALPHA)

    def draw(self, win, offset_x, offset_y):
        win.blit(self.image, (self.rect.x - offset_x, self.rect.y - offset_y))


class Block(Object):
    def __init__(self, x, y, screen_x, screen_y, image, sizeW, sizeH):
        super().__init__(x, y, screen_x, screen_y, image, sizeW, sizeH)
        # block = get_block(size)
        # self.image.blit(block, (0, 0))
        self.mask = pygame.mask.from_surface(self.image)


class AnimatedObject(Object):
    ANIMATION_DELAY = 3

    def __init__(self, x, y, screen_x, screen_y, width, height, location, name, image=None):
        super().__init__(x, y, screen_x, screen_y, image, width, height, name)
        self.sprites = load_sprite_sheets(location, name, width, height)
        self.image = self.sprites["off"][0]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_count = 0
        self.animation_name = "off"

    def on(self):
        self.animation_name = "on"

    def off(self):
        self.animation_name = "off"

    def loop(self):
        sprites = self.sprites[self.animation_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.image = sprites[sprite_index]
        self.animation_count += 1
        # update()
        self.rect = self.image.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.image)

        if self.animation_count // self.ANIMATION_DELAY > len(sprites):
            self.animation_count = 0


# moving object is a block that moves from left to right
class MovingObject (AnimatedObject):
    def __init__(self, x, y, screen_x, screen_y, width, height, location, name, image=None):
        super().__init__(x, y, screen_x, screen_y, width, height, location, name, image)
        self.sprite_sheet = "idle"
        
    # this method will move an object based on the player
    def loop(self):
        # falling based on how long we have been in free-fall
        self.y_vel += min(1, (self.fall_count / FPS) * self.GRAVITY)
        self.move(self.x_vel, self.y_vel)

        if self.hit:
            self.hit_count += 1
        if self.hit_count > FPS * 2:
            self.hit = False
            self.hit_count = 0

        # +1 fall count per fps
        self.fall_count += 1
        self.update_sprite()

    def move(self, dx, dy):
        self.rect.x += dx
        self.rect.y += dy

    def move_left(self, vel):
        self.x_vel = -vel
        if self.direction != "left":
            self.direction = "left"
            self.animation_count = 0

    def move_right(self, vel):
        self.x_vel = vel
        if self.direction != "right":
            self.direction = "right"
            self.animation_count = 0

    def update_sprite(self):
        sprite_sheet = "idle"
        if self.hit:
            sprite_sheet = "hit"
        elif self.y_vel > self.GRAVITY * 2:
            sprite_sheet = "fall"
        elif self.x_vel != 0:
            sprite_sheet = "run"

        sprite_sheet_name = sprite_sheet + "_" + self.direction
        sprites = self.SPRITES[sprite_sheet_name]
        sprite_index = (self.animation_count // self.ANIMATION_DELAY) % len(sprites)
        self.sprite = sprites[sprite_index]
        self.animation_count += 1
        self.update()
    
    def update(self):
        self.rect = self.sprite.get_rect(topleft=(self.rect.x, self.rect.y))
        self.mask = pygame.mask.from_surface(self.sprite)


class Controller:
    def __init__(self, joystick):
        self.controller = joystick
        self.buttonCount = joystick.get_numbuttons()
        self.hatCount = joystick.get_numhats()
        self.axesCount = joystick.get_numaxes()
        self.ballCount = joystick.get_numballs()
        self.jumpButtonId = 0  # first button
        self.attackButtonId = 2  # second button
        self.buttonsPressed = []

    def GetHatPosition(self, hat_id):
        # returns (x,y)
        if self.hatCount > hat_id:
            x, y = self.controller.get_hat(hat_id)
            print("hat position: ", x,y)
            if x > 0 and y == 0:
                return "right"
            elif x < 0 and y == 0:
                return "left"
        return "center"

    def GetAxisPosition(self, axis_id):
        # returns (x,y)
        if self.axesCount > axis_id:
            pos = self.controller.get_axis(axis_id)
            sign = pos < 0
            # print("axes position: ", pos)
            if sign and pos < -0.80:
                return "left"
            if pos > 0.80 and not sign:
                return "right"
        return "center"

    def GetBallPosition(self, ball_id):
        # returns (x,y)
        if self.ballCount > ball_id:
            x, y = self.controller.get_ball(ball_id)
            if x > 0 and y == 0:
                return "right"
            elif x < 0 and y == 0:
                return "left"
        return "center"

    def GetPressedButtons(self):
        return self.buttonsPressed

    def SetButtonPressed(self, button_id):
        is_significant = self.jumpButtonId == button_id or self.attackButtonId == button_id
        if is_significant and len(self.buttonsPressed) == 0:
            print("button pressed ", button_id)
            self.buttonsPressed.append(button_id)
        elif is_significant and len(self.buttonsPressed) > 0:
            for idx in self.buttonsPressed:
                if idx == button_id:
                    # button is already in there and is marked pressed
                    return
        elif is_significant:
            print("button pressed ", button_id)
            self.buttonsPressed.append(button_id)

    def SetButtonUnpressed(self, button_id):
        is_significant = self.jumpButtonId == button_id or self.attackButtonId == button_id
        if is_significant and len(self.buttonsPressed) < 1:
            return
        elif is_significant and len(self.buttonsPressed) > -1:
            print("button released ", button_id)
            for idx in self.buttonsPressed:
                if idx == button_id:
                    self.buttonsPressed.remove(button_id)

    def DidJumpButtonPress(self):
        if self.controller.get_button(self.jumpButtonId):
            self.SetButtonPressed(self.jumpButtonId)
            return True

        return False

    def DidAttackButtonPress(self):
        if self.controller.get_button(self.attackButtonId):
            print("pressing attack button")
            self.SetButtonPressed(self.attackButtonId)
            return True

        return False

    def GetPower(self):
        return self.controller.get_power_level()

    def GetGuid(self):
        return self.controller.get_guid()

# change this to use a tilemap
# def get_background(name):
#     image = pygame.image.load(join("assets", "Background", name))
#     _, _, width, height = image.get_rect()
#     tiles = []
#
#     for i in range(WIDTH // width + 1):
#         for j in range(HEIGHT // height + 1):
#             # the position of the top left corner of the tile being added.
#             pos = (i * width, j * height)
#             tiles.append(pos)
#     return tiles, image

def worldCoordsToScreenCoords(x, y, block_size_w, block_size_h):
    return x * block_size_w, y * block_size_h


def draw(level, window, map, player, blocks, objects, offset_x, offset_y):
    w_rect = window.get_rect()
    window_top = w_rect.top - level.block_size_h
    window_bottom = w_rect.bottom + level.block_size_h
    window_left = w_rect.left - level.block_size_w
    window_right = w_rect.right + level.block_size_w

    # this is the background,things that are not interactive with the player or game
    for x, y, image in map:
        # if x < w_rect.left and x > w_rect.right:
        #     #don't draw if the block is off the screen on the x axis
        #     continue

        # if y < w_rect.top and y > w_rect.bottom:
        #     #don't draw if the block is off the screen on the y axis
        #     continue

        if y - offset_y < window_top or y - offset_y > window_bottom:
            continue
        elif x - offset_x < window_left or x - offset_x > window_right:
            continue
        # elif x - offset_x < 0:
        #     window.blit(image, (x, y))
        # else:
        #     window.blit(image, (x - offset_x, y - offset_y))
        else:
            window.blit(image, (x - offset_x, y - offset_y))

    # these are the floor blocks. They do not move
    for obj in blocks:
        if obj.rect.y - offset_y < window_top or obj.rect.y - offset_y > window_bottom:
            continue
        elif obj.rect.x - offset_x < window_left or obj.rect.x - offset_x > window_right:
            continue
        else:
            obj.draw(window, offset_x, offset_y)

    # these are things the player interacts with
    for obj in objects:
        if obj.rect.y - offset_y < window_top or obj.rect.y - offset_y > window_bottom:
            continue
        elif obj.rect.x - offset_x < window_left or obj.rect.x - offset_x > window_right:
            continue
        else:
            obj.draw(window, offset_x, offset_y)

    player.draw(window, offset_x, offset_y)

    # draw the menu
    level.draw_menu(window)

    pygame.display.update()


def handle_vertical_collision(player, objects, dy):
    collided_objects = []
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            if dy > 0:
                player.rect.bottom = obj.rect.top
                player.landed()
            elif dy < 0:
                player.rect.top = obj.rect.bottom
                player.hit_head()

            collided_objects.append(obj)

    return collided_objects


def collide(player, objects, dx):
    player.move(dx, 0)
    player.update()
    collided_object = None
    for obj in objects:
        if pygame.sprite.collide_mask(player, obj):
            collided_object = obj
            break

    player.move(-dx, 0)
    player.update()
    return collided_object


def handle_move(player, controllers, objects):
    keys = pygame.key.get_pressed()

    # remove this to handle
    player.x_vel = 0
    collide_left = collide(player, objects, -PLAYER_VEL * 2)
    collide_right = collide(player, objects, PLAYER_VEL * 2)

    if keys[pygame.K_LEFT] and not collide_left:
        player.move_left(PLAYER_VEL)

    if keys[pygame.K_RIGHT] and not collide_right:
        player.move_right(PLAYER_VEL)

    for cntrlr in controllers:
        hat_direction = cntrlr.GetHatPosition(0)
        axis_direction = cntrlr.GetAxisPosition(0)
        if (hat_direction == "left" or axis_direction == "left") and not collide_left:
            player.move_left(PLAYER_VEL)
        elif (hat_direction == "right" or axis_direction == "right") and not collide_right:
            player.move_right(PLAYER_VEL)

    vertical_collide = handle_vertical_collision(player, objects, player.y_vel)
    to_check = [collide_left, collide_right, *vertical_collide]

    for obj in to_check:
        if obj and obj.name == "Fire":
            player.make_hit()


def draw_text(text, color, x, y, window, isTitle=False):
    size = 15
    
    if isTitle:
        size = 30
    
    font = pygame.font.SysFont("arialblack", size)
    
    img = font.render(text, True, color)
    window.blit(img, (x,y))


CLASS_DICTIONARY = {
    'AnimatedObject': AnimatedObject,
    'MovingObject': MovingObject
}

LEVEL_DICTIONARY = {
    0: ["assets", "world", "Intro.tmx"],
    2: ["assets", "world", "Level_0.tmx"],
    1: ["assets", "world", "Level_1.tmx"],
    3: ["assets", "world2", "Level_2.tmx"],
    4: ["assets", "world2", "Level_3.tmx"],
    5: ["assets", "world2", "Level_4.tmx"],
    6: ["assets", "world2", "Level_5.tmx"],
    7: ["assets", "world2", "Level_6.tmx"]
}

PLAYER_SPRITE_DICTIONARY = {
    0: "MaskDude",
    1: "NinjaFrog",
    2: "PinkMan",
    3: "VirtualGuy"
}

class Level():
    def __init__(self, id):
        self.level_id = id
        self.objects = []
        self.blocks = []
        self.background = []
        self.level_start_x = 100
        self.level_start_y = 100
        self.level_end_x = 50
        self.level_end_y = 50
        self.level_end_width = 32
        self.level_end_height = 32
        level_str = ""
        for slug in LEVEL_DICTIONARY[self.level_id]:
            level_str = join(level_str, slug)
        print("loading level: ", self.level_id)
        self.tiled_map = load_pygame(join(os.getcwd(), level_str))
        self.level_h = self.tiled_map.height
        self.level_w = self.tiled_map.width
        self.block_size_h = self.tiled_map.tileheight
        self.block_size_w = self.tiled_map.tilewidth
        self.properties = None
        self.next_level = self.level_id + 1
        if self.next_level > len(LEVEL_DICTIONARY):
            self.next_level = -1
        
        # for the menu
        self.player = None
        self.controller = None
        self.text_color = (255,255,255)
    
    def level_parse(self):
        for layerObj in self.tiled_map.layers:
            layerProperties = layerObj.properties
            # set some properties
            if layerObj.name == "Level_Properties":
                self.properties = layerProperties
                self.block_size_w = int(layerProperties['LevelBlockSizeWidth'])
                self.block_size_h = int(layerProperties['LevelBlockSizeHeight'])

                _x = layerProperties['LevelStartX']
                _y = layerProperties['LevelStartY']
                self.level_start_x, self.level_start_y = worldCoordsToScreenCoords(int(_x), int(_y), self.block_size_w, self.block_size_h)

                _x = layerProperties['LevelEndX']
                _y = layerProperties['LevelEndY']
                self.level_end_x, self.level_end_y = worldCoordsToScreenCoords(int(_x), int(_y), self.block_size_w, self.block_size_h)

                # this layer should not have any blocks to load.
                continue

            # background first
            for x, y, image in layerObj.tiles():
                screen_x, screen_y = worldCoordsToScreenCoords(x, y, self.block_size_w, self.block_size_h)
                if layerObj.name == "Background":
                    self.background.append([screen_x, screen_y, image])
                elif layerObj.name == "Blocks":
                    blk = Block(x, y, screen_x, screen_y, image, self.block_size_w, self.block_size_h)
                    self.blocks.append(blk)
                elif "Objects" in layerObj.name:
                    object_width = image.get_width()
                    object_height = image.get_height()
                    world_y_offset = object_height - self.block_size_h
                    screen_x, screen_y = worldCoordsToScreenCoords(x, y, self.block_size_w, self.block_size_h)
                    screen_y -= world_y_offset
                    if "Animated" in layerObj.name:
                        # x, y, screen_x, screen_y, width, height, location, name, image=None
                        object_instance = CLASS_DICTIONARY[layerProperties['objectType']](x, y, screen_x, screen_y,
                                                                                        object_width, object_height,
                                                                                        layerProperties[
                                                                                            'objectLocation'],
                                                                                        layerProperties[
                                                                                            'objectName'])
                        self.objects.append(object_instance)

    def get_blocks(self):
        return self.blocks

    def set_menu(self, player):
        self.player = player
        if player.controller:
            self.controller = player.controller

    def draw_menu(self, window):
        pygame.draw.rect(window, (0, 0, 0), (0, 0, WIDTH, 70))
        # here we are going to draw the top bar to display some cool stats
        draw_text('Player: ' + str(self.player.id), self.text_color, 10, 10, window)
        if self.controller:
            # draw_text('Controller Id: ' + self.controller.GetGuid(), self.text_color, 130, 10, window)
            draw_text('Controller Battery: ' + self.controller.GetPower(), self.text_color, 130, 10, window)
        else:
            # draw_text('Controller Id: n/a ', self.text_color, 130, 10, window)
            draw_text('Controller Battery: n/a ', self.text_color, 130, 10, window)

        draw_text('Times Hit: ' + str(self.player.times_hit), self.text_color, 10, 35, window)
        draw_text('Lives: ' + str(self.player.death_count), self.text_color, 130, 35, window)
        draw_text('Current Level: ' + str(self.level_id), self.text_color, 530, 15, window, True)

def load_level(level_id):
    level = Level(level_id)
    level.level_parse()

    HEIGHT = level.block_size_h * level.level_h
    window = pygame.display.set_mode((WIDTH, HEIGHT), FLAGS, 16)
    return (window, level)

def game_over(player, controllers, player_sprite_id=0):
    window, level = load_level(0)
    player = Player(level.level_start_x, level.level_start_y, level.block_size_w, level.block_size_h, player.id, player_sprite_id)
    
    if len(controllers) > 0:
        player.controller = controllers[0]
    level.set_menu(player)

    return (window, level, player)

def main(window):
    # level stats
    pygame.font.init()
    current_player = 1
    player_sprite_id = 0

    clock = pygame.time.Clock()

    # load the first level 
    window, level = load_level(0)
    player = Player(level.level_start_x, level.level_start_y, level.block_size_w, level.block_size_h, current_player)
    # player.id = current_player

    # initial the joysticks
    pygame.joystick.init()
    controllers = []
    if pygame.get_init():
        joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for jstk in joysticks:
            control = Controller(jstk)
            controllers.append(control)
            jstk.rumble(0.2, 0.5, 100)
            jstk.rumble(0.6, 0.8, 200)
            jstk.stop_rumble()
    
    # give the first player the first controller found
    if len(controllers) > 0:
        player.controller = controllers[0]

    # set the level's player to the first player  
    level.set_menu(player)

    offset_x = 0
    offset_y = 0
    scroll_area_width = 200

    run = True
    oldOffset_y = 0
    # event loop
    while run:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and player.jump_count < 3:
                    player.jump()
                if event.key == pygame.K_c and level.level_id == 0:
                    # here we change the character
                    player_sprite_id = (player_sprite_id + 1) % len(PLAYER_SPRITE_DICTIONARY)
                    old_death_count = player.death_count
                    player_controller = player.controller
                    player = Player(level.level_start_x, level.level_start_y, level.block_size_w, level.block_size_h,
                                    current_player, player_sprite_id)

                    player.death_count = old_death_count

                    if len(controllers) > 0:
                        player.controller = player_controller

                    level.set_menu(player)

                elif event.key == pygame.K_ESCAPE or event.key ==  pygame.K_q:
                    run = False
                    break
            # joyStick buttons
            if event.type == pygame.JOYBUTTONDOWN or event.type == pygame.JOYBUTTONUP:
                for ctrlr in controllers:
                    did_jump = ctrlr.DidJumpButtonPress()
                    ctrlr.DidAttackButtonPress()
                    if did_jump and player.jump_count < 3:
                        player.jump()

        # end game
        if player.did_die:
            player.did_die = False
            player.times_hit = 0
            player.rect.x = level.level_start_x
            player.rect.y = level.level_start_y
            offset_x = 0
            offset_y = 0

        if player.rect.top > (level.level_h * level.block_size_h):
            # we fell through the ground... Dead :P
            # run = False
            player.death_count -= 1
            player.rect.x = level.level_start_x
            player.rect.y = level.level_start_y
            offset_x = 0
            offset_y = 0
            print("You Fell to Your Death!", "Restarting Level")
        if player.rect.left >= level.level_end_x and player.rect.top >= (level.level_end_y) and player.rect.bottom <= (
                level.level_end_y * level.block_size_h) and player.rect.right <= (level.level_end_x * level.block_size_w):

            if level.next_level > 0 and level.next_level < len(LEVEL_DICTIONARY):
                print("Loading next level")
                window, level = load_level(level.next_level)
                old_death_count = player.death_count
                player = Player(level.level_start_x, level.level_start_y, level.block_size_w, level.block_size_h, current_player, player_sprite_id)
                player.death_count = old_death_count

                if len(controllers) > 0:
                    player.controller = controllers[0]
                level.set_menu(player)

                offset_x = 0
                offset_y = 0
                continue
            else:
                print("Game over, you win!")
                print("Loading next level")
                # window, level = load_level(0)
                # player = Player(level.level_start_x, level.level_start_y, level.block_size_w, level.block_size_h, current_player)

                # if len(controllers) > 0:
                #     player.controller = controllers[0]
                # level.set_menu(player)

                window, level, player = game_over(player, controllers, player_sprite_id)

                offset_x = 0
                offset_y = 0
        if player.death_count < 1:
            window, level, player = game_over(player, controllers, player_sprite_id)
            offset_x = 0
            offset_y = 0

        player.loop(FPS)

        for ao in level.objects:
            ao.on()
            ao.loop()

        solids = [*level.get_blocks(), *level.objects]
        handle_move(player, controllers, solids)
        window.fill((0,0,0))
        
        offset_y = player.rect.bottom - window.get_rect().centery
        offset_x = player.rect.centerx - window.get_rect().centerx

        draw(level, window, level.background, player, level.get_blocks(), level.objects, offset_x, offset_y)
        
        # print(player.rect.bottom, window.get_rect().bottom)
        # oldOffset_y = offset_y

        # offset_y = player.rect.bottom - window.get_rect().centery
        # offset_x = player.rect.centerx - window.get_rect().centerx
        # if oldOffset_y != offset_y:
        #    print('player bottom: ', player.rect.bottom, ' window bottom: ', window.get_rect().bottom, ' Old Offset_y: ', oldOffset_y, ' new offset_y ', offset_y)
        
        # if ((player.rect.right - offset_x >= WIDTH - scroll_area_width) and player.x_vel > 0) or (
        #         (player.rect.left - offset_x <= scroll_area_width) and player.x_vel < 0):
        #     offset_x += player.x_vel


    pygame.quit()
    quit()


if __name__ == "__main__":
    main(window)
