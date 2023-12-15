import collections, random
import constants


## -- passenger class -- ##


class Passenger:
    def __init__(self, p_id, starting_seat, walkspeed, carry_ons, compliant):
        self.p_id = p_id
        self.location = starting_seat
        self.location_moving_to = None
        self.state = "default"
        self.move_time_remaining = None
        self.carry_on_time_remaining = None
        self.walkspeed = walkspeed
        self.carry_ons_left = carry_ons
        self.compliant = compliant


## -- simulation class -- ##


class Simulation:
    def __init__(self, strat_type, compliance, avg_carry_ons):
        # all attributes
        self.strat_type = strat_type
        self.strat = None
        self.compliance = compliance
        self.avg_carry_ons = avg_carry_ons
        self.passenger_list = []
        self.hall_llist = collections.deque()
        self.seat_map = {}
        self.finished = False
        self.time_elapsed = 0
        
        # initialize passenger list and seat map
        # a passenger's id must correspond to their index in passenger_list
        for row in range(1, constants.num_rows + 1):
            for i in range(constants.num_letters):
                # set passenger parameters
                p_id = (row - 1) * constants.num_letters + i
                starting_seat = str(row) + constants.seat_letters[i]
                rand_speed = random.gauss(constants.walk_speed_mean, constants.walk_speed_sd)
                walkspeed = max(rand_speed, constants.walk_speed_min)
                carry_ons = min( int(random.uniform(0, 1) + self.avg_carry_ons), 1 )
                compliant = (random.uniform(0, 1) < self.compliance)
                
                # create passenger, place passenger in passenger_list and seat_map
                passenger = Passenger(p_id, starting_seat, walkspeed, carry_ons, compliant)
                self.passenger_list += [passenger]
                self.seat_map[passenger.location] = passenger.p_id
        
        # initialize strat
        self.strat = strat_type(self.passenger_list, self.seat_map, self.hall_llist)
    def print_attributes(self):
        print("simulation attributes:")
        print("\tstrat_type: " + str(self.strat_type))
        print("\tcompliance: " + str(self.compliance))
        print("\tavg carry ons: " + str(self.avg_carry_ons))
        print("\tfinished: " + str(self.finished))
        print("\ttime elapsed: " + str(self.time_elapsed))
    def print_passenger(self, p):
        print("id: " + str(p.p_id))
        print("\tlocation: " + str(p.location))
        print("\tstate: " + str(p.state))
        if p.state == "moving":
            print("\t\tlocation moving to: " + str(p.location_moving_to))
            print("\t\tmove time remaining: " + str(p.move_time_remaining))
        elif p.state == "grabbing-carry-on":
            print("\t\tcarry on time remaining: " + str(p.carry_on_time_remaining))
        print("\twalkspeed: " + str(p.walkspeed))
        print("\tcarry ons left: " + str(p.carry_ons_left))
        print("\tcompliant: " + str(p.compliant))
    def print_passengers(self):
        print("== passenger list ==\n")
        for p in self.passenger_list:
            self.print_passenger(p)
        print()
    def print_cabin(self):
        print("\n== seats ==\n")
        for letter in ['F', 'E', 'D', 'C', 'B', 'A']:
            for row in range(1, constants.num_rows + 1):
                location = str(row) + letter
                p_id = self.seat_map[location]
                if p_id == None:
                    print(location + ": X\t", end="")
                else:
                    print(location + ": " + str(p_id) + "\t", end="")
            print()
        print("\nhall: ", end="")
        for i in range( len(self.hall_llist) ):
            if i != 0: print("--", end="")
            print(str(self.hall_llist[i]), end="")
        print()
    def tick(self):
        if self.finished == True: return
        # update strat's state
        self.strat.tick_update()
        # update all passengers according to disembarking method
        all_passengers_finished = True
        passengers_randomly_ordered = random.sample(self.passenger_list, len(self.passenger_list))
        for passenger in passengers_randomly_ordered:
            self.strat.update_passenger(passenger)
            if passenger.state != "finished": all_passengers_finished = False
        # if all passengers are finished, then this simulation is also
        if all_passengers_finished: self.finished = True
        self.time_elapsed += constants.tick_time
    def run(self):
        while self.time_elapsed < constants.sim_time_max and not self.finished:
            self.tick()
        return self.time_elapsed


## -- helper functions for disembarking strat class -- ##


# returns a 2-tuple; the second value is an index, and the first value is as follows:
# 1 if hall_interval is in hall_llist at that index, 2 if hall_interval can be inserted in hall_llist at that index,
# -1 if there is a (non-equal) interval at that index that intersects with hall_interval
def compare_hall_interval(hall_llist, hall_interval):
    if len(hall_llist) == 0:
        return (2, 0)
    
    # inclusive range of indices i for which hall_llist[i] might intersect with hall_interval
    possible_range = [0, len(hall_llist) - 1]
    
    count = 0
    count_max = len(hall_llist) + 2
    while count < count_max:
        count += 1
        
        # find the hall interval in the middle of the possible range
        mid_index = (possible_range[0] + possible_range[1]) // 2
        mid_interval = hall_llist[mid_index]
        
        # if hall_interval < mid_interval
        if hall_interval[1] < mid_interval[0]:
            if possible_range[0] == possible_range[1] or mid_index == possible_range[0]:
                return (2, mid_index)
            possible_range[1] = mid_index - 1
        # if hall_interval > mid_interval
        elif hall_interval[0] > mid_interval[1]:
            if possible_range[0] == possible_range[1]:
                return (2, mid_index + 1)
            possible_range[0] = mid_index + 1
        # if the intervals intersect
        else:
            if hall_interval == mid_interval: return (1, mid_index)
            else: return (-1, mid_index)
    print("exceeded max count in compare_hall_interval")
    exit(0)

