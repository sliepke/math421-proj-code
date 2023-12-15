# other libraries
import collections, pathlib, random
from matplotlib import pyplot as plt
import numpy as np
# my modules
import constants, base, strats, data


# used to load trialset and create individual plots for each pair of compliance and carry-on values
# the plots were combined using an image editor to make the final graphs
def load_and_plot_trialset(trialset_dir, img_dir):
    # load
    trials_rand = data.load_trials_from_json(trialset_dir + "/trials-random-strat.json")[1]
    trials_seat = data.load_trials_from_json(trialset_dir + "/trials-seat-strat.json")[1]
    trials_row = data.load_trials_from_json(trialset_dir + "/trials-row-strat.json")[1]
    # plot
    for i in range(len(trials_rand)):
        t_rand = trials_rand[i]
        t_seat = trials_seat[i]
        t_row = trials_row[i]
        data.draw_plot(t_rand, t_seat, t_row, img_dir)


# used to make background of graph
# I used image editor to place the individual plots onto this figure
def make_figure():
    fig, ax = plt.subplots()
    
    ax.grid(True)
    ax.set(xlim=(0, 31.125), xticks = np.array([]), ylim=(0, 15), yticks=np.arange(0, 16))
    ax.set_ylabel("Time until finish (min)")
    
    fig = plt.gcf()
    fig.set_size_inches(8.3, 4)
    fig.savefig('Figure.png', dpi=100)
    
    plt.show()


def run_and_save_trialset(compliance_values, carry_on_values, sample_size, trialset_dir_name):
    # make trial list, same trials will be used for all 3 strats
    trial_list = []
    for compliance in compliance_values:
        for avg_carry_ons in carry_on_values:
            t = data.Trial(compliance, avg_carry_ons, sample_size)
            trial_list += [t]
    
    # make trialset directory if it does not already exist
    trialset_dir = pathlib.Path(trialset_dir_name)
    if not trialset_dir.exists():
        trialset_dir.mkdir()
    elif not trialset_dir.is_dir():
        trialset_dir = pathlib.Path(".")
    
    # run all trials, save them to json files to save progress
    trials_rand = data.run_and_save_samples(strats.random_strat, trial_list, \
        trialset_dir_name + "/trials-random-strat.json")
    trials_seat = data.run_and_save_samples(strats.seat_strat, trial_list, \
        trialset_dir_name +  "/trials-seat-strat.json")
    trials_row = data.run_and_save_samples(strats.row_strat, trial_list, \
        trialset_dir_name + "/trials-row-strat.json")


# runs all 30 trials, each with 50 samples, then saves them to json files
# !!WARNING!! - takes a long time (~3-4hr for me when using 32 rows)
def run_and_save_big_trialset(trialset_dir_name):
    compliance_values = [0, 0.25, 0.5, 0.75, 0.9, 1]
    carry_on_values = [0, 0.25, 0.5, 0.75, 1]
    sample_size = 50
    trialset_dir_name = "big-trialset2"
    
    run_and_save_trialset(compliance_values, carry_on_values, sample_size, trialset_dir_name)