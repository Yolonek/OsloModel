import numpy as np
import numba as nb
from OsloModelNumba import OsloModelNumba
from matplotlib.colors import LinearSegmentedColormap


@nb.njit()
def add_vectors(vector1: nb.int32[:], vector2: nb.int32[:]) -> nb.int32[:]:
    if len(vector1) > len(vector2):
        vector3 = vector1.copy()
        vector3[:len(vector2)] += vector2
    else:
        vector3 = vector2.copy()
        vector3[:len(vector1)] += vector1
    return vector3


def simulate_time_evolution(L, grains, is_randomly_incremented, threshold=tuple([2]), left_wall_closed=False):
    osloModel = OsloModelNumba(L=L, grains=grains, threshold=threshold, left_wall_closed=left_wall_closed)
    grid = osloModel.get_current_grid().copy()[:, None]
    for grain in range(grains):
        if is_randomly_incremented:
            osloModel.increment_randomly()
        else:
            osloModel.increment_top_left()
        grid = np.concatenate((grid, osloModel.get_current_grid()[:, None]), axis=1, dtype=np.int8)
        osloModel.system_relaxation()
        grid = np.concatenate((grid, osloModel.get_current_grid()[:, None]), axis=1, dtype=np.int8)
    steps, avalanche = osloModel.get_plot_data()
    return grid, steps, avalanche


def plot_time_evolution(L, steps, grid, axes=None):
    if axes:
        colors, quality = ['#000000', '#000000', '#ffc130', '#941100'], 4
        cmap = LinearSegmentedColormap.from_list('', colors, N=quality)
        vmax, vmin = grid.max(), grid.min()
        axes.pcolormesh(np.arange(0, steps + 0.5, 0.5), np.arange(L), grid[::-1, :],
                        cmap=cmap, vmin=vmin, vmax=vmax)
        axes.set(xlabel='time', yticks=[])


def plot_avalanche_size(steps, steps_array, avalanche, axes=None, ylim=1):
    if axes:
        axes.scatter(steps_array, avalanche / avalanche.max(), s=7, alpha=.5, color='black')
        axes.set(ylim=[0, ylim], xlim=[0, steps])
        axes.set_yticklabels('')
        axes.set_xticklabels('')
        axes.tick_params(axis='both', direction='out', length=0)
        axes.grid()
        axes.set_axisbelow(True)


def plot_avalanche_size_scatter(oslo_model, time_delta, axes=None, ylim=1, alpha=1, color='black'):
    if axes:
        steps, avalanche = oslo_model.get_plot_data()
        axes.scatter(steps, avalanche / avalanche.max(),
                     label=f'time taken: {time_delta:.3f} s',
                     s=10,
                     alpha=alpha,
                     color=color)
        axes.set(xlabel='time', ylabel=r'$\frac{s}{s_{max}}$', ylim=[0, ylim])
        axes.grid()
        axes.set_axisbelow(True)
        axes.legend(loc='upper left')


def calculate_avalanche_probabilities_with_trials(L, grains, trials, random_increment, left_wall_closed):
    osloModel = OsloModelNumba(L=L, grains=grains, left_wall_closed=left_wall_closed)
    avalanche_count = np.array([]).astype(np.int64)
    for trial in range(trials):
        osloModel.add_all_grains(random_increment)
        steps, avalanche = osloModel.get_plot_data()
        avalanche_count = add_vectors(avalanche_count, np.bincount(avalanche).astype(np.int64))
    return avalanche_count / np.sum(avalanche_count)


def calculate_avalanche_probabilities(L, grains, random_increment, left_wall_closed):
    osloModel = OsloModelNumba(L=L, grains=grains, left_wall_closed=left_wall_closed)
    osloModel.add_all_grains(random_increment)
    steps, avalanche = osloModel.get_plot_data()
    avalanche_count = np.bincount(avalanche).astype(np.int64)
    return avalanche_count / np.sum(avalanche_count)


def plot_scatter_histogram(L, avalanche_bins, avalanche_count, time_delta=0, axes=None, color='black'):
    if axes:
        axes.scatter(avalanche_bins, avalanche_count,
                     color=color,
                     s=10,
                     label=f'L={L}, time: {time_delta:.3f} s',
                     alpha=.7)
        axes.set(xlabel='avalanche size $s$',
                 ylabel='avalanche probability $P$',
                 xscale='log', yscale='log')
                 # xlim=[10, 1000])
        axes.legend(loc='lower left')
        axes.grid()
        axes.set_axisbelow(True)


if __name__ == '__main__':
    pass
