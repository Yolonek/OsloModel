import sys
import pygame
import pymunk
import pymunk.pygame_util
from Flock import Flock
from UserInterface import UserInterface
import thorpy as tp


def main():
    running = True
    pygame.init()
    WIDTH, HEIGHT = 1900, 1000
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fps = 30
    dt = 1 / fps

    space = pymunk.Space()
    user_interface = UserInterface(window, WIDTH, HEIGHT, margin=50)
    simulation_parameters = user_interface.get_parameters()
    # print(simulation_parameters)

    number_of_bodies = 50
    flock = Flock(number_of_bodies, space,
                  space_coordinates=(WIDTH, HEIGHT),
                  boid_size=simulation_parameters.boid,
                  speed_scale=simulation_parameters.speed_scale,
                  speed_range=(1, simulation_parameters.speed_range),
                  speed_active=simulation_parameters.speed_active,
                  avoid_range=simulation_parameters.avoid_range,
                  avoid_factor=simulation_parameters.avoid_factor,
                  align_range=simulation_parameters.align_range,
                  align_factor=simulation_parameters.align_factor,
                  cohesion_range=simulation_parameters.cohesion_range,
                  cohesion_factor=simulation_parameters.cohesion_factor,
                  turn_margin=simulation_parameters.boundary_margin,
                  turn_factor=simulation_parameters.boundary_factor)

    draw_options = pymunk.pygame_util.DrawOptions(window)

    while running:
        mouse_rel = pygame.mouse.get_rel()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                if user_interface.get_menu_state():
                    user_interface.deactivate_menu()
                else:
                    user_interface.activate_menu()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                if flock.speed_active:
                    simulation_parameters.speed_active = False
                    flock.stop_boids()
                else:
                    simulation_parameters.speed_active = True
                    flock.accelerate_boids()
        if simulation_parameters != user_interface.get_parameters():
            simulation_parameters = user_interface.get_parameters()
            flock.update_parameters(simulation_parameters)
        if flock.speed_active:
            flock.update_boid_velocity(
                check_boundaries=simulation_parameters.boundary_active,
                horizontal_cyclic_boundary=simulation_parameters.cyclic_horizontal,
                vertical_cyclic_boundary=simulation_parameters.cyclic_vertical,
                separation_active=simulation_parameters.avoid_active,
                alignment_active=simulation_parameters.align_active,
                cohesion_active=simulation_parameters.cohesion_active,
                vertical_wall_active=simulation_parameters.wall_vertical,
                horizontal_wall_active=simulation_parameters.wall_horizontal
            )
        
        user_interface.parameter_changed()
        window.fill((11, 11, 11))
        space.debug_draw(draw_options)
        user_interface.update(events, mouse_rel)
        pygame.display.update()
        space.step(dt)
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    # sys.exit(main())
    main()