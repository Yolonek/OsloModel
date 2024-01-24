import sys
import pygame
import pymunk
import pymunk.pygame_util
from pymunk import Vec2d
import math
import numpy as np


def create_triangle(position, angle, scale=1):
    triangle_vertices = [(-2 * scale, 0), (0, 6 * scale), (2 * scale, 0)]
    triangle_body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
    triangle_body.position = position
    triangle_body.velocity = (0, 0)
    triangle_body.angle = angle
    triangle_shape = pymunk.Poly(triangle_body, triangle_vertices)
    return triangle_body, triangle_shape


def accelerate_body(body: pymunk.Body, scale: int) -> None:
    angle = body.angle + np.pi / 2
    x_velocity, y_velocity = math.cos(angle), math.sin(angle)
    body.velocity = Vec2d(x_velocity, y_velocity).normalized() * scale


def stop_body(body: pymunk.Body) -> None:
    body.velocity = Vec2d(0, 0)


def main():
    running = True
    pygame.init()

    # WIDTH, HEIGHT = 800, 800
    WIDTH, HEIGHT = 1920, 1080
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    velocity_scale = 200

    space = pymunk.Space()

    number_of_bodies = 500
    triangles = []
    for _ in range(number_of_bodies):
        triangle, shape = create_triangle(((np.random.randint(WIDTH)), np.random.randint(HEIGHT)),
                                          np.random.random() * 2 * np.pi)
        space.add(triangle, shape)
        triangles.append(triangle)

    draw_options = pymunk.pygame_util.DrawOptions(window)
    # vx, vy = (400, 400)
    # vx, vy = (0, 0)
    # tol = 50
    speed_active = False
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if speed_active:
                    for body in triangles:
                        stop_body(body)
                        speed_active = False
                else:
                    for body in triangles:
                        accelerate_body(body, velocity_scale)
                        speed_active = True
        for body in triangles:
            if body.position[0] >= WIDTH:
                body.position = (0, body.position[1])
            elif body.position[0] <= 0:
                body.position = (WIDTH, body.position[1])
            if body.position[1] >= HEIGHT:
                body.position = (body.position[0], 0)
            elif body.position[1] <= 0:
                body.position = (body.position[0], HEIGHT)

        window.fill((11, 11, 11))
        space.debug_draw(draw_options)
        pygame.display.update()
        space.step(dt)
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    sys.exit(main())
