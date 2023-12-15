# the width (in inches) of each row
# or, the distance between a point on a seat and the same point on a seat in front or behind it
seat_pitch = 30

# number of rows of seats in the cabin
num_rows = 32

# the time (in seconds) for a passenger to move from a seat to the seat next to them, or to the hallway
seat_move_time = 3

# how much space (in inches) someone takes up while standing
# or, the diameter of the interval that they occupy while in the hallway
hall_interval_size = 25

# how much real world time (in seconds) a tick represents
tick_time = 0.05

# how much time it takes for someone to pick up a carry-on bag from the overhead bins
carry_on_time = 4

# mean, standard deviation, and minimum of walkspeed in in / sec
# walkspeeds are generated on a normal distribution using these parameters
walk_speed_mean = 44
walk_speed_sd = 18
walk_speed_min = 10

seat_letters = ['A', 'B', 'C', 'D', 'E', 'F']
num_letters = len(seat_letters)

# maximum amount of (simulated) time (in seconds) that a simulation will run for
sim_time_max = 60 * 60

# plot width and height (in pixels)
plot_width = 150
plot_height = 400
# radius of circles (in pixels) when plotting
circle_radius = 4
# length of lines (in pixels) when plotting the pmin and pmax values
line_length = 16
# width of lines (in pixels) when plotting
line_width = 3
# used for plotting; the highest possible point of a plot corresponds to this time (in seconds)
max_time_expected = 15 * 60
# colors used to plot; the color of datapoints indicate the strat of the datapoint
plot_colors = ("red", "blue", "green")

# conversion between a row number (for example 3) and the position of the row (in inches) on the hallway
# or, the position on the hallway that a passenger takes when they move from a seat to the hallway
def row_to_hall_position(row):
    return float(row) * seat_pitch