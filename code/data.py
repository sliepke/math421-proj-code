import copy, decimal, numpy, json, pathlib
from PIL import Image, ImageDraw
import constants, base, strats

# round n to nearest multiple of r exactly (simpler methods give results like 15.5000001)
# should be used when r is something expressible in a short decimal string such as 0.05 or 0.025
def round_nearest(n, r):
    n, r = decimal.Decimal(str(n)), decimal.Decimal(str(r))
    return float(round(n / r) * r)

class Trial:
    def __init__(self, compliance, avg_carry_ons, sample_size):
        self.compliance = compliance
        self.avg_carry_ons = avg_carry_ons
        self.sample_size = sample_size
        
        self.time_avg = None
        self.time_pmin = None
        self.time_pmax = None
        self.times = None
    def __str__(self):
        return "[compliance=" + str(self.compliance) + ", avg_carry_ons=" + \
            str(self.avg_carry_ons) + ", sample_size=" + str(self.sample_size) + \
            ", time_avg=" + str(self.time_avg) + ", time_pmin=" + str(self.time_pmin) + \
            ", time_pmax=" + str(self.time_pmax) + "]"

# returns a 2-tuple: first element is a strat type, second is a list of trial objects
def load_trials_from_json(filename):
    file = open(filename)
    data = json.load(file)
    strat_type = strats.str_to_class(data["stratname"])
    
    # create trial objects from the trial dictionaries in the json file
    trial_dict_list = data["trial_list"]
    trial_obj_list = []
    for trial_dict in trial_dict_list:
        trial = Trial(trial_dict["compliance"], trial_dict["avg_carry_ons"], trial_dict["sample_size"])
        trial.time_avg = trial_dict["time_avg"]
        trial.time_pmin = trial_dict["time_pmin"]
        trial.time_pmax = trial_dict["time_pmax"]
        trial.times = trial_dict["times"]
        trial_obj_list += [trial]
    
    file.close()
    return (strat_type, trial_obj_list)

# returns new trial list, also (optionally) saves them to json
def run_and_save_samples(strat_type, trial_list, filename, save=True):
    # copy trial list
    new_trial_list = []
    for trial in trial_list:
        new_trial_list += [copy.copy(trial)]
    # run trials, set trial attributes accordingly
    for trial in new_trial_list:
        trial.times = []
        # run trial
        for i in range(trial.sample_size):
            sim = base.Simulation(strat_type, trial.compliance, trial.avg_carry_ons)
            trial.times += [round_nearest(sim.run(), constants.tick_time)]
        # compute statistics
        trial.time_avg = numpy.average(trial.times)
        trial.time_pmin = round_nearest(numpy.percentile(trial.times, 5), constants.tick_time)
        trial.time_pmax = round_nearest(numpy.percentile(trial.times, 95), constants.tick_time)
    
    if not save: return new_trial_list
    
    # convert each trial into a dictionary for json
    trial_dict_list = []
    for trial in new_trial_list:
        dct = {}
        dct["compliance"] = trial.compliance; dct["avg_carry_ons"] = trial.avg_carry_ons
        dct["sample_size"] = trial.sample_size; dct["time_avg"] = trial.time_avg
        dct["time_pmin"] = trial.time_pmin; dct["time_pmax"] = trial.time_pmax
        dct["times"] = trial.times
        trial_dict_list += [dct]
    # save trial list to file in json format
    json_obj = json.dumps({"stratname": strat_type.__name__, "trial_list": trial_dict_list})
    
    with open(filename, "w") as file:
        file.write(json_obj)
    
    return new_trial_list

# creates plot comparing times of the 3 methods; starting parameters of trials should be the same
# saves plot as image, I combine the images in image editor later
def draw_plot(trial_rand, trial_seat, trial_row, img_dir_name):
    compliance_st = str(trial_rand.compliance).replace(".", "_")
    avg_carry_ons_st = str(trial_rand.avg_carry_ons).replace(".", "_")
    filename = compliance_st + "-" + avg_carry_ons_st + ".png"
    im = Image.new("RGBA", (constants.plot_width, constants.plot_height), "rgba(0, 0, 0, 0)")
    draw = ImageDraw.Draw(im)
    
    # plot datapoints
    i = 0
    for strat_i in (trial_rand, trial_seat, trial_row):
        color = constants.plot_colors[i]
        x = constants.plot_width * (i + 1) / 4
        
        # plot circle (average time)
        circle_center_y = constants.plot_height \
            - constants.plot_height * strat_i.time_avg / constants.max_time_expected
        circle_xy1 = (x - constants.circle_radius, circle_center_y - constants.circle_radius)
        circle_xy2 = (x + constants.circle_radius, circle_center_y + constants.circle_radius)
        draw.ellipse([circle_xy1, circle_xy2], fill = color, width = constants.line_width)
        
        # plot bottom line (5th percentile)
        bline_y = constants.plot_height \
            - constants.plot_height * strat_i.time_pmin / constants.max_time_expected
        bline_xy1 = (x - constants.line_length / 2, bline_y)
        bline_xy2 = (x + constants.line_length / 2, bline_y)
        draw.line([bline_xy1, bline_xy2], fill = color, width = constants.line_width)
        
        # plot top line (95th percentile)
        tline_y = constants.plot_height \
            - constants.plot_height * strat_i.time_pmax / constants.max_time_expected
        tline_xy1 = (x - constants.line_length / 2, tline_y)
        tline_xy2 = (x + constants.line_length / 2, tline_y)
        draw.line([tline_xy1, tline_xy2], fill = color, width = constants.line_width)
        
        i += 1
    
    # save image
    img_dir = pathlib.Path(img_dir_name)
    if not img_dir.exists():
        img_dir.mkdir()
    elif not img_dir.is_dir():
        img_dir = pathlib.Path(".")
    im.save(img_dir / filename)