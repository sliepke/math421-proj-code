###
# this module is a great way to test running individual simulations or a trial,
# without it taking forever or requiring familiarity with all the other code
# example usage and simple, understandable descriptions are included
###

import pathlib
import constants, base, strats, data, main

# use less rows for this module, so that trials don't take so long
constants.num_rows = 4


# example usage: test.test_ticks("random_strat", 0.5, 0.75)
#   (can pick random_strat, seat_strat, or row_strat)
# every time you enter a number, the simulation will tick that many times
# then, the cabin will be displayed
# a passenger's p_id is displayed at their location
# passengers moving from seat to seat, or from seat to hall, are considered to
#   occupy 2 locations
# stop it with CTRL+C
def test_ticks(strat_name, compliance, avg_carry_ons):
    strat_type = strats.str_to_class(strat_name)
    sim = base.Simulation(strat_type, compliance, avg_carry_ons)
    
    tick_num = 1
    while True:
        print("\ncabin at " + str( data.round_nearest(sim.time_elapsed, \
            constants.tick_time) ) + " seconds")
        sim.print_cabin()
        tick_num = int(input("\nticks: "))
        for j in range(tick_num):
            sim.tick()


# example usage: test.run_and_save_trial("random_strat", 0.5, 0.75, 4, "random-test1")
#   (can pick random_strat, seat_strat, or row_strat)
# this is a redundant, but more user-friendly and single-strat version of main.run_and_save_trialset()
# the trial will automatically be saved to the test-trials directory
def run_and_save_trial(strat_name, compliance, avg_carry_ons, sample_size, filename):
    strat_type = strats.str_to_class(strat_name)
    trial = data.Trial(compliance, avg_carry_ons, sample_size)
    
    # make test-trials directory if doesn't yet exist
    trialset_dir = pathlib.Path("test-trials")
    if not trialset_dir.exists():
        trialset_dir.mkdir()
    elif not trialset_dir.is_dir():
        trialset_dir = pathlib.Path(".")
    
    data.run_and_save_samples(strat_type, [trial], "test-trials/" + filename + ".json")