import pygame
import random

from pygame.locals import *
from pygame import mixer

# Configure and start mixer
pygame.mixer.pre_init(44100, -16, 2, 512)
mixer.init()

# Start pygame
pygame.init()

# Screen configuration
screen_width = 864
screen_height = 936
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("PetPiu")

# Framerate configuration
clock = pygame.time.Clock()
fps = 60

# Font and color configuration
font = pygame.font.SysFont("Arial", 60)
white_color = (255, 255, 255)

# Game variables
ground_height = 768
ground_scroll = 0
scroll_speed = 4
flying = False
air_hit = False  # Bird hit the pipe or the top
game_over = False
wait_start = True  # Wait for the player to start the game
pipe_gap = 175  # Gap between top and bottom pipe
pipe_frequency = 1500  # In milliseconds
last_pipe = pygame.time.get_ticks() - pipe_frequency
score = 0
pass_pipe = False

# Load background and restart button image
background_image = pygame.image.load("../assets/image/background.png")
ground_image = pygame.image.load("../assets/image/ground.png")
restart_image = pygame.image.load("../assets/image/restart.png")

# Load sounds
wing_fx = pygame.mixer.Sound("../assets/music/wing.wav")
point_fx = pygame.mixer.Sound("../assets/music/point.wav")
hit_fx = pygame.mixer.Sound("../assets/music/hit.wav")
fall_fx = pygame.mixer.Sound("../assets/music/fall.wav")

# Bird class
class Bird(pygame.sprite.Sprite):
    def __init__(self, x, y):
        pygame.sprite.Sprite.__init__(self)
        self.images = []
        self.index = 0
        self.counter = 0

        for num in range(1, 4):
            img = pygame.image.load(f"../assets/image/bird{num}.png")
            self.images.append(img)

        self.image = self.images[self.index]
        self.rect = self.image.get_rect()
        self.rect.center = [x, y]
        self.vel = 0
        self.space_pressed = False

    def update(self):
        # Gravity
        if flying == True:
            self.vel += 0.5

            if self.vel > 8:
                self.vel = 8

            if self.rect.bottom < ground_height:
                self.rect.y += int(self.vel)

        if game_over == False:
            # Jump
            key = pygame.key.get_pressed()  # Get the pressed key

            if key[pygame.K_SPACE] and self.space_pressed == False:
                wing_fx.play()
                self.space_pressed = True
                self.vel = -10
            
            if key[pygame.K_SPACE] == False:
                self.space_pressed = False

            # Handle the animation
            self.counter += 1
            flap_cooldown = 5

            if self.counter > flap_cooldown:
                self.counter = 0
                self.index += 1

                if self.index >= len(self.images):
                    self.index = 0

            self.image = self.images[self.index]
            self.image = pygame.transform.rotate(self.images[self.index], self.vel*(-2))  # Rotate the bird

            if wait_start == True:
                self.image = pygame.transform.rotate(self.images[2], 0)  # Reset bird rotation when starting a new game
        else:
            self.image = pygame.transform.rotate(self.images[2], -90)  # Rotate the bird when there is a collision

# Pipe class
class Pipe(pygame.sprite.Sprite):
    def __init__(self, x, y, position):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load("../assets/image/pipe.png")
        self.rect = self.image.get_rect()

        # Position 1 is from the top
        if position == 1:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect.bottomleft = [x, y - pipe_gap//2]

        # Position -1 is from the bottom
        if position == -1:
            self.rect.topleft = [x, y + pipe_gap//2]

    def update(self):
        self.rect.x -= scroll_speed

        # Check if the pipe is outside the screen and delete
        if self.rect.right < 0:
            self.kill()

# Button Class
class Button():
    def __init__(self, x, y, image):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)

    def draw(self):
        action = False
        key = pygame.key.get_pressed()  # Get the pressed key
        screen.blit(self.image, (self.rect.x, self.rect.y))  # Draw button

        # Check if the space bar was pressed
        if key[pygame.K_SPACE]:
            action = True

        return action

# Draw text function
def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    screen.blit(img, (x, y))

# Restart game function
def restart_game():
    pipe_group.empty()
    petpiu.rect.x = 100
    petpiu.rect.y = screen_height//2
    score = 0

    return score

# Manage instances and sprites
bird_group = pygame.sprite.Group()
pipe_group = pygame.sprite.Group()

petpiu = Bird(100, screen_height//2)
bird_group.add(petpiu)

button = Button(screen_width//2 - 50, screen_height//2 - 100, restart_image)

# Main loop
run = True

while run:
    clock.tick(fps)  # Update the clock

    screen.blit(background_image, (0, 0))  # Draw background

    pipe_group.draw(screen)  # Draw pipe

    bird_group.draw(screen)  # Draw bird
    bird_group.update()  # Update bird

    screen.blit(ground_image, (ground_scroll, ground_height))  # Draw ground

    # Check the score
    if len(pipe_group) > 0:
        if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.left \
                                and bird_group.sprites()[0].rect.right < pipe_group.sprites()[0].rect.right \
                                and pass_pipe == False:
            pass_pipe = True

        if pass_pipe == True:
            if bird_group.sprites()[0].rect.left > pipe_group.sprites()[0].rect.right:
                point_fx.play()
                score += 1
                pass_pipe = False

    draw_text(str(score), font, white_color, screen_width//2, 20)  # Draw the score

    # Look for collision
    if pygame.sprite.groupcollide(bird_group, pipe_group, False, False):
        if game_over == False:
            hit_fx.play()
            fall_fx.play()
            air_hit = True

        game_over = True

    # Check if bird has hit the top
    if petpiu.rect.top < 0:
        if game_over == False:
            hit_fx.play()
            fall_fx.play()
            air_hit = True

        game_over = True

    # Check if bird has hit the ground
    if petpiu.rect.bottom >= ground_height:
        if game_over == False or air_hit == True:
            hit_fx.play()

        air_hit = False
        game_over = True
        wait_start = True
        flying = False

    if game_over == False and flying == True:
        # Generate new pipes
        time_now = pygame.time.get_ticks()

        if (time_now-last_pipe) > pipe_frequency:
            pipe_height = random.randint(-100, 100)
            bottom_pipe = Pipe(screen_width, screen_height//2 + pipe_height, -1)
            top_pipe = Pipe(screen_width, screen_height//2 + pipe_height, 1)
            pipe_group.add(bottom_pipe)
            pipe_group.add(top_pipe)
            last_pipe = time_now

        # Scroll the ground
        ground_scroll -= scroll_speed

        # Check if the ground is outside the screen and reset
        if abs(ground_scroll) > 35:
            ground_scroll = 0

        pipe_group.update()  # Update pipes

    # Check for game over and restart
    if game_over == True:
        if button.draw() == True:
            game_over = False
            score = restart_game()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Check if the game has closed
            run = False
        if event.type == pygame.KEYDOWN:  # Start the game
            if event.key == pygame.K_SPACE and flying == False and game_over == False:
                flying = True
                wait_start = False

    pygame.display.flip()  # Update the screen

# Exit pygame
pygame.quit()

