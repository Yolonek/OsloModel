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

    WIDTH, HEIGHT = 800, 800
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fps = 60
    dt = 1 / fps

    velocity_scale = 200

    space = pymunk.Space()

    triangle_body, triangle_shape = create_triangle((300, 300), 0, scale=10)
    space.add(triangle_body, triangle_shape)

    speed_active = False
    draw_options = pymunk.pygame_util.DrawOptions(window)
    vx, vy = (400, 400)
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if speed_active:
                    stop_body(triangle_body)
                    speed_active = False
                else:
                    accelerate_body(triangle_body, velocity_scale)
                    speed_active = True
            elif event.type == pygame.MOUSEMOTION:
                vx, vy = pymunk.pygame_util.get_mouse_pos(window)
                difference = Vec2d(vx, vy) - triangle_body.position
                triangle_body.velocity = difference.normalized() * velocity_scale
                triangle_body.angle = math.atan2(-difference[0], difference[1])
        if triangle_body.position[0] >= WIDTH:
            triangle_body.position = (0, triangle_body.position[1])
        elif triangle_body.position[0] <= 0:
            triangle_body.position = (WIDTH, triangle_body.position[1])
        if triangle_body.position[1] >= HEIGHT:
            triangle_body.position = (triangle_body.position[0], 0)
        elif triangle_body.position[1] <= 0:
            triangle_body.position = (triangle_body.position[0], HEIGHT)


        window.fill((11, 11, 11))
        space.debug_draw(draw_options)
        pygame.display.update()
        space.step(dt)
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    sys.exit(main())