# find if the given hall interval intersects an interval already on the hallway; if not, insert it in the right position
# since the hall intervals are ordered, this can be done more efficiently than the normal deque.find()
# returns 1 if hall interval is succesfully inserted, returns -1 if there is an intersection
def try_insert_hall_interval(hall_llist, hall_interval):
    val = compare_hall_interval(hall_llist, hall_interval)
    if val[0] == 1 or val[0] == -1: return -1
    hall_llist.insert(val[1], hall_interval)
    return 1

# try to replace interval_from with interval_to in hall_llist; returns 1 if succesful, -1 otherwise
# assumes that interval_to's left endpoint <= interval_from's left endpoint; same for right endpoints
# also assumes that the only possible intersection with interval_to is the interval immediately
#   before interval_from (in other words, don't make the parameters ridiculous,
#   like tick_time = 2 sec, or hall_interval_size = 0.1 in)
def try_move_hall_interval(hall_llist, interval_from, interval_to):
    # if the function is called properly, then we know interval_from is already there; we just want its index
    val = compare_hall_interval(hall_llist, interval_from)
    if val[1] == 0:
        hall_llist[0] = interval_to
        return 1
    if hall_llist[val[1] - 1][1] < interval_to[0]:
        hall_llist[val[1]] = interval_to
        return 1
    return -1


## -- default disembarking strat class, other strats inherit from this -- ##


class disembarking_strat:
    def __init__(self, passenger_list, seat_map, hall_llist):
        self.passenger_list = passenger_list
        self.seat_map = seat_map
        self.hall_llist = hall_llist
    def tick_update(self):
        pass
    def update_passenger(self, passenger):
        if passenger.state == "moving":
            passenger.move_time_remaining -= constants.tick_time
            # if done moving
            if passenger.move_time_remaining <= 0:
                # remove passenger from previous location (will always be a seat); update passenger's location
                self.seat_map[passenger.location] = None
                passenger.location = passenger.location_moving_to
                passenger.location_moving_to = None
                
                # if now on the hallway and need to grab carry-on bags, set the passenger's state accordingly
                if type(passenger.location) == list and passenger.carry_ons_left > 0:
                    passenger.state = "grabbing-carry-on"
                    passenger.carry_on_time_remaining = constants.carry_on_time
                else:
                    passenger.state = "default"
        elif passenger.state == "grabbing-carry-on":
            passenger.carry_on_time_remaining -= constants.tick_time
            # if done picking up carry-on
            if passenger.carry_on_time_remaining <= 0:
                passenger.carry_ons_left -= 1
                # if need to pick up another carry-on
                if passenger.carry_ons_left > 0:
                    passenger.carry_on_time_remaining = constants.carry_on_time
                else:
                    passenger.state = "default"
        # if passenger is not in the process of moving or unloading a carry-on, try to move to the next location
        elif passenger.state == "default":
            loc_current = passenger.location
            loc_next = None
            
            # determine type of current location (either a seat or hall interval)
            loc_current_type = "seat"
            if type(passenger.location) == list: loc_current_type = "hall"
            
            # determine type of next location (either a seat or a hall interval)
            loc_next_type = "hall"
            if loc_current_type == "seat":
                seat_letter = loc_current[-1]
                if seat_letter in ['A', 'B', 'E', 'F']:
                    loc_next_type = "seat"
            
            # determine next location
            if loc_next_type == "seat":
                letter_current = loc_current[-1]
                letter_next = 'B'
                if letter_current == 'B': letter_next = 'C'
                elif letter_current == 'E': letter_next = 'D'
                elif letter_current == 'F': letter_next = 'E'
                loc_next = loc_current[0:-1] + letter_next
            else:
                if loc_current_type == "seat":
                    hall_position = constants.row_to_hall_position( int(loc_current[0:-1]) )
                    loc_next = [hall_position - constants.hall_interval_size / 2, \
                                      hall_position + constants.hall_interval_size / 2]
                if loc_current_type == "hall":
                    distance_to_move = passenger.walkspeed * constants.tick_time
                    loc_next = [loc_current[0] - distance_to_move, loc_current[1] - distance_to_move]
            
            # if next location is not occupied, move to it (or start moving there if it takes time)
            if loc_next_type == "seat":
                if self.seat_map[loc_next] != None: return
                
                self.seat_map[loc_next] = passenger.p_id
                passenger.location_moving_to = loc_next
                passenger.state = "moving"
                passenger.move_time_remaining = constants.seat_move_time
            else:
                if loc_current_type == "seat":
                    val = try_insert_hall_interval(self.hall_llist, loc_next + [passenger.p_id])
                    if val == -1: return
                    passenger.location_moving_to = loc_next
                    passenger.state = "moving"
                    passenger.move_time_remaining = constants.seat_move_time
                else:
                    # if moving gets them to the exit, then the passenger is finished and removed from the hall
                    if loc_next[0] <= 0:
                        self.hall_llist.remove(passenger.location + [passenger.p_id])
                        passenger.location = None
                        passenger.state = "finished"
                        return
                    
                    # try moving from current hall interval to next
                    val = try_move_hall_interval(self.hall_llist, \
                        loc_current + [passenger.p_id], loc_next + [passenger.p_id])
                    if val == -1: return
                    passenger.location = loc_next
