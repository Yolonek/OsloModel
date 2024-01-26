import numpy as np
from matplotlib import pyplot as plt
import numba as nb
from numba.experimental import jitclass


spec = [
    ('L', nb.int16),
    ('grid', nb.int8[:]),
    ('step', nb.int32),
    ('grains', nb.int32),
    ('size_array', nb.int64[:]),
    ('critical_value_options', nb.int8[:]),
    ('left_wall_closed', nb.boolean)
]


@jitclass(spec)
class OsloModelNumba:
    def __init__(self, L: nb.int16 = 10,
                 grains: nb.int32 = 10,
                 threshold: tuple[nb.int8] = (1, 2),
                 left_wall_closed: nb.boolean = False):
        self.L = L
        self.grid = np.zeros(self.L, dtype=nb.int8)
        self.step = 0
        self.grains = grains
        self.size_array = np.zeros(grains, dtype=nb.int64)
        self.critical_value_options = np.array(threshold, dtype=nb.int8)
        self.left_wall_closed = left_wall_closed

    def change_boundary_condition(self, is_closed: nb.boolean) -> None:
        self.left_wall_closed = is_closed

    def get_current_grid(self) -> nb.int8[:]:
        return self.grid

    def get_plot_data(self) -> tuple[nb.int64[:], nb.int64[:]]:
        return np.arange(1, self.grains + 1), self.size_array

    def reset_parameters(self) -> None:
        self.grid = np.zeros(self.L, dtype=nb.int8)
        self.step = 0
        self.size_array = np.zeros(self.grains, dtype=nb.int64)

    def increment_top_left(self) -> None:
        self.grid[0] += 1

    def increment_randomly(self) -> None:
        self.grid[np.random.choice(self.L)] += 1

    def single_relaxation(self, thresholds: nb.int8) -> nb.int64:
        size = 0
        for index, site in enumerate(self.grid):
            if site > thresholds[index]:
                size += 1
                if self.L - 1 > index > 0:
                    self.grid[index] -= 2
                    self.grid[index + 1] += 1
                    self.grid[index - 1] += 1
                elif index == 0:
                    self.grid[index] -= 1 if self.left_wall_closed else 2
                    self.grid[index + 1] += 1
                else:
                    self.grid[index] -= 2
                    self.grid[index - 1] += 1
                    # size += 1
        return 1 if size else 0

    def system_relaxation(self) -> None:
        thresholds = np.random.choice(self.critical_value_options, size=self.L).astype(nb.int8)
        avalanche_total_size = 0
        while True:
            avalanche_size = self.single_relaxation(thresholds)
            if avalanche_size == 0:
                break
            else:
                avalanche_total_size += avalanche_size
        self.size_array[self.step] = avalanche_total_size
        self.step += 1

    def add_all_grains(self, random_increment: nb.boolean) -> None:
        self.reset_parameters()
        for _ in range(self.grains):
            if random_increment:
                self.increment_randomly()
            else:
                self.increment_top_left()
            self.system_relaxation()

    def calculate_avalanche_histogram(self, bins: nb.int32, starts_from: nb.int32 = 0)\
            -> tuple[nb.float64[:], nb.float64[:]]:
        steps, avalanche = self.get_plot_data()
        if starts_from > 0:
            avalanche = avalanche[starts_from:]
        avalanche_count, avalanche_bins = np.histogram(avalanche, bins=bins)
        avalanche_bins = np.array(
            [0.5 * (avalanche_bins[i] + avalanche_bins[i + 1]) for i in range(len(avalanche_count))])
        return avalanche_bins, avalanche_count


if __name__ == '__main__':
    L = 200
    grains = 1000
    is_random = False
    model = OsloModelNumba(L=L, grains=grains, left_wall_closed=True)
    model.add_all_grains(is_random)
    print(model.size_array)
    print(model.calculate_avalanche_histogram(10))

