import pygame
import os
import time

# map
_map = """
00000000000000
00111100000011
10000001110000
11111111110000
11111111100011
11111111111111
"""

# global 
ids = 0

# load images into game
BASE_SIZE = [80,80]
IMAGES = {}

# entities and blocks list
entities = {}
blocks = []
block_hitbox = []

# linear interpolation
# clamping
def clamp(value: float, low: float, high: float):
    if value > high:
        return high
    elif value < low:
        return low
    return value

def lerp(start: float, to: float, percent: float) -> float:
    return (start + percent * (to - start))

def normalize(vec2: list) -> list:
    mag = math.sqrt(vec2[0] ** 2 + vec2[1] ** 2)
    return [vec2[0] / mag, vec2[1] / mag]

# create youtube icon player thing
def create_id():
    global ids
    ids += 1
    return ids

# blocks should be the block_hitbox list
def collision_check(entity, blocks):
    # create a temporary list
    collisions = []
    # loop through each block and check if the entity collided with it
    for hitbox in blocks:
        if entity.rect.colliderect(hitbox):
            collisions.append(hitbox)
    return collisions

# reaction
def react_to_collisions(entity) -> dict:
    global block_hitbox

    # dict for collision sides
    collided = {"top":False,"bottom":False,"left":False,"right":False}

    movement = entity.motion

    # move x
    entity.rect.x += movement[0]
    collisions = collision_check(entity, block_hitbox)
    # loop through collisions
    for collision in collisions:
        # check if collided
        if round(movement[0]) > 0:
            entity.rect.right = collision.left
            collided["right"] = True
            entity.motion[0] = 0
        elif round(movement[0]) < 0:
            entity.rect.left = collision.right
            collided["left"] = True
            entity.motion[0] = 0

    # move y
    entity.rect.y += movement[1]
    collisions = collision_check(entity, block_hitbox)
    # loop through collisions again
    for collision in collisions:
        # check if collided
        if round(movement[1]) > 0:
            entity.rect.bottom = collision.top
            collided["bottom"] = True
            entity.motion[1] = 0
        elif round(movement[1]) < 0:
            entity.rect.top = collision.bottom
            collided["top"] = True
            entity.motion[1] = 0
    
    return collided

# entity class
class Entity:
    def __init__(self, image:str, x:int, y:int, width:int, height:int):
        self.image_str = image
        self.image = IMAGES[image]

        # collision detection
        self.rect = pygame.Rect(x, y, width, height)

        # movement variables
        self.current_movement = [0,0]
        self.motion = [0,0]
        self.collided = {"top":False,"bottom":False,"right":False,"left":False}
    
    def update(self, dt: float):
        pass

    def move_and_slide(self):
        # add current movement to the motion
        self.motion[0] += self.current_movement[0]
        self.motion[1] += self.current_movement[1]

        # this handles movement and collision
        self.collided = react_to_collisions(self)

        # reset current movement
        self.current_movement[0] = 0
        self.current_movement[1] = 0

# function for creating entities
def create_entity(image: str, x: int, y: int, obj_type = Entity):
    entities[create_id()] = obj_type(image, x, y, BASE_SIZE[0], BASE_SIZE[1])

def create_block(image: str, x: int, y: int):
    blocks.append([image, x, y, BASE_SIZE[0], BASE_SIZE[1]])
    block_hitbox.append(pygame.Rect(x, y, BASE_SIZE[0], BASE_SIZE[1]))


# objects
class Player(Entity):
    def __init__(self, image: str, x: int, y: int, width: int, height: int):
        super().__init__(image, x, y, width, height)
        # stats
        self.movespeed = 100
        self.move_resistance = 0.1
        self.on_ground_resistance = 0.2
        self.resistance = 0

        self.gravity = 150
        self.jump_speed = 50

        self.jumping = True
        self.on_ground = False

    def update(self, dt: float):
        keys = pygame.key.get_pressed()

        if not self.collided["bottom"]:
            # add gravity
            self.current_movement[1] += self.gravity * dt
            self.resistance = self.move_resistance
        else:
            self.jumping = False
            self.resistance = self.on_ground_resistance
        # movement
        # must add movement stuff to the self.current_movement
        if keys[pygame.K_d]:
            self.current_movement[0] += self.movespeed * dt
        if keys[pygame.K_a]:
            self.current_movement[0] -= self.movespeed * dt
        if keys[pygame.K_w]:
            self.current_movement[1] -= self.movespeed * dt
        if keys[pygame.K_s]:
            self.current_movement[1] += self.movespeed * dt
        if keys[pygame.K_SPACE] and not self.jumping:
            self.current_movement[1] -= self.jump_speed
            self.jumping = True

        self.move_and_slide()

        # lerp
        self.motion[0] = lerp(self.motion[0], 0.0, self.resistance)
        self.motion[1] = lerp(self.motion[1], 0.0, self.resistance)

def main():
    
    # window variables
    size = [1280, 720]

    # create your game window
    window = pygame.display.set_mode(size)

    # create a clock
    clock = pygame.time.Clock()

    # set fps for game
    FPS = 120

    path = "assets"
    for file in os.listdir(path):
        # loop through - and load images into the transformed size
        IMAGES[file] = pygame.transform.scale(pygame.image.load(f"{path}/{file}").convert_alpha(), BASE_SIZE)

    # an object is like this
    # [image, x, y, width, height]
    # create first entity
    create_entity("youtube.png", 100, 100, obj_type=Player)

    # create map
    lines = _map.split("\n")
    for y in range(len(lines)):
        # y would be a string of numbers
        for x in range(len(lines[y])):
            value = int(lines[y][x])
            if value == 0:
                continue
            elif value == 1:
                create_block("ground.png", x * BASE_SIZE[0], y * BASE_SIZE[1])


    # control variable
    running = True

    # delta time
    starttime = time.time()
    endtime = 0
    dt = 0

    # game loop
    while running:
        # clear screen
        window.fill([50,150,255])

        # update entities
        [entity.update(dt) for id, entity in entities.items()]

        # render entities
        # for id, entity in entities.items():
        #   window.blit(entity.image, entity.rect)
        window.blits([[entity.image, [int(entity.rect.x), int(entity.rect.y)]] for id, entity in entities.items()])

        # render blocks
        window.blits([[IMAGES[b[0]], [b[1],b[2]]] for b in blocks])

        # updates the whole screen - regardless if changes were made
        # generally for 3D games
        # pygame.display.flip()

        # only updates parts of the screen that have been changed
        pygame.display.update()

        # use clock to limit framerate
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
        
        # time updates
        endtime = time.time()
        dt = endtime - starttime
        starttime = endtime
    
    pygame.quit()

if __name__ == "__main__":
    main()