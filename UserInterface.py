import thorpy as tp
from dataclasses import dataclass


@dataclass
class BoidFlockingParameters:
    boid: int = 5

    speed_active: bool = False
    speed_range: int = 3
    speed_scale: int = 100

    avoid_active: bool = False
    avoid_range: int = 50
    avoid_factor: float = 0.4

    align_active: bool = False
    align_range: int = 100
    align_factor: float = 0.2

    cohesion_active: bool = False
    cohesion_range: int = 100
    cohesion_factor: float = 0.5

    boundary_active: bool = True
    boundary_margin: int = 50
    boundary_factor: int = 10

    cyclic_horizontal: bool = True
    cyclic_vertical: bool = True

    wall_horizontal: bool = False
    wall_vertical: bool = False


class UserInterface:
    def __init__(self, window, width, height, margin: int = 100):
        tp.init(window, tp.theme_text_dark)
        tp.TitleBox.style_normal.bottom_line = False
        tp.TitleBox.style_normal.left_line = False
        tp.TitleBox.style_normal.right_line = False

        self.WIDTH = width
        self.HEIGHT = height
        self.margin = margin
        self.window = window

        self.menu_active = False
        self.updater = None

        self.row_boid = None
        self.row_speed, self.box_speed = None, None
        self.row_avoid, self.box_avoid = None, None
        self.row_align, self.box_align = None, None
        self.row_cohesion, self.box_cohesion = None, None
        self.row_boundary, self.box_boundary = None, None
        self.row_cyclic, self.box_cyclic = None, None
        self.row_wall, self.box_wall = None, None
        self.main_box = None

        self.parameters = BoidFlockingParameters()

        self.create_row_boid()
        self.create_row_speed()
        self.create_row_avoid()
        self.create_row_align()
        self.create_row_cohesion()
        self.create_row_boundary()
        self.create_main_box()
        self.create_updater()

    def get_parameters(self):
        return self.parameters

    def create_row_boid(self):
        self.row_boid = tp.SliderWithText('Boid size', 1, 10, self.parameters.boid, 100)
        # print(self.row_boid.get_value())

    def create_row_speed(self):
        speed_active = tp.SwitchButton(False)
        speed_active.at_unclick = self.parameter_changed
        speed_range = tp.SliderWithText('scale', 1, 10, self.parameters.speed_range, 40)
        speed_range.at_unclick = self.parameter_changed
        speed_scale = tp.SliderWithText('range', 100, 500, self.parameters.speed_scale, 40)
        speed_scale.at_unclick = self.parameter_changed
        self.row_speed = tp.Group([speed_active, speed_range, speed_scale], 'h')
        self.box_speed = tp.TitleBox('Speed', children=[self.row_speed])

    def create_row_avoid(self):
        avoid_active = tp.SwitchButtonWithText('active', texts=('', ''), value=self.parameters.avoid_active)
        avoid_active.at_unclick = self.parameter_changed
        avoid_range = tp.SliderWithText('range', 10, 200, self.parameters.avoid_range, 40)
        avoid_range.at_unclick = self.parameter_changed
        avoid_factor = tp.SliderWithText('factor', 0, 2, self.parameters.avoid_factor, 40)
        avoid_factor.at_unclick = self.parameter_changed
        self.row_avoid = tp.Group([avoid_active, avoid_range, avoid_factor], 'h')
        self.box_avoid = tp.TitleBox('Avoidance', children=[self.row_avoid])

    def create_row_align(self):
        align_active = tp.SwitchButtonWithText('active', texts=('', ''), value=self.parameters.align_active)
        align_active.at_unclick = self.parameter_changed
        align_range = tp.SliderWithText('range', 10, 500, self.parameters.align_range, 40)
        align_range.at_unclick = self.parameter_changed
        align_factor = tp.SliderWithText('factor', 0, 2, self.parameters.align_factor, 40)
        align_factor.at_unclick = self.parameter_changed
        self.row_align = tp.Group([align_active, align_range, align_factor], 'h')
        self.box_align = tp.TitleBox('Alignment', children=[self.row_align])

    def create_row_cohesion(self):
        cohesion_active = tp.SwitchButtonWithText('active', texts=('', ''), value=self.parameters.cohesion_active)
        cohesion_active.at_unclick = self.parameter_changed
        cohesion_range = tp.SliderWithText('range', 10, 500, self.parameters.cohesion_range, 40)
        cohesion_range.at_unclick = self.parameter_changed
        cohesion_factor = tp.SliderWithText('factor', 0, 2, self.parameters.cohesion_active, 40)
        cohesion_factor.at_unclick = self.parameter_changed
        self.row_cohesion = tp.Group([cohesion_active, cohesion_range, cohesion_factor], 'h')
        self.box_cohesion = tp.TitleBox('Cohesion', children=[self.row_cohesion])

    def create_row_boundary(self):
        boundary_active = tp.SwitchButtonWithText('active', texts=('', ''), value=self.parameters.boundary_active)
        boundary_active.at_unclick = self.parameter_changed
        boundary_margin = tp.SliderWithText('margin', 10, 500, self.parameters.boundary_margin, 40)
        boundary_margin.at_unclick = self.parameter_changed
        boundary_factor = tp.SliderWithText('factor', 2, 100, self.parameters.boundary_factor, 40)
        boundary_factor.at_unclick = self.parameter_changed
        self.row_boundary = tp.Group([boundary_active, boundary_margin, boundary_factor], 'h')
        self.create_row_cyclic()
        self.create_row_wall()
        self.box_boundary = tp.TitleBox('Boundaries', children=[self.row_boundary, self.box_cyclic, self.box_wall])

    def create_row_cyclic(self):
        cyclic_horizontal = tp.SwitchButtonWithText('Horizontal', texts=('on', 'off'),
                                                    value=self.parameters.cyclic_horizontal)
        cyclic_horizontal.at_unclick = self.parameter_changed
        cyclic_vertical = tp.SwitchButtonWithText('Vertical', texts=('on', 'off'),
                                                  value=self.parameters.cyclic_vertical)
        cyclic_vertical.at_unclick = self.parameter_changed
        self.row_cyclic = tp.Group([cyclic_horizontal, cyclic_vertical], 'h')
        self.box_cyclic = tp.TitleBox('Cyclic', children=[self.row_cyclic])

    def create_row_wall(self):
        wall_horizontal = tp.SwitchButtonWithText('Horizontal', texts=('on', 'off'),
                                                  value=self.parameters.wall_horizontal)
        wall_horizontal.at_unclick = self.parameter_changed
        wall_vertical = tp.SwitchButtonWithText('Vertical', texts=('on', 'off'),
                                                value=self.parameters.wall_vertical)
        wall_vertical.at_click = self.parameter_changed
        self.row_wall = tp.Group([wall_horizontal, wall_vertical], 'h')
        self.box_wall = tp.TitleBox('Wall', children=[self.row_wall])

    def create_main_box(self):
        children = [self.row_boid, self.box_speed, self.box_avoid, self.box_align, self.box_cohesion, self.box_boundary]
        self.main_box = tp.TitleBox('Parameters', children=children)
        self.main_box.set_topleft(self.WIDTH - self.main_box.rect.size[0] - self.margin, self.margin)
        # self.main_box.at_unclick = self.main_box_clicked

    def parameter_changed(self):
        speed_widgets = self.row_speed.get_children()
        avoid_widgets = self.row_avoid.get_children()
        align_widgets = self.row_align.get_children()
        cohesion_widgets = self.row_cohesion.get_children()
        boundary_widgets = self.row_boundary.get_children()
        cyclic_widgets = self.row_cyclic.get_children()
        wall_widgets = self.row_wall.get_children()
        new_parameters = BoidFlockingParameters(boid=self.row_boid.get_value(),
                                                speed_active=speed_widgets[0].get_value(),
                                                speed_range=speed_widgets[1].get_value(),
                                                speed_scale=speed_widgets[2].get_value(),
                                                avoid_active=avoid_widgets[0].get_value(),
                                                avoid_range=avoid_widgets[1].get_value(),
                                                avoid_factor=avoid_widgets[2].get_value(),
                                                align_active=align_widgets[0].get_value(),
                                                align_range=align_widgets[1].get_value(),
                                                align_factor=align_widgets[2].get_value(),
                                                cohesion_active=cohesion_widgets[0].get_value(),
                                                cohesion_range=cohesion_widgets[1].get_value(),
                                                cohesion_factor=cohesion_widgets[2].get_value(),
                                                boundary_active=boundary_widgets[0].get_value(),
                                                boundary_margin=boundary_widgets[1].get_value(),
                                                boundary_factor=boundary_widgets[2].get_value(),
                                                cyclic_horizontal=cyclic_widgets[0].get_value(),
                                                cyclic_vertical=cyclic_widgets[1].get_value(),
                                                wall_horizontal=wall_widgets[0].get_value(),
                                                wall_vertical=wall_widgets[1].get_value())
        self.parameters = new_parameters
        print(new_parameters)

    def create_updater(self):
        self.updater = self.main_box.get_updater()

    def activate_menu(self):
        self.menu_active = True

    def deactivate_menu(self):
        self.menu_active = False

    def get_menu_state(self):
        return self.menu_active

    def update(self, events, mouse_rel):
        if self.menu_active:
            self.updater.update(events=events, mouse_rel=mouse_rel)

    # def update
