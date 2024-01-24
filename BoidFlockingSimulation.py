import sys
import pygame
import pymunk
import pymunk.pygame_util
from Flock import Flock
from UserInterface import UserInterface
import thorpy as tp
from time import time


def main():
    running = True
    pygame.init()
    WIDTH, HEIGHT = 1900, 1000
    window = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    fps = 30
    dt = 1 / fps
    use_numba = True

    space = pymunk.Space()
    user_interface = UserInterface(window, WIDTH, HEIGHT, margin=50)
    simulation_parameters = user_interface.get_parameters()
    # print(simulation_parameters)

    check_boundaries = True
    horizontal_cyclic_boundary = False
    vertical_cyclic_boundary = False
    separation_active = True
    alignment_active = True
    cohesion_active = True
    horizontal_wall_active = True
    vertical_wall_active = True

    number_of_bodies = 1000
    flock = Flock(number_of_bodies, space,
                  space_coordinates=(WIDTH, HEIGHT),
                  boid_size=2,
                  speed_scale=200,
                  speed_range=(1, 2),
                  speed_active=False,
                  avoid_range=15,
                  avoid_factor=2,
                  align_range=100,
                  align_factor=0.10,
                  cohesion_range=200,
                  cohesion_factor=0.05,
                  turn_margin=100,
                  turn_factor=20)

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
                    # simulation_parameters.speed_active = False
                    flock.stop_boids()
                else:
                    # simulation_parameters.speed_active = True
                    flock.accelerate_boids()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                check_boundaries = False if check_boundaries else True
                print(f'check_boundaries {check_boundaries}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                horizontal_cyclic_boundary = False if horizontal_cyclic_boundary else True
                print(f'horizontal_cyclic_boundary {horizontal_cyclic_boundary}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_3:
                vertical_cyclic_boundary = False if vertical_cyclic_boundary else True
                print(f'vertical_cyclic_boundary {vertical_cyclic_boundary}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_4:
                separation_active = False if separation_active else True
                print(f'separation_active {separation_active}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_5:
                alignment_active = False if alignment_active else True
                print(f'alignment_active {alignment_active}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_6:
                cohesion_active = False if cohesion_active else True
                print(f'cohesion_active {cohesion_active}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_7:
                horizontal_wall_active = False if horizontal_wall_active else True
                print(f'horizontal_wall_active {horizontal_wall_active}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_8:
                vertical_wall_active = False if vertical_wall_active else True
                print(f'vertical_wall_active {vertical_wall_active}')
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                flock.reset_boids()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                use_numba = False if use_numba else True
                print(f'use numba {use_numba}')

        # if simulation_parameters != user_interface.get_parameters():
        #     simulation_parameters = user_interface.get_parameters()
        #     flock.update_parameters(simulation_parameters)
        if flock.speed_active:
            start = time()
            if use_numba:
                flock.update_boid_velocity_with_numba(
                    check_boundaries=check_boundaries,
                    horizontal_cyclic_boundary=horizontal_cyclic_boundary,
                    vertical_cyclic_boundary=vertical_cyclic_boundary,
                    separation_active=separation_active,
                    alignment_active=alignment_active,
                    cohesion_active=cohesion_active,
                    vertical_wall_active=vertical_wall_active,
                    horizontal_wall_active=horizontal_wall_active
                )
            else:
                flock.update_boid_velocity(
                    check_boundaries=check_boundaries,
                    horizontal_cyclic_boundary=horizontal_cyclic_boundary,
                    vertical_cyclic_boundary=vertical_cyclic_boundary,
                    separation_active=separation_active,
                    alignment_active=alignment_active,
                    cohesion_active=cohesion_active,
                    vertical_wall_active=vertical_wall_active,
                    horizontal_wall_active=horizontal_wall_active
                )
            print(f'fps: {time() - start:.6f}')

        # user_interface.parameter_changed()
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