import sys
import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math


def create_triangle():
    # pointer_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    triangle_vertices = [(0, 8), (0, -8), (24, 0)]
    triangle_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    # triangle_body.mass = 1
    triangle_body.position = (400, 400)
    # triangle_body.velocity = (20, 20)
    triangle_shape = pymunk.Poly(triangle_body, triangle_vertices)
    return triangle_body, triangle_shape


def update_rotation_and_velocity(body, velocity):
    pass


def main():
    running = True
    pygame.init()

    WIDTH, HEIGHT = 800, 800
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    velocity_scale = 100

    space = pymunk.Space()

    triangle_body, triangle_shape = create_triangle()
    space.add(triangle_body, triangle_shape)

    draw_options = pymunk.pygame_util.DrawOptions(window)
    vx, vy = (400, 400)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEMOTION:
                vx, vy = pymunk.pygame_util.get_mouse_pos(window)
        difference = Vec2d(vx, vy) - triangle_body.position
        if -1 < difference[0] < 1 and -1 < difference[1] < 1:
            triangle_body.velocity = (0, 0)
        else:
            triangle_body.velocity = difference.normalized() * velocity_scale
            triangle_body.angle = math.atan2(-difference[0], difference[1])


        window.fill((11, 11, 11))
        space.debug_draw(draw_options)
        pygame.display.update()
        space.step(dt)
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    sys.exit(main())
