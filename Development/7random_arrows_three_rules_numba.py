import sys
import pygame
import pymunk
import pymunk.pygame_util
from Flock import Flock


def main():
    running = True
    pygame.init()
    WIDTH, HEIGHT = 1920, 1080
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fps = 30
    dt = 1 / fps

    velocity_scale = 200
    body_scale = 4

    space = pymunk.Space()

    number_of_bodies = 100
    flock = Flock(number_of_bodies, space,
                  boid_size=body_scale,
                  space_coordinates=(WIDTH, HEIGHT),
                  speed_scale=velocity_scale,
                  avoid_range=30,
                  avoid_factor=0.5,
                  align_range=100,
                  align_factor=0.005,
                  cohesion_range=200,
                  cohesion_factor=0.5,
                  turn_margin=200,
                  turn_factor=20)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if flock.speed_active:
                    flock.stop_boids()
                else:
                    flock.accelerate_boids()
        if flock.speed_active:
            flock.update_boid_velocity(
                check_boundaries=True,
                horizontal_cyclic_boundary=True,
                vertical_cyclic_boundary=False,
                separation_active=False,
                alignment_active=True,
                cohesion_active=False,
                vertical_wall_active=True,
                horizontal_wall_active=False
            )

        window.fill((11, 11, 11))
        space.debug_draw(draw_options)
        pygame.display.update()
        space.step(dt)
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    sys.exit(main())
