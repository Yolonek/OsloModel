import pymunk
import pygame
import numpy as np
import numba as nb
from pymunk import Vec2d
from scipy.spatial import distance


class Boid:
    def __init__(self, position: tuple[int, int], angle: float,
                 scale: int = 1, speed: int = 1):
        self.body = None
        self.shape = None
        self.saved_speed = Vec2d(0, 0)
        self.speed = speed
        self.create(position, angle, scale)

    def create(self, position: tuple[int, int], angle: float, scale: int):
        triangle_vertices = [
            (0, 2 * scale),
            (0, -2 * scale),
            (6 * scale, 0)
        ]
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = position
        self.body.angle = angle
        self.shape = pymunk.Poly(self.body, triangle_vertices)

    def change_velocity(self, vx: float, vy: float, vmax: int, vmin: int):
        self.body.angle = np.arctan2(-vx, vy) + np.pi / 2
        velocity = Vec2d(vx, vy)
        speed = abs(velocity)
        if speed >= vmax:
            self.body.velocity = velocity.normalized() * vmax
            self.speed = vmax
        elif speed < vmin:
            self.body.velocity = velocity.normalized() * vmin
            self.speed = vmin
        else:
            self.body.velocity = velocity
            self.speed = speed

    def accelerate(self):
        x_velocity, y_velocity = np.cos(self.body.angle), np.sin(self.body.angle)
        self.body.velocity = Vec2d(x_velocity, y_velocity) * self.speed

    def stop(self):
        self.speed = abs(self.body.velocity)
        self.body.velocity = Vec2d(0, 0)

    def check_boundaries(self, WIDTH: int, HEIGHT: int):
        if self.body.position[0] >= WIDTH:
            self.body.position = (0, self.body.position[1])
        elif self.body.position[0] <= 0:
            self.body.position = (WIDTH, self.body.position[1])
        if self.body.position[1] >= HEIGHT:
            self.body.position = (self.body.position[0], 0)
        elif self.body.position[1] <= 0:
            self.body.position = (self.body.position[0], HEIGHT)


class Flock:
    def __init__(self, number_of_boids: int, scale: int,
                 space: pymunk.Space,
                 space_coordinates: tuple[int, int],
                 coordinates: tuple[int, int] = None,
                 speed_range: tuple[int, int] = (1, 3),
                 speed_scale: int = 100,
                 avoid_range: int = 10,
                 avoid_factor: float = 0.05,
                 align_range: int = 50,
                 align_factor: float = 0.05,
                 cohesion_range: int = 50,
                 cohesion_factor: float = 0.05):
        self.number_of_boids = number_of_boids
        self.boids = []
        self.boid_scale = scale
        self.WIDTH = space_coordinates[0]
        self.HEIGHT = space_coordinates[1]
        self.space = space
        self.speed_active = False
        self.speed_min, self.speed_max = Vec2d(*speed_range) * speed_scale
        self.speed_scale = speed_scale
        self.avoid_range = avoid_range
        self.avoid_factor = avoid_factor
        self.align_range = align_range
        self.align_factor = align_factor
        self.cohesion_range = cohesion_range
        self.cohesion_factor = cohesion_factor
        if coordinates is not None:
            self.place_boids_from_list(coordinates)
        else:
            self.create_boids()

    def create_boids(self):
        for _ in range(self.number_of_boids):
            boid = Boid((np.random.randint(self.WIDTH),
                         np.random.randint(self.HEIGHT)),
                        np.random.random() * 2 * np.pi,
                        scale=self.boid_scale,
                        speed=self.speed_scale)
            self.space.add(boid.body, boid.shape)
            self.boids.append(boid)

    def place_boids_from_list(self, coordinates: tuple[int, int]):
        pass

    def accelerate_boids(self):
        for boid in self.boids:
            boid.accelerate()
        self.speed_active = True

    def stop_boids(self):
        for boid in self.boids:
            boid.stop()
        self.speed_active = False

    def update_boid_velocity(self,
                             check_boundaries: bool,
                             separation_active: bool,
                             alignment_active: bool,
                             cohesion_active: bool):
        for boid in self.boids:
            if check_boundaries:
                boid.check_boundaries(self.WIDTH, self.HEIGHT)
            if any([separation_active, alignment_active, cohesion_active]):
                close_dx, close_dy = 0, 0
                xvel_avg, yvel_avg, neighboring_boids_align = 0, 0, 0
                xpos_avg, ypos_avg, neighboring_boids_cohesion = 0, 0, 0
                for other in self.boids:
                    if other != boid:
                        boid_distance = distance.euclidean(boid.body.position, other.body.position)
                        if separation_active and boid_distance < self.avoid_range:
                            boid_x, boid_y = boid.body.position
                            close_dx += boid_x - other.body.position[0]
                            close_dy += boid_y - other.body.position[1]

                        if alignment_active and boid_distance < self.align_range:
                            xvel_avg += other.body.velocity[0]
                            yvel_avg += other.body.velocity[1]
                            neighboring_boids_align += 1

                        if cohesion_active and boid_distance < self.cohesion_range:
                            xpos_avg += other.body.position[0]
                            ypos_avg += other.body.position[1]
                            neighboring_boids_cohesion += 1

                separation_vx, separation_vy = 0, 0
                if separation_active:
                    separation_vx = close_dx * self.avoid_factor
                    separation_vy = close_dy * self.avoid_factor

                alignment_vx, alignment_vy = 0, 0
                if neighboring_boids_align > 0 and alignment_active:
                    alignment_vx = ((xvel_avg / neighboring_boids_align) - boid.body.velocity[0]) * self.align_factor
                    alignment_vy = ((yvel_avg / neighboring_boids_align) - boid.body.velocity[1]) * self.align_factor

                cohesion_vx, cohesion_vy = 0, 0
                if neighboring_boids_cohesion > 0 and cohesion_active:
                    cohesion_vx = ((xpos_avg / neighboring_boids_cohesion) - boid.body.position[0]) * self.cohesion_factor
                    cohesion_vy = ((ypos_avg / neighboring_boids_cohesion) - boid.body.position[1]) * self.cohesion_factor

                boid.change_velocity(
                    boid.body.velocity[0] + separation_vx + alignment_vx + cohesion_vx,
                    boid.body.velocity[1] + separation_vy + alignment_vy + cohesion_vy,
                    self.speed_max, self.speed_min
                )


if __name__ == '__main__':
    pass
