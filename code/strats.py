import sys
import constants, base

# convert string to strat class, for example using the string "random_strat"
def str_to_class(st):
    return getattr(sys.modules[__name__], st)

class random_strat(base.disembarking_strat):
    pass

class seat_strat(base.disembarking_strat):
    def __init__(self, passenger_list, seat_map, hall_llist):
        super().__init__(passenger_list, seat_map, hall_llist)
        
        # map from passengers id's to letters, a passenger is mapped to the letter of the seat they are initially in
        self.p_to_letter_map = {}
        # map from letters to lists of passenger id's, a letter is mapped to a list of all passengers in its group
        self.letter_to_p_map = {}
        for letter in ['A', 'B', 'C', 'D', 'E', 'F']:
            self.letter_to_p_map[letter] = []
        for passenger in passenger_list:
            seat_letter = passenger.location[-1]
            self.p_to_letter_map[passenger.p_id] = seat_letter
            self.letter_to_p_map[seat_letter] += [passenger.p_id]
        
        # determines which passengers are allowed to move onto the hallway
        self.stage = ['C', 'D']
    def tick_update(self):
        if self.stage == ['A', 'B']: return
        
        passengers_allowed_to_move = self.letter_to_p_map[self.stage[0]] + \
            self.letter_to_p_map[self.stage[1]]
        all_finished = True
        for p_id in passengers_allowed_to_move:
            if self.passenger_list[p_id].state != "finished":
                all_finished = False
                break
        if all_finished:
            if self.stage == ['C', 'D']:
                self.stage = ['B', 'E']
            elif self.stage == ['B', 'E']:
                self.stage = ['A', 'F']
    def update_passenger(self, passenger):
        # if not in a seat, update
        if passenger.state == "finished" or type(passenger.location) == list:
            super().update_passenger(passenger)
            return
        
        starting_letter = self.p_to_letter_map[passenger.p_id]
        current_letter = passenger.location[-1]
        # don't allow compliant passengers to move onto hallway if they aren't in the group being called
        if starting_letter not in self.stage and current_letter in ['C', 'D'] and passenger.compliant:
            return
        
        super().update_passenger(passenger)

class row_strat(base.disembarking_strat):
    def __init__(self, passenger_list, seat_map, hall_llist):
        super().__init__(passenger_list, seat_map, hall_llist)
        # row_to_p_map is a list, where the element at index i is the list of passenger id's who started at row i
        self.row_to_p_map = []
        for i in range(constants.num_rows + 1):
            self.row_to_p_map += [[]]
        self.row_to_p_map[0] = None
        for passenger in passenger_list:
            seat_number = int(passenger.location[0:-1])
            self.row_to_p_map[seat_number] += [passenger.p_id]
        # which row of passengers is allowed to move; lower rows are also allowed to move
        self.stage = 1
    def tick_update(self):
        if self.stage >= constants.num_rows: return
        
        # if all passengers of current row are out of their seats, the next row can start moving
        all_out = True
        for p_id in self.row_to_p_map[self.stage]:
            passenger = self.passenger_list[p_id]
            if passenger.state != "finished":
                if type(passenger.location) == str:
                    all_out = False
                    break
        if all_out:
            self.stage += 1
    def update_passenger(self, passenger):
        # if (compliant) passenger is in a seat whose row is higher than allowed row, don't move
        if passenger.state != "finished" and passenger.compliant:
            if type(passenger.location) == str:
                row = int(passenger.location[0:-1])
                if row > self.stage:
                    return
        super().update_passenger(passenger)