import pymunk
import pygame
import numpy as np
import numba as nb
from pymunk import Vec2d
from scipy.spatial import distance
from UserInterface import BoidFlockingParameters


class Boid:
    def __init__(self, position: tuple[int, int], angle: float,
                 scale: float = 1, speed: int = 1):
        self.body = None
        self.shape = None
        self.saved_speed = Vec2d(0, 0)
        self.speed = speed
        self.create(position, angle, scale)

    def create(self, position: tuple[int, int], angle: float, scale: float):
        triangle_vertices = [
            (0, 1 * scale),
            (0, -1 * scale),
            (3 * scale, 0)
        ]
        self.body = pymunk.Body(body_type=pymunk.Body.KINEMATIC)
        self.body.position = position
        self.body.angle = angle
        self.shape = pymunk.Poly(self.body, triangle_vertices)

    def change_boid(self, position: tuple[int, int], angle: float, speed_active: bool):
        self.body.position = position
        self.body.angle = angle
        if speed_active:
            self.accelerate()

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

    def check_boundaries(self, WIDTH: int, HEIGHT: int,
                         cyclic_horizontal: bool = True, cyclic_vertical: bool = True):
        if cyclic_horizontal:
            if self.body.position[0] >= WIDTH:
                self.body.position = (0, self.body.position[1])
            elif self.body.position[0] <= 0:
                self.body.position = (WIDTH, self.body.position[1])
        else:
            if self.body.position[0] > WIDTH:
                self.body.position = (WIDTH, self.body.position[1])
            elif self.body.position[0] < 0:
                self.body.position = (0, self.body.position[1])

        if cyclic_vertical:
            if self.body.position[1] >= HEIGHT:
                self.body.position = (self.body.position[0], 0)
            elif self.body.position[1] <= 0:
                self.body.position = (self.body.position[0], HEIGHT)
        else:
            if self.body.position[1] > HEIGHT:
                self.body.position = (self.body.position[0], HEIGHT)
            elif self.body.position[1] < 0:
                self.body.position = (self.body.position[0], 0)


class Flock:
    def __init__(self, number_of_boids: int, space: pymunk.Space,
                 space_coordinates: tuple[int, int],
                 boid_size: int = 5,
                 speed_range: tuple[int, int] = (1, 3),
                 speed_scale: int = 100,
                 speed_active: bool = False,
                 avoid_range: int = 10,
                 avoid_factor: float = 0.05,
                 align_range: int = 50,
                 align_factor: float = 0.05,
                 cohesion_range: int = 50,
                 cohesion_factor: float = 0.05,
                 turn_margin: int = 50,
                 turn_factor: int = 1):
        self.number_of_boids = number_of_boids
        self.boids = []
        self.boid_scale = boid_size
        self.WIDTH = space_coordinates[0]
        self.HEIGHT = space_coordinates[1]
        self.space = space
        self.speed_active = speed_active
        self.speed_min, self.speed_max = Vec2d(*speed_range) * speed_scale
        self.speed_scale = speed_scale
        self.avoid_range = avoid_range
        self.avoid_factor = avoid_factor
        self.align_range = align_range
        self.align_factor = align_factor
        self.cohesion_range = cohesion_range
        self.cohesion_factor = cohesion_factor
        self.turn_margin = turn_margin
        self.turn_factor = turn_factor
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

    def reset_boids(self):
        for boid in self.boids:
            boid.change_boid((np.random.randint(self.WIDTH),
                              np.random.randint(self.HEIGHT)),
                             np.random.random() * 2 * np.pi,
                             self.speed_active)

    def convert_boid_to_tuples(self):
        return [(*boid.body.position, *boid.body.velocity) for boid in self.boids]

    # def convert_tuples_to_boids(self, velocities):
    #     for boid in self.boids:
    #         boid.body.

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
                             horizontal_cyclic_boundary: bool,
                             vertical_cyclic_boundary: bool,
                             separation_active: bool,
                             alignment_active: bool,
                             cohesion_active: bool,
                             vertical_wall_active: bool,
                             horizontal_wall_active: bool):
        for boid in self.boids:
            if check_boundaries:
                boid.check_boundaries(self.WIDTH, self.HEIGHT,
                                      cyclic_horizontal=horizontal_cyclic_boundary,
                                      cyclic_vertical=vertical_cyclic_boundary)
            if any([separation_active, alignment_active, cohesion_active, vertical_wall_active,
                    horizontal_wall_active]):
                close_dx, close_dy = 0, 0
                xvel_avg, yvel_avg, neighboring_boids_align = 0, 0, 0
                xpos_avg, ypos_avg, neighboring_boids_cohesion = 0, 0, 0
                boid_x, boid_y = boid.body.position
                for other in self.boids:
                    if other != boid:
                        other_x, other_y = other.body.position
                        boid_distance = distance.euclidean(boid.body.position, other.body.position)
                        if separation_active and boid_distance < self.avoid_range:
                            # boid_x, boid_y = boid.body.position
                            close_dx += boid_x - other_x
                            close_dy += boid_y - other_y

                        if alignment_active and boid_distance < self.align_range:
                            xvel_avg += other.body.velocity[0]
                            yvel_avg += other.body.velocity[1]
                            neighboring_boids_align += 1

                        if cohesion_active and boid_distance < self.cohesion_range:
                            xpos_avg += other_x
                            ypos_avg += other_y
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
                    cohesion_vx = ((xpos_avg / neighboring_boids_cohesion) - boid_x) * self.cohesion_factor
                    cohesion_vy = ((ypos_avg / neighboring_boids_cohesion) - boid_y) * self.cohesion_factor

                wall_vx = 0
                if horizontal_wall_active:
                    if boid_x < self.turn_margin:
                        wall_vx = self.turn_factor
                    elif boid_x > self.WIDTH - self.turn_margin:
                        wall_vx = -self.turn_factor

                wall_vy = 0
                if vertical_wall_active:
                    if boid_y < self.turn_margin:
                        wall_vy = self.turn_factor
                    elif boid_y > self.HEIGHT - self.turn_margin:
                        wall_vy = -self.turn_factor

                boid.change_velocity(
                    boid.body.velocity[0] + separation_vx + alignment_vx + cohesion_vx + wall_vx,
                    boid.body.velocity[1] + separation_vy + alignment_vy + cohesion_vy + wall_vy,
                    self.speed_max, self.speed_min
                )

    def update_boid_velocity_with_numba(self,
                                        check_boundaries: bool,
                                        horizontal_cyclic_boundary: bool,
                                        vertical_cyclic_boundary: bool,
                                        separation_active: bool,
                                        alignment_active: bool,
                                        cohesion_active: bool,
                                        vertical_wall_active: bool,
                                        horizontal_wall_active: bool):
        boid_coordinates = self.convert_boid_to_tuples()
        boid_velocities = update_boid_velocity_numba(boid_coordinates, self.WIDTH, self.HEIGHT,
                                                     separation_active, alignment_active, cohesion_active,
                                                     self.avoid_range, self.avoid_factor,
                                                     self.align_range, self.align_factor,
                                                     self.cohesion_range, self.cohesion_factor,
                                                     horizontal_wall_active, vertical_wall_active,
                                                     self.turn_margin, self.turn_factor)
        for boid, velocity in zip(self.boids, boid_velocities):
            if check_boundaries:
                boid.check_boundaries(self.WIDTH, self.HEIGHT,
                                      cyclic_horizontal=horizontal_cyclic_boundary,
                                      cyclic_vertical=vertical_cyclic_boundary)
            velocity_vx, velocity_vy = velocity
            boid.change_velocity(velocity_vx, velocity_vy, self.speed_max, self.speed_min)

    def update_parameters(self, parameters: BoidFlockingParameters):
        self.boid_scale = parameters.boid
        self.speed_active = parameters.speed_active
        self.speed_scale = parameters.speed_scale
        self.speed_min, self.speed_max = Vec2d(1, parameters.speed_range) * self.speed_scale
        self.avoid_range = parameters.avoid_range
        self.avoid_factor = parameters.avoid_factor
        self.align_range = parameters.align_range
        self.align_factor = parameters.align_factor
        self.cohesion_range = parameters.cohesion_range
        self.cohesion_factor = parameters.cohesion_factor
        self.turn_margin = parameters.boundary_margin
        self.turn_factor = parameters.boundary_factor


