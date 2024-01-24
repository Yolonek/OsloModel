import sys
import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math
import numpy as np


def create_triangle(position, angle, scale=1):
    triangle_vertices = [(2 * scale, 0), (-2 * scale, 0), (0, 6 * scale)]
    triangle_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    triangle_body.position = position
    triangle_body.velocity = (0, 0)
    # triangle_body.mass = 1
    triangle_body.angle = angle
    triangle_shape = pymunk.Poly(triangle_body, triangle_vertices)
    return triangle_body, triangle_shape


def update_rotation_and_velocity(body, velocity):
    pass


def main():
    running = True
    pygame.init()

    # WIDTH, HEIGHT = 800, 800
    WIDTH, HEIGHT = 1920, 1080
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    velocity_scale = 100

    space = pymunk.Space()

    number_of_bodies = 100
    # triangles = (create_triangle(((np.random.randint(WIDTH)), np.random.randint(HEIGHT)), np.random.random() * 2 * np.pi) for _ in range(number_of_bodies))
    # triangle_body, triangle_shape = create_triangle()
    # for triangle, shape in triangles:
    #     space.add(triangle, shape)
    triangles = []
    for _ in range(number_of_bodies):
        triangle, shape = create_triangle(((np.random.randint(WIDTH)), np.random.randint(HEIGHT)),
                                          np.random.random() * 2 * np.pi)
        space.add(triangle, shape)
        triangles.append(triangle)

    draw_options = pymunk.pygame_util.DrawOptions(window)
    # vx, vy = (400, 400)
    vx, vy = (0, 0)
    tol = 50
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False

            elif event.type == pygame.MOUSEMOTION:
                vx, vy = pymunk.pygame_util.get_mouse_pos(window)
        if (vx, vy) != (0, 0):
            for triangle_body in triangles:
                difference = Vec2d(vx, vy) - triangle_body.position
                if -tol < difference[0] < tol and -tol < difference[1] < tol:
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
