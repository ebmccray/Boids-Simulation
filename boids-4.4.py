# GAME INFORMATION
title = 'Boids'
version = '4.3'
creator = 'Erienne McCray'
copyright = '2021'

# IMPORT MODULES:
from os import sep
import pygame
import random
import traceback
import numpy as np
from pygame import Rect, sprite
from pygame.constants import MOUSEMOTION

from pygame.math import Vector2


with open('traceback boid2s .txt', 'w+') as f:

    try:
        # CONSTANTS:
        # Window and Game Variables:
        WIDTH = 1920
        HEIGHT = 1080
        FPS = 30

        # COLORS:
        BLACK = (0, 0, 0)
        WHITE = (255, 255, 255)
        RED = (255, 0, 0)
        GREEN = (0, 255, 0)
        BLUE = (0, 0, 255)
        CYAN = (0, 255, 255)
        GRAY = (100, 100, 100)

        # ADDITIONAL VARIABLES
        # Boid appearance:
        size = 10
        narrowness = min(5, size)
        color_array = [GREEN, BLUE, CYAN]

        # Boid movement:
        population = 50 # Max is about 125 with my machine
        targeted_boids = min(4, 0)
        detection_radius = 75
        division_factor1 = 1000
        division_factor2 = 32
        division_factor3 = 5000
        separation = 20
        outer_buffer = -100
        inner_buffer = -50
        avoid_speed = 0.6

        same_color_flocks = True

        # GROUPS AND ARRAYS
        all_sprites = pygame.sprite.Group()
        all_boids = pygame.sprite.Group()
        all_collisions = pygame.sprite.Group()

        # CLASSES
        class Boid(pygame.sprite.Sprite):
            def __init__(self, coord, color):
                super().__init__()

                self.size = size
                self.color = color
                self.no_hit = True

                # Calculate points of the triangle
                self.points = ((0, (size/narrowness)), (0, size-(size/narrowness)), (size, size/2))

                # Draw image and get the rect at the coordinate
                self.image = pygame.Surface((self.size, self.size))
                self.image.fill(WHITE)
                self.image.set_colorkey(WHITE)
                pygame.draw.polygon(self.image, self.color, self.points)
                self.rect = self.image.get_rect(center = coord)

                # Rotation information
                self.orig_image = self.image.copy()
                self.angle = 0
                self.direction = pygame.Vector2(1,0)

                # Detection information
                self.radius = detection_radius

                # Movement information
                self.velocity = pygame.Vector2(0,0)
                self.new_pos = pygame.Vector2(self.rect.center)
            
            def update(self):
                self.vector1 = pygame.Vector2(0,0)

                self.collisions = self.detect_local()

                self.mass_center(self.collisions)

                self.avoid_boids(self.collisions)

                self.avoid_obstacles()

                self.match_velocity(self.collisions)

                self.avoid_edge()

                self.velocity += self.vector1 + self.vector2 + self.vector3 + self.vector4

                self.collide()

               # Rotate towards the point we're aiming at
                point = pygame.Vector2(self.rect.center) + self.velocity
                self.rotate(point)

                self.rect.center = self.new_pos


            def rotate(self, point): # Rotate the boid to face the direction of movement
                # Get the angle from the point to the center of the boid
                my_center = pygame.Vector2(self.rect.center)
                new_angle = pygame.math.Vector2(point-my_center).angle_to((1,0))

                # Rotate the stored image to point in that directon
                self.direction = pygame.math.Vector2(1,0).rotate(new_angle)
                self.image = pygame.transform.rotate(self.orig_image, new_angle)
                self.rect = self.image.get_rect(center = my_center)

                # Store the new angle
                self.angle = new_angle

            def detect_local(self): # Find all other sprite objects within the detection radius.
                collisions = pygame.sprite.spritecollide(self, all_sprites, False, pygame.sprite.collide_circle)
                return collisions

            def mass_center(self, collisions): # Detect the center of mass of local boids.
                self.vector1 = pygame.Vector2(0,0)
                local_boids = []

                for boid in collisions:
                    if boid in all_boids:
                        if same_color_flocks:
                            if self.color == boid.color:
                                local_boids.append(pygame.Vector2(boid.rect.center))
                        else:
                            local_boids.append(pygame.Vector2(boid.rect.center))
                
                mass_mean = np.mean(local_boids, axis=0)

                mass_mean = pygame.Vector2(mass_mean[0], mass_mean[1])

                # Create a vector that moves the boid closer to the center of mass
                self.vector1 = (mass_mean-pygame.Vector2(self.rect.center))/division_factor1

            def avoid_boids(self,collisions): # Move the boid slightly away from other boids that are too close.
                self.vector2 = pygame.Vector2(0,0)
                self.vector2_x = 0
                self.vector2_y = 0
                for obstacle in collisions:
                    if obstacle in all_boids:
                            if abs(self.rect.centerx-obstacle.rect.centerx) <= separation:
                                self.vector2_x += (self.rect.centerx-obstacle.rect.centerx)/division_factor2
                            if abs(self.rect.centery-obstacle.rect.centery) <= separation:
                                self.vector2_y += (self.rect.centery-obstacle.rect.centery)/division_factor2

                # Create a vector that moves the boid away from local boids.
                self.vector2 = pygame.Vector2(self.vector2_x, self.vector2_y)

            def avoid_obstacles(self):
                collisions = pygame.sprite.spritecollide(self, all_sprites, False)
                for obstacle in collisions:
                    if not obstacle.no_hit:
                        if self.rect.centerx >= obstacle.rect.left+(separation*2) and self.rect.centerx <= obstacle.rect.right+separation:
                            self.vector2_x *= 0.25
                            self.vector2_x += (self.rect.centerx-obstacle.rect.left)/division_factor2
                            #self.vector2_x = -self.vector2_x
                        elif self.rect.centerx <= obstacle.rect.right+(separation*2) and self.rect.centerx >= obstacle.rect.left-separation:
                            self.vector2_x *= 0.25
                            self.vector2_x += (self.rect.centerx-obstacle.rect.right)/division_factor2
                            #self.vector2_x *= -1
                        if self.rect.centery >= obstacle.rect.top+(separation*2) and self.rect.centery <= obstacle.rect.bottom+separation:
                            self.vector2_y *= 0.25
                            self.vector2_y += (self.rect.centery-obstacle.rect.top)/division_factor2
                            #self.vector2_y *= -1
                        elif self.rect.centery <= obstacle.rect.bottom+(separation*2) and self.rect.centery >= obstacle.rect.top-separation:
                            self.vector2_y *= 0.25
                            self.vector2_y += (self.rect.centery-obstacle.rect.bottom)/division_factor2
                            #self.vector2_y *= -1

                self.vector2 = pygame.Vector2(self.vector2_x, self.vector2_y)

            def match_velocity(self, collisions): # Find the average velocity of all local boids and make own velocity more like them.
                self.vector3 = pygame.Vector2(0,0)
                local_velocities = []
                for boid in collisions:
                    if boid in all_boids:
                        if same_color_flocks:
                            if self.color == boid.color:
                                local_velocities.append(boid.velocity)
                        else:
                            local_velocities.append(boid.velocity)

                velocities_mean = np.mean(local_velocities, axis=0)
                velocities_mean = pygame.Vector2(velocities_mean[0], velocities_mean[1])

                # Create vector which adjusts the current velocity slightly toward the targeted velocity.
                self.vector3 = (velocities_mean-self.velocity)/division_factor2

            def avoid_edge(self): # Turns the boid around and back towards the center of the screen when it hits a certain cutoff.
                self.vector4 = pygame.Vector2(0,0)
                vector4_x = 0
                vector4_y = 0
                if self.rect.centerx <= separation:
                    vector4_x += (self.rect.centerx-separation)/division_factor1
                
                if self.rect.centery >= WIDTH - separation:
                    vector4_x += (self.rect.centerx-(WIDTH-separation))/division_factor1

                if self.rect.centery <= separation:
                    vector4_y -= (self.rect.centery-separation)/division_factor1
                
                if self.rect.centery >= HEIGHT + separation :
                    vector4_y -= (self.rect.centery-(HEIGHT-separation))/division_factor1

                self.vector4 = pygame.Vector2(vector4_x, vector4_y)

                if self.rect.centerx <= outer_buffer:
                    self.rect.centerx = inner_buffer
                    self.velocity[0] = (self.velocity[0])*-0.5
                if self.rect.centerx >= WIDTH  -outer_buffer:
                    self.rect.centerx = WIDTH -inner_buffer
                    self.velocity[0] = (self.velocity[0])*-0.5
                if self.rect.centery <= outer_buffer:
                    self.rect.centery = inner_buffer
                    self.velocity[1] = (self.velocity[1])*-0.5
                if self.rect.centery >= HEIGHT -outer_buffer:
                    self.rect.centery = HEIGHT -inner_buffer
                    self.velocity[1] = (self.velocity[1])*-0.5

            def collide(self): # Prevent boids from entering the space of obstacles and other boids.
                orig_pos = pygame.Vector2(self.rect.center)
                new_pos = orig_pos + self.velocity
                new_rect = self.rect.copy()
                new_rect.center = new_pos
                self.new_pos = new_pos
                for item in all_collisions:
                    if item != self:
                        collide = new_rect.colliderect(item.rect)
                        if collide:
                            self.new_pos = orig_pos
                            x = self.velocity[0]
                            y = self.velocity[1]
                            if self.rect.centerx-item.rect.centerx != 0:
                                factor_x = abs(self.rect.centerx-item.rect.centerx)/(self.rect.centerx-item.rect.centerx)
                            else:
                                factor_x = 0
                            if self.rect.centery-item.rect.centery != 0:
                                factor_y = abs(self.rect.centery-item.rect.centery)/(self.rect.centery-item.rect.centery)
                            else:
                                factor_y = 0
                            '''x += avoid_speed*factor_x
                            y += avoid_speed*factor_y
                            self.velocity = pygame.Vector2(x, y)'''
                        else:
                            self.new_pos = new_pos

        class TargetedBoid(Boid): # Boids that are continually aiming for a specific target. (See class Boid)
            def __init__(self, coord, color, target):
                super().__init__(coord, color)
                self.target = target
            
            def update(self):
                self.collisions = []
                for boid in all_boids:
                    self.collisions.append(boid)
                
                self.mass_center(self.collisions)

                self.avoid_boids(self.collisions)

                self.match_velocity(self.collisions)

                self.velocity += self.find_target(self.target)

                return super().update()

            def mass_center(self, collisions):
                self.vector1 = pygame.Vector2(0,0)
                local_boids = []

                for boid in collisions:
                    if boid in all_boids:
                        if same_color_flocks:
                            if self.color == boid.color:
                                local_boids.append(pygame.Vector2(boid.rect.center))
                        else:
                            local_boids.append(pygame.Vector2(boid.rect.center))
                
                mass_mean = np.mean(local_boids, axis=0)

                mass_mean = pygame.Vector2(mass_mean[0], mass_mean[1])

                self.vector1 = (mass_mean-pygame.Vector2(self.rect.center))/division_factor2

            def match_velocity(self, collisions):
                self.vector3 = pygame.Vector2(0,0)
            
            def find_target(self, target):
                vector5 = pygame.Vector2(0,0)
                boid_collisions = pygame.sprite.spritecollide(self, all_boids, False, pygame.sprite.collide_circle)
                if boid_collisions:
                    vector5 = (target-pygame.Vector2(self.rect.center))/division_factor3
                else:
                    print(boid_collisions)
                return vector5

        class Obstacle(pygame.sprite.Sprite): # User-created obstacles.
            def __init__(self, coord, width, height):
                super().__init__()

                self.no_hit = False

                self.image = pygame.Surface((width, height))
                self.image.fill(WHITE)
                self.rect = self.image.get_rect(topleft = coord)

        class TempObstacle(pygame.sprite.Sprite): # Preview image of user-created obstacle.
            def __init__(self, coord):
                super().__init__()

                self.image = pygame.Surface((1, 1))
                self.image.fill(GRAY)
                self.rect = self.image.get_rect(topleft = coord)
                self.orig_x = self.rect.x
                self.orig_y = self.rect.y
                self.no_hit = True

            
            def update(self): # Get the position of the mouse and adjust the size to fit with the current mouse.
                mouse_pos = pygame.mouse.get_pos()
                mouse_x = mouse_pos[0]
                mouse_y = mouse_pos[1]
                new_x = self.orig_x
                new_y = self.orig_y
                if drawing:
                    self.image = pygame.Surface((abs(self.orig_x-mouse_x), abs(self.orig_y-mouse_y)))
                    self.image.fill(GRAY)
                    if self.orig_x > mouse_x:
                        new_x = mouse_x
                    if self.orig_y > mouse_y:
                        new_y = mouse_y
                    self.rect = self.image.get_rect(topleft = (new_x, new_y))
                else: # When we stop drawing, create the wall.
                    block = Obstacle(self.rect.topleft, self.rect.width, self.rect.height)
                    all_sprites.add(block)
                    all_collisions.add(block)
                    self.kill()
                


        # FUNCTIONS
        # General Game Functions:
        def DrawGame():
            window.fill((BLACK))
            all_sprites.draw(window)
            pygame.display.update()

        def InitPositions(): # Reset simulation and randomize positions and colors of all boids on screen
            all_sprites.empty()
            all_boids.empty()
            all_collisions.empty()

            i = 0
            while i <= population:
                coord = pygame.Vector2(random.randint(0, WIDTH-size), random.randint(0, HEIGHT-size))
                color = random.choice(color_array)
                boid = Boid(coord, color)
                all_sprites.add(boid)
                all_boids.add(boid)
                all_collisions.add(boid)
                i += 1

            i = 0
            while i < targeted_boids:
                coord = pygame.Vector2(random.randint(0, WIDTH-size), random.randint(0, HEIGHT-size))
                if i == 0:
                    target = pygame.Vector2(0,HEIGHT/2)
                if i == 1:
                    target = pygame.Vector2(WIDTH,HEIGHT/2)
                if i == 2:
                    target = pygame.Vector2(WIDTH/2,0)
                if i == 3:
                    target = pygame.Vector2(WIDTH/2,HEIGHT)
                boid = TargetedBoid(coord, RED, target)
                all_sprites.add(boid)
                all_boids.add(boid)
                i += 1

        def CreateTemp(coord): # Create a "temporary obstacle" preview obect.
            block = TempObstacle(coord)
            all_sprites.add(block)

        # INITIALIZATION
        pygame.init()

        # Create window and define cclock
        window = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption(title + "-" + version)
        clock = pygame.time.Clock()

        # SIM LOOP
        running = True
        paused = False
        drawing = False

        # Set-up before game runs
        InitPositions()

        # While Game is running:
        while running:
            # Set FPS
            clock.tick(FPS)

            # Check for user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if not drawing:
                        CreateTemp(pygame.mouse.get_pos())
                    drawing = not drawing
                elif event.type == pygame.KEYDOWN:
                    key = event.key
                    if key == pygame.K_RETURN:
                        InitPositions()
                    elif key == pygame.K_SPACE:
                        paused = not paused
                    elif key == pygame.K_ESCAPE:
                        running = False

            # While not paused, run simulation
            if not paused:
                all_sprites.update()

        
            DrawGame()

        pygame.QUIT

    except:
        traceback.print_exc(file=f)