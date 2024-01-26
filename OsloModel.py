import numpy as np
from matplotlib import pyplot as plt


class OsloModel:
    def __init__(self, L=10, grains=10, threshold=(1, 2), left_wall_closed=False):
        self.L = L
        self.grid = np.zeros(self.L, dtype=np.int8)
        self.step = 0
        self.grains = grains
        self.size_array = np.zeros(grains, dtype=np.int32)
        self.critical_value_options = np.array(threshold, dtype=np.int8)
        self.left_wall_closed = left_wall_closed

    def change_boundary_condition(self, is_closed):
        self.left_wall_closed = is_closed

    def get_current_grid(self):
        return self.grid

    def get_plot_data(self):
        return np.arange(1, self.grains), self.size_array

    def reset_parameters(self):
        self.grid = np.zeros(self.L, dtype=np.int8)
        self.step = 0
        self.size_array = np.zeros(self.grains, dtype=np.int32)

    def increment_top_left(self):
        self.grid[0] += 1

    def increment_randomly(self):
        self.grid[np.random.choice(self.L)] += 1

    def single_relaxation(self, thresholds):
        size = 0
        for index, site in enumerate(self.grid):
            if site >= thresholds[index]:
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
        return size

    def system_relaxation(self):
        thresholds = np.random.choice(self.critical_value_options, size=self.L).astype(np.int8)
        avalanche_total_size = 0
        while True:
            avalanche_size = self.single_relaxation(thresholds)
            if avalanche_size == 0:
                break
            else:
                avalanche_total_size += avalanche_size
        self.size_array[self.step] = avalanche_total_size
        self.step += 1

    def add_all_grains(self, random_increment=False):
        self.reset_parameters()
        for _ in range(self.grains):
            if random_increment:
                self.increment_randomly()
            else:
                self.increment_top_left()
            self.system_relaxation()

    def calculate_avalanche_probabilities(self, bins, density):
        steps, avalanche = self.get_plot_data()
        avalanche_count, avalanche_bins = np.histogram(avalanche, bins=bins, density=density)
        avalanche_bins = np.array([0.5 * (avalanche_bins[i] + avalanche_bins[i + 1]) for i in range(len(avalanche_count))])
        print(avalanche_count.dtype, avalanche_bins.dtype)
        print(len(avalanche_count), len(avalanche_bins))
        return avalanche_bins, avalanche_count


if __name__ == '__main__':
    L = 50
    grains = 100
    is_random = False
    model = OsloModel(L=L, grains=grains, threshold=tuple([1, 2]), left_wall_closed=True)
    model.add_all_grains(random_increment=is_random)
    print(model.size_array)
    a = model.calculate_avalanche_probabilities(10, False)
    b = model.calculate_avalanche_probabilities(10, True)
    print(a[1] / a[1].sum())
    print(b[1])
    print(b[1].sum())