@nb.njit()
def update_boid_velocity_numba(flock, width, height, separation_active, alignment_active, cohesion_active,
                               avoid_range, avoid_factor, align_range, align_factor, cohesion_range, cohesion_factor,
                               horizontal_wall_active, vertical_wall_active, turn_margin, turn_factor):
    flock_length = len(flock)
    boid_velocities = []
    for index in nb.prange(flock_length):
        boid_vx, boid_vy = flock[index][2], flock[index][3]
        if separation_active or alignment_active or cohesion_active or horizontal_wall_active or vertical_wall_active:
            close_dx, close_dy = 0, 0
            xvel_avg, yvel_avg, neighboring_boids_align = 0, 0, 0
            xpos_avg, ypos_avg, neighboring_boids_cohesion = 0, 0, 0
            boid_x, boid_y = flock[index][0], flock[index][1]
            for other in flock:
                if other != flock[index]:
                    boid_distance = np.sqrt(((flock[index][0] - other[0]) ** 2) + ((flock[index][1] - other[1]) ** 2))
                    other_x, other_y = other[0], other[1]
                    other_vx, other_vy = other[2], other[3]
                    if separation_active and boid_distance < avoid_range:
                        close_dx += boid_x - other_x
                        close_dy += boid_y - other_y
                    if alignment_active and boid_distance < align_range:
                        xvel_avg += other_vx
                        yvel_avg += other_vy
                        neighboring_boids_align += 1
                    if cohesion_active and boid_distance < cohesion_range:
                        xpos_avg += other_x
                        ypos_avg += other_y
                        neighboring_boids_cohesion += 1
            separation_vx, separation_vy = 0, 0
            if separation_active:
                separation_vx = close_dx * avoid_factor
                separation_vy = close_dy * avoid_factor
            alignment_vx, alignment_vy = 0, 0
            if neighboring_boids_align > 0 and alignment_active:
                alignment_vx = ((xvel_avg / neighboring_boids_align) - boid_vx) * align_factor
                alignment_vy = ((yvel_avg / neighboring_boids_align) - boid_vy) * align_factor
            cohesion_vx, cohesion_vy = 0, 0
            if neighboring_boids_cohesion > 0 and cohesion_active:
                cohesion_vx = ((xpos_avg / neighboring_boids_cohesion) - boid_x) * cohesion_factor
                cohesion_vy = ((ypos_avg / neighboring_boids_cohesion) - boid_y) * cohesion_factor
            wall_vx = 0
            if horizontal_wall_active:
                if boid_x < turn_margin:
                    wall_vx = turn_factor
                elif boid_x > width - turn_margin:
                    wall_vx = -turn_factor
            wall_vy = 0
            if vertical_wall_active:
                if boid_y < turn_margin:
                    wall_vy = turn_factor
                elif boid_y > height - turn_margin:
                    wall_vy = -turn_factor
            boid_vx += separation_vx + alignment_vx + cohesion_vx + wall_vx
            boid_vy += separation_vy + alignment_vy + cohesion_vy + wall_vy
        boid_velocities.append((boid_vx, boid_vy))
    return boid_velocities


if __name__ == '__main__':
    pass
