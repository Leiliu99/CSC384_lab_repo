import sys
import heapq as hq
import copy
import time

#global variable to define types in battleship
empty = 0
water = 1
submarine = 2
middle = 3
left = 4
right = 5
top = 6
bottom = 7

out_bound = -1
ver_type_one = 1 #place from T vertically
ver_type_two = 2 #place from B vertically


encode_dict = {
    '0': 0,
    'W': 1,
    'S': 2,
    'M': 3,
    'L': 4,
    'R': 5,
    'T': 6,
    'B': 7
}

decode_dict = {
    0: '0',
    1: 'W',
    2: 'S',
    3: 'M',
    4: 'L',
    5: 'R',
    6: 'T',
    7: 'B'
}
ship_num = {# numbers represent the number of each ship type in order
    'S': 0,
    'D': 0,
    'C': 0,
    'B': 0
}
#ship_num = [] #1-4
#row and column constraint defined by input
official_row_constraint = []
official_col_constraint = []
puzzle_N = 0 #puzzle size should be N by N

int_puzzle = []
#to be deleted
#variable_queue = []
#{key: string of position, value: grid which includes 1. whether assigned 2. its domain}
variable_dict = {}

def debug_print(arr):
    decoded = []
    for i in range(puzzle_N):
        decoded.append([0] * puzzle_N)#initialize layout to all zeros first
    for i in range(puzzle_N):
        for j in range(puzzle_N):
            decoded[i][j] = decode_dict[arr[i][j]]
    for i in range(puzzle_N):
        print(decoded[i])

def debug_variable():
    print("******check variable queue******")
    for key, value in variable_dict.items():
        potential_list = []
        for potential in value.domain:
            potential_list.append(decode_dict[potential])
        print(key + ": " + str(potential_list))
        if not len(value.hint) == 0:
            print("hint exists in: " + str(value.hint))

def covert_output(output_board):
    string_arr = []
    for row in output_board:
        string_row = ''
        for encoded_element in row:
            string_row += decode_dict[encoded_element]
        string_arr.append(string_row)
    return string_arr

def write_out(output_file, string_board):
    with open(output_file, 'a') as f:
        f.truncate(0)
        if not len(string_board) == 0:
            for string_row in string_board:
                f.write(string_row)
                f.write('\n')

def safe_palce(item, position_i, position_j, board_arr):
    # place item (int) into the board array's corresponding position
    # board here is a reference!
    if 0 <= position_i < puzzle_N and 0 <= position_j < puzzle_N:
        board_arr[position_i][position_j] = item
    #if position given is not within bound, we simply do nothing

def safe_check(position_i, position_j, board_arr):
    # return item (int) into the board array's corresponding position
    # board here is a reference!
    if 0 <= position_i < puzzle_N and 0 <= position_j < puzzle_N:
        return board_arr[position_i][position_j]
    else:
        return out_bound

def within_bound(position):
    return 0 <= position[0] < puzzle_N and 0 <= position[1] < puzzle_N

def analyze_input(input_arr):
    global puzzle_N
    global official_row_constraint
    global official_col_constraint
    global ship_num
    global int_puzzle

    str_puzzle = []
    ship_list = []
    input_parse = 0
    puzzle_N = len(input_arr[0])
    for str_row in input_arr:
        if input_parse == 0:# row constraint
            for i in range(puzzle_N):
                official_row_constraint.append(int(str_row[i]))
        elif input_parse == 1: #col constraint
            for j in range(puzzle_N):
                official_col_constraint.append(int(str_row[j]))
        elif input_parse == 2: #ship num
            for k in range(len(str_row)):
                ship_list.append(int(str_row[k]))
        else: #string puzzle layout
            str_puzzle.append(str_row)
            #append them into an array as string
        input_parse += 1

    for i in range(len(ship_list)):
        if i == 0:
            ship_num['S'] = ship_list[i]
        elif i == 1:
            ship_num['D'] = ship_list[i]
        elif i == 2:
            ship_num['C'] = ship_list[i]
        elif i == 3:
            ship_num['B'] = ship_list[i]
        else:
            print("------Error in preparing ship dict------")

    #encode puzzle layout to integer
    #note: we will change some values while encoding since following constraints are obvious
    #before search begin.
    for i in range(puzzle_N):
        int_puzzle.append([0] * puzzle_N)#initialize layout to all zeros first
    #encoding: string to int
    for i in range(puzzle_N):
        for j in range(puzzle_N):
            type = str_puzzle[i][j]
            int_puzzle[i][j] = encode_dict[type]
            # if hint is S, we could update row/con constraint, ship num right away
            if type == 'S':
                official_row_constraint[i] -= 1
                official_col_constraint[j] -= 1
                ship_num['S'] -= 1
            elif type == 'T' or type == 'B':
                official_row_constraint[i] -= 1
            elif type == 'L' or type == 'R':
                official_col_constraint[j] -= 1

    #constraint situation 1: when 0 shows in row/col constraints, means this row/col should be filled with ALL water
    for i in range(puzzle_N):
        if official_row_constraint[i] == 0:
            for k in range(puzzle_N):
                if int_puzzle[i][k] == empty:
                    int_puzzle[i][k] = water
    for k in range(puzzle_N):
        if official_col_constraint[k] == 0:
            for i in range(puzzle_N):
                if int_puzzle[i][k] == empty:
                    int_puzzle[i][k] = water

    # constraint situation 2: for ship/ or partial ship in the hint, water should be around
    for i in range(puzzle_N):
        for j in range(puzzle_N):
            if int_puzzle[i][j] == submarine:
                safe_palce(water, i - 1, j - 1, int_puzzle)
                safe_palce(water, i - 1, j, int_puzzle)
                safe_palce(water, i - 1, j + 1, int_puzzle)
                safe_palce(water, i, j - 1, int_puzzle)
                safe_palce(water, i, j + 1, int_puzzle)
                safe_palce(water, i + 1, j - 1, int_puzzle)
                safe_palce(water, i + 1, j, int_puzzle)
                safe_palce(water, i + 1, j + 1, int_puzzle)
            elif int_puzzle[i][j] == left:
                safe_palce(water, i - 1, j - 1, int_puzzle)
                safe_palce(water, i - 1, j, int_puzzle)
                safe_palce(water, i - 1, j + 1, int_puzzle)
                safe_palce(water, i - 1, j + 2, int_puzzle)
                safe_palce(water, i, j - 1, int_puzzle)
                safe_palce(water, i + 1, j - 1, int_puzzle)
                safe_palce(water, i + 1, j, int_puzzle)
                safe_palce(water, i + 1, j + 1, int_puzzle)
                safe_palce(water, i + 1, j + 2, int_puzzle)
            elif int_puzzle[i][j] == right:
                safe_palce(water, i - 1, j - 2, int_puzzle)
                safe_palce(water, i - 1, j - 1, int_puzzle)
                safe_palce(water, i - 1, j, int_puzzle)
                safe_palce(water, i - 1, j + 1, int_puzzle)
                safe_palce(water, i, j + 1, int_puzzle)
                safe_palce(water, i + 1, j - 2, int_puzzle)
                safe_palce(water, i + 1, j - 1, int_puzzle)
                safe_palce(water, i + 1, j, int_puzzle)
                safe_palce(water, i + 1, j + 1, int_puzzle)
            elif int_puzzle[i][j] == top:
                safe_palce(water, i - 1, j - 1, int_puzzle)
                safe_palce(water, i - 1, j, int_puzzle)
                safe_palce(water, i - 1, j + 1, int_puzzle)
                safe_palce(water, i, j - 1, int_puzzle)
                safe_palce(water, i, j + 1, int_puzzle)
                safe_palce(water, i + 1, j - 1, int_puzzle)
                safe_palce(water, i + 1, j + 1, int_puzzle)
                safe_palce(water, i + 2, j - 1, int_puzzle)
                safe_palce(water, i + 2, j + 1, int_puzzle)
            elif int_puzzle[i][j] == bottom:
                safe_palce(water, i - 2, j - 1, int_puzzle)
                safe_palce(water, i - 2, j + 1, int_puzzle)
                safe_palce(water, i - 1, j - 1, int_puzzle)
                safe_palce(water, i - 1, j + 1, int_puzzle)
                safe_palce(water, i, j - 1, int_puzzle)
                safe_palce(water, i, j + 1, int_puzzle)
                safe_palce(water, i + 1, j - 1, int_puzzle)
                safe_palce(water, i + 1, j, int_puzzle)
                safe_palce(water, i + 1, j + 1, int_puzzle)
            elif int_puzzle[i][j] == middle:
                safe_palce(water, i - 1, j - 1, int_puzzle)
                safe_palce(water, i - 1, j + 1, int_puzzle)
                safe_palce(water, i + 1, j - 1, int_puzzle)
                safe_palce(water, i + 1, j + 1, int_puzzle)

    # print("----check input conversion-----")
    # print(official_row_constraint)
    # print(official_col_constraint)
    # print(ship_num)
    # debug_print(int_puzzle)
    # print("-----------------------------")

    input_state = PuzzleState(int_puzzle, official_row_constraint, official_col_constraint, ship_num, True)
    return input_state

def prepare_variable():
    #global variable_queue
    global variable_dict
    for i in range(puzzle_N):
        for j in range(puzzle_N):
            domain = []
            hint = []
            if int_puzzle[i][j] == empty:
                if safe_check(i - 1, j, int_puzzle) == top or safe_check(i - 1, j, int_puzzle) == middle:
                    domain.extend([bottom, middle])
                    hint.extend([i - 1, j])
                elif safe_check(i + 1, j, int_puzzle) == bottom or safe_check(i + 1, j, int_puzzle) == middle:
                    domain.extend([top, middle])
                    hint.extend([i + 1, j])
                elif safe_check(i, j - 1, int_puzzle) == left or safe_check(i, j - 1, int_puzzle) == middle:
                    domain.extend([right, middle])
                    hint.extend([i, j - 1])
                elif safe_check(i, j + 1, int_puzzle) == right or safe_check(i, j + 1, int_puzzle) == middle:
                    domain.extend([left, middle])
                    hint.extend([i, j + 1])
                else:
                    if i == 0:
                        if j == 0:
                            domain.extend([water, submarine, top, left])
                        elif j == puzzle_N - 1:
                            domain.extend([water, submarine, top, right])
                        else:
                            domain.extend([water, submarine, middle, top, left, right])
                    elif i == puzzle_N - 1:
                        if j == 0:
                            domain.extend([water, submarine, bottom, left])
                        elif j == puzzle_N - 1:
                            domain.extend([water, submarine, bottom, right])
                        else:
                            domain.extend([water, submarine, middle, bottom, left, right])
                    elif j == 0:
                        domain.extend([water, submarine, middle, top, bottom, left])
                    elif j == puzzle_N - 1:
                        domain.extend([water, submarine, middle, top, bottom, right])
                    else:
                        domain.extend([water, submarine, middle, top, bottom, left, right])

                grid = GridVariable(False, [i, j], domain, hint)
                #hq.heappush(variable_queue, grid)
                variable_dict[str([i, j])] = grid
            else:
                continue

def all_assgined(test_dict):
    for key, value in test_dict.items():
        if not value.assigned:
            return False
    return True

def all_cleaned(ship_dict):
    tobe_fill = 0
    for key, value in ship_dict.items():
        if not value == 0:
            if key == 'S':
                tobe_fill += value
            elif key == 'D':
                tobe_fill += value * 2
            elif key == 'C':
                tobe_fill += value * 3
            else:
                tobe_fill += value * 4
    return tobe_fill

def check_ver(variable, state, position, width, type):
    if width == 4:
        boat = 'B'
    elif width == 3:
        boat = 'C'
    elif width == 2:
        boat = 'D'
    else:
        print("------Error in handling width!------")

    if type == ver_type_one: #place from T
        #check row constraints and place T, M or B
        for offset in range(width):
            if not state.puzzle_arr[position[0] + offset][position[1]] == empty:
                if offset == 0:
                    if not state.puzzle_arr[position[0] + offset][position[1]] == top:
                        return False
                    else:
                        continue
                elif offset == width - 1:
                    if not state.puzzle_arr[position[0] + offset][position[1]] == bottom:
                        return False
                    else:
                        continue
                elif not state.puzzle_arr[position[0] + offset][position[1]] == middle:
                    return False
                else:
                    if state.puzzle_arr[position[0] + offset][position[1]] == middle:
                        state.curr_row_con[position[0] + offset] -= 1 #we do not deduct middle's row constraint
                    continue
            if state.curr_row_con[position[0] + offset] == 0:
                return False  # no vacancy in row
            #position is empty and row constraint good
            if offset == 0:
                state.puzzle_arr[position[0] + offset][position[1]] = top
                variable.pop(str([position[0] + offset, position[1]]))
            elif offset == width - 1:
                state.puzzle_arr[position[0] + offset][position[1]] = bottom
                variable.pop(str([position[0] + offset, position[1]]))
            else:
                state.puzzle_arr[position[0] + offset][position[1]] = middle
                variable.pop(str([position[0] + offset, position[1]]))
            #update row constraint
            state.curr_row_con[position[0] + offset] -= 1

        #check surroundings and place water
        for row_off in range(-1, width + 1):
            for col_off in range(-1, 2):
                if col_off == 0 and not row_off == -1 and not row_off == width:
                    continue#already placed
                check_pos = [position[0] + row_off, position[1] + col_off]
                if within_bound(check_pos):
                    if state.puzzle_arr[check_pos[0]][check_pos[1]] > 1:
                        return False
                    if state.puzzle_arr[check_pos[0]][check_pos[1]] == empty:
                        state.puzzle_arr[check_pos[0]][check_pos[1]] = water
                        variable.pop(str(check_pos))# remove assigned from variable list
        # update col constraints
        state.curr_col_con[position[1]] -= width
        # update ship
        state.ship_list[boat] -= 1

    elif type == ver_type_two: #place from B

        # check row constraints and place B, M or T
        for offset in range(width):
            if not state.puzzle_arr[position[0] - offset][position[1]] == empty:
                if offset == 0:
                    if not state.puzzle_arr[position[0] - offset][position[1]] == bottom:
                        return False
                    else:
                        continue
                elif offset == width - 1:
                    if not state.puzzle_arr[position[0] - offset][position[1]] == top:
                        return False
                    else:
                        continue
                elif not state.puzzle_arr[position[0] - offset][position[1]] == middle:
                    return False
                else:
                    if state.puzzle_arr[position[0] - offset][position[1]] == middle:
                        state.curr_row_con[position[0] - offset] -= 1 #we do not deduct middle's row constraint
                    continue
            if state.curr_row_con[position[0] - offset] == 0:
                return False  # no vacancy in row
            #position is empty and row constraint good
            if offset == 0:
                state.puzzle_arr[position[0] - offset][position[1]] = bottom
                variable.pop(str([position[0] - offset, position[1]]))
            elif offset == width - 1:
                state.puzzle_arr[position[0] - offset][position[1]] = top
                variable.pop(str([position[0] - offset, position[1]]))
            else:
                state.puzzle_arr[position[0] - offset][position[1]] = middle
                variable.pop(str([position[0] - offset, position[1]]))
            #update row constraint
            state.curr_row_con[position[0] - offset] -= 1

        # check surroundings and place water
        for row_off in range(-1, width + 1):
            for col_off in range(-1, 2):
                if col_off == 0 and not row_off == -1 and not row_off == width:
                    continue
                check_pos = [position[0] - row_off, position[1] + col_off]
                if within_bound(check_pos):
                    if state.puzzle_arr[check_pos[0]][check_pos[1]] > 1:
                        return False
                    if state.puzzle_arr[check_pos[0]][check_pos[1]] == empty:
                        state.puzzle_arr[check_pos[0]][check_pos[1]] = water
                        variable.pop(str(check_pos))  # remove assigned from variable list
        # update col constraints
        state.curr_col_con[position[1]] -= width
        # update ship
        state.ship_list[boat] -= 1
    else:
        print("------Error in vertical type!------")

    # place all empty grid of this col/row to water if constraint down to zero
    water_list = []
    for position, var in variable.items():
        row = var.position[0]
        col = var.position[1]
        if state.curr_row_con[row] == 0:
            state.puzzle_arr[row][col] = water
            water_list.append(str([row, col]))
        elif state.curr_col_con[col] == 0:
            state.puzzle_arr[row][col] = water
            water_list.append(str([row, col]))
    for i in range(len(water_list)):
        variable.pop(water_list[i])

    return True

def check_hor(variable, state, position, width):
    if width == 4:
        boat = 'B'
    elif width == 3:
        boat = 'C'
    elif width == 2:
        boat = 'D'
    else:
        print("------Error in handling width!------")

    # check row constraints and place L, M or R
    for offset in range(width):
        row = position[0]
        col = position[1] + offset
        if not state.puzzle_arr[row][col] == empty:
            if offset == 0:
                if not state.puzzle_arr[row][col] == left:
                    return False
                else:
                    continue
            elif offset == width - 1:
                if not state.puzzle_arr[row][col] == right:
                    return False
                else:
                    continue
            elif not state.puzzle_arr[row][col] == middle:
                return False
            else:
                if state.puzzle_arr[row][col] == middle:
                    state.curr_col_con[col] -= 1  # we do not deduct middle's col constraint
                continue
        if state.curr_col_con[col] == 0:
            return False  # no vacancy in col
        # position is empty and row constraint good
        if offset == 0:
            state.puzzle_arr[row][col] = left
            variable.pop(str([row, col]))
        elif offset == width - 1:
            state.puzzle_arr[row][col] = right
            variable.pop(str([row, col]))
        else:
            state.puzzle_arr[row][col] = middle
            variable.pop(str([row, col]))
        # update col constraint
        state.curr_col_con[col] -= 1

    # check surroundings and place water
    for col_off in range(-1, width + 1):
        for row_off in range(-1, 2):
            if row_off == 0 and not col_off == -1 and not col_off == width:
                continue
            check_pos = [position[0] + row_off, position[1] + col_off]
            if within_bound(check_pos):
                if state.puzzle_arr[check_pos[0]][check_pos[1]] > 1:
                    return False
                if state.puzzle_arr[check_pos[0]][check_pos[1]] == empty:
                    state.puzzle_arr[check_pos[0]][check_pos[1]] = water
                    variable.pop(str(check_pos))  # remove assigned from variable list
    # update row constraints
    state.curr_row_con[position[0]] -= width
    # update ship
    state.ship_list[boat] -= 1

    # place all empty grid of this col/row to water if constraint down to zero
    water_list = []
    for position, var in variable.items():
        row = var.position[0]
        col = var.position[1]
        if state.curr_row_con[row] == 0:
            state.puzzle_arr[row][col] = water
            water_list.append(str([row, col]))
        elif state.curr_col_con[col] == 0:
            state.puzzle_arr[row][col] = water
            water_list.append(str([row, col]))
    for i in range(len(water_list)):
        variable.pop(water_list[i])

    return True

def check_submarine(variable, state, position):
    if not state.puzzle_arr[position[0]][position[1]] == empty:
        if not state.puzzle_arr[position[0]][position[1]] > submarine:#not empty, water not submarine
            return False
    for row_off in range(-1,2):
        for col_off in range(-1, 2):
            if row_off == 0 and col_off == 0:
                continue
            check_pos = [position[0] + row_off, position[1] + col_off]
            if within_bound(check_pos):
                if state.puzzle_arr[check_pos[0]][check_pos[1]] > 1:
                    return False
                if state.puzzle_arr[check_pos[0]][check_pos[1]] == empty:
                    state.puzzle_arr[check_pos[0]][check_pos[1]] = water
                    variable.pop(str(check_pos))  # remove assigned from variable list
    #place submarine
    state.puzzle_arr[position[0]][position[1]] = submarine
    variable.pop(str(position))
    # update row/col constraints
    state.curr_row_con[position[0]] -= 1
    state.curr_col_con[position[1]] -= 1
    # update ship
    state.ship_list['S'] -= 1

    # place all empty grid of this col/row to water if constraint down to zero
    water_list = []
    for position, var in variable.items():
        row = var.position[0]
        col = var.position[1]
        if state.curr_row_con[row] == 0:
            state.puzzle_arr[row][col] = water
            water_list.append(str([row, col]))
        elif state.curr_col_con[col] == 0:
            state.puzzle_arr[row][col] = water
            water_list.append(str([row, col]))
    for i in range(len(water_list)):
        variable.pop(water_list[i])

    return True

def search(unassigned_dict, puzzle_state):
    #puzzle_state.debug_puzzle()

    if len(unassigned_dict) == 0 or all_assgined(unassigned_dict):
        if all_cleaned(puzzle_state.ship_list) == 0:
            print("Hit base case!")
            return puzzle_state
        else:
            puzzle_state.satisfied = False
            return puzzle_state
    if all_cleaned(puzzle_state.ship_list) > len(unassigned_dict):
        #print("** To be filled greater than # of empty grids")
        puzzle_state.satisfied = False
        return puzzle_state

    unassigned_row = []
    unassigned_col = []
    unassigned_row.extend([0] * puzzle_N)  # initialize layout to all zeros first
    unassigned_col.extend([0] * puzzle_N)  # initialize layout to all zeros first
    for pos, var in unassigned_dict.items():
        unassigned_row[var.position[0]] += 1
        unassigned_col[var.position[1]] += 1
    for i in range(puzzle_N):
        if unassigned_row[i] < puzzle_state.curr_row_con[i]:# empty cells less than the constraint required ??
            #print("** row constraint not satisfied")
            puzzle_state.satisfied = False
            return puzzle_state
        if unassigned_col[i] < puzzle_state.curr_col_con[i]:
            #print("** col constraint not satisfied")
            puzzle_state.satisfied = False
            return puzzle_state

    curr_puzzle = puzzle_state.puzzle_arr
    cur_rowcon = puzzle_state.curr_row_con
    cur_colcon = puzzle_state.curr_col_con
    cur_ship = puzzle_state.ship_list

    sort_grid = sorted(unassigned_dict.items(), key=lambda x: len(x[1].domain))  # MRV

    # for k in range(len(sort_grid)):
    top_grid = sort_grid[0]
    grid_domain = top_grid[1].domain
    len_domain = len(grid_domain)
    row = top_grid[1].position[0]
    col = top_grid[1].position[1]

    for i in range(len_domain - 1, -1, -1):#try filling with directions first
        value = grid_domain[i]
        #print("examing: " + decode_dict[value] + " at position: " + top_grid[0])
        if cur_rowcon[row] == 0 or cur_colcon[col] == 0:#TODO: add if only
            if not i == len_domain - 1:
                #print("Already examined, hard place water")
                break
            try_variable = copy.deepcopy(unassigned_dict)
            # mark it as assigned
            try_variable[top_grid[0]].assigned = True

            try_state = copy.deepcopy(puzzle_state)
            try_state.puzzle_arr[row][col] = water
            try_variable.pop(top_grid[0])
            #mark all water!
            if cur_rowcon[row] == 0:
                for t in range(puzzle_N):
                    if try_state.puzzle_arr[row][t] == empty:
                        try_state.puzzle_arr[row][t] = water
                        try_variable.pop(str([row, t]))
            if cur_colcon[col] == 0:
                for p in range(puzzle_N):
                    if try_state.puzzle_arr[p][col] == empty:
                        try_state.puzzle_arr[p][col] = water
                        try_variable.pop(str([p, col]))

            test_result = search(try_variable, try_state)
            if test_result.satisfied:
                return test_result
        elif value == middle:
            if cur_ship['C'] == 0 and cur_ship['B'] == 0:
                continue# never reached?
            if len(top_grid[1].hint) == 0:
                #print("*****Potential is middle but no hint, skip currently...****")
                continue

            hint_position = top_grid[1].hint
            if curr_puzzle[hint_position[0]][hint_position[1]] == top or \
                curr_puzzle[hint_position[0]][hint_position[1]] == bottom:
                if curr_puzzle[hint_position[0]][hint_position[1]] == top:
                    if not hint_position == [row - 1, col]:
                        print("------Error in checking vertical, no T given!------")
                        continue
                    start_position = [row - 1, col]
                    bound_one = [row + 1, col]
                    bound_two = [row + 2, col]
                    check = ver_type_one
                else:
                    if not hint_position == [row + 1, col]:
                        print("------Error in checking vertical, no B given!------")
                        continue
                    start_position = [row + 1, col]
                    bound_one = [row - 1, col]
                    bound_two = [row - 2, col]
                    check = ver_type_two

                if not cur_ship['B'] == 0 and cur_colcon[col] >= 4: # place size of 4
                    if within_bound(bound_two):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        if check_ver(try_variable, try_state, start_position, 4, check):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result
                if not cur_ship['C'] == 0 and cur_colcon[col] >= 3:  # place size of 3
                    if within_bound(bound_one):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        if check_ver(try_variable, try_state, start_position, 3, check):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result

            elif curr_puzzle[hint_position[0]][hint_position[1]] == middle:
                if cur_ship['B'] == 0: #no 4-size ship
                    continue
                if hint_position == [row - 1, col] and cur_colcon[col] >= 4:
                    if within_bound([row - 2, col]) and within_bound([row + 1, col]):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        #try_state.curr_row_con[row - 1] -= 1 #TODO
                        if check_ver(try_variable, try_state, [row - 2, col], 4, ver_type_one):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result
                elif hint_position == [row + 1, col] and cur_colcon[col] >= 4:
                    if within_bound([row - 1, col]) and within_bound([row + 2, col]):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        #try_state.curr_row_con[row + 1] -= 1  # TODO
                        if check_ver(try_variable, try_state, [row - 1, col], 4, ver_type_one):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result
                elif hint_position == [row, col - 1] and cur_rowcon[row] >= 4:
                    if within_bound([row, col - 2]) and within_bound([row, col + 1]):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        if check_hor(try_variable, try_state, [row, col - 2], 4):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result
                elif hint_position == [row, col + 1] and cur_rowcon[row] >= 4:
                    if within_bound([row, col - 1]) and within_bound([row, col + 2]):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        if check_hor(try_variable, try_state, [row, col - 1], 4):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result

            elif curr_puzzle[hint_position[0]][hint_position[1]] == left or \
                curr_puzzle[hint_position[0]][hint_position[1]] == right:
                if curr_puzzle[hint_position[0]][hint_position[1]] == left:
                    if not hint_position == [row, col - 1]:
                        print("------Error in checking vertical, no L given!------")
                        continue
                    start_position = [row, col - 1]
                    bound_one = [row, col + 1]
                    bound_two = [row, col + 2]
                else:
                    if not hint_position == [row, col + 1]:
                        print("------Error in checking vertical, no R given!------")
                        continue
                    start_position = [row, col - 2] #change for C!!
                    bound_one = [row, col - 1]
                    bound_two = [row, col - 2]

                if not cur_ship['B'] == 0 and cur_rowcon[row] >= 4: # place size of 4
                    if within_bound(bound_two):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        if check_hor(try_variable, try_state, start_position, 4):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result
                if not cur_ship['C'] == 0 and cur_rowcon[row] >= 3: # place size of 3
                    if within_bound(bound_one):
                        try_variable = copy.deepcopy(unassigned_dict)
                        # mark it as assigned
                        try_variable[top_grid[0]].assigned = True
                        try_state = copy.deepcopy(puzzle_state)
                        if curr_puzzle[hint_position[0]][hint_position[1]] == right:
                            start_position = [row, col - 1]
                        if check_hor(try_variable, try_state, start_position, 3):
                            test_result = search(try_variable, try_state)
                            if test_result.satisfied:
                                return test_result

        elif value == top or value == bottom:
            if value == top:
                bound_three = [row + 3, col]
                bound_two = [row + 2, col]
                bound_one = [row + 1, col]
                check = ver_type_two
            else:
                bound_three = [row - 3, col]
                bound_two = [row - 2, col]
                bound_one = [row - 1, col]
                check = ver_type_one
            if not cur_ship['B'] == 0 and cur_colcon[col] >= 4:  # place size of 4
                if within_bound(bound_three):
                    try_variable = copy.deepcopy(unassigned_dict)
                    # mark it as assigned
                    try_variable[top_grid[0]].assigned = True
                    try_state = copy.deepcopy(puzzle_state)
                    if check_ver(try_variable, try_state, bound_three, 4, check):
                        test_result = search(try_variable, try_state)
                        if test_result.satisfied:
                            return test_result
            if not cur_ship['C'] == 0 and cur_colcon[col] >= 3:  # place size of 3
                if within_bound(bound_two):
                    try_variable = copy.deepcopy(unassigned_dict)
                    # mark it as assigned
                    try_variable[top_grid[0]].assigned = True
                    try_state = copy.deepcopy(puzzle_state)
                    if check_ver(try_variable, try_state, bound_two, 3, check):
                        test_result = search(try_variable, try_state)
                        if test_result.satisfied:
                            return test_result
            if not cur_ship['D'] == 0 and cur_colcon[col] >= 2:  # place size of 2
                if within_bound(bound_one):
                    try_variable = copy.deepcopy(unassigned_dict)
                    # mark it as assigned
                    try_variable[top_grid[0]].assigned = True
                    try_state = copy.deepcopy(puzzle_state)
                    if check_ver(try_variable, try_state, bound_one, 2, check):
                        test_result = search(try_variable, try_state)
                        if test_result.satisfied:
                            return test_result

        elif value == left or value == right:
            if value == left:
                bound_three = [row, col + 3]
                bound_two = [row, col + 2]
                bound_one = [row, col + 1]
                start_position = [row, col]
            else:
                bound_three = [row, col - 3]
                bound_two = [row, col - 2]
                bound_one = [row, col - 1]
                start_position = [row, col - 3] #WILL CHANGE BY SHIP!!
            if not cur_ship['B'] == 0 and cur_rowcon[row] >= 4: # place size of 4
                if within_bound(bound_three):
                    try_variable = copy.deepcopy(unassigned_dict)
                    # mark it as assigned
                    try_variable[top_grid[0]].assigned = True
                    try_state = copy.deepcopy(puzzle_state)
                    if check_hor(try_variable, try_state, start_position, 4):
                        test_result = search(try_variable, try_state)
                        if test_result.satisfied:
                            return test_result
            if not cur_ship['C'] == 0 and cur_rowcon[row] >= 3: # place size of 3
                if within_bound(bound_two):
                    try_variable = copy.deepcopy(unassigned_dict)
                    # mark it as assigned
                    try_variable[top_grid[0]].assigned = True
                    try_state = copy.deepcopy(puzzle_state)
                    if value == right:
                        start_position = [row, col - 2]
                    if check_hor(try_variable, try_state, start_position, 3):
                        test_result = search(try_variable, try_state)
                        if test_result.satisfied:
                            return test_result
            if not cur_ship['D'] == 0 and cur_rowcon[row] >= 2: # place size of 2
                if within_bound(bound_one):
                    try_variable = copy.deepcopy(unassigned_dict)
                    # mark it as assigned
                    try_variable[top_grid[0]].assigned = True
                    try_state = copy.deepcopy(puzzle_state)
                    if value == right:
                        start_position = [row, col - 1]
                    if check_hor(try_variable, try_state, start_position, 2):
                        test_result = search(try_variable, try_state)
                        if test_result.satisfied:
                            return test_result

        elif value == submarine:
            if cur_ship['S'] == 0:
                continue
            if cur_rowcon[row] >= 1 and cur_colcon[col] >= 1:
                try_variable = copy.deepcopy(unassigned_dict)
                # mark it as assigned
                try_variable[top_grid[0]].assigned = True
                try_state = copy.deepcopy(puzzle_state)
                if check_submarine(try_variable, try_state, [row, col]):
                    test_result = search(try_variable, try_state)
                    if test_result.satisfied:
                        return test_result
        elif value == water:
            try_variable = copy.deepcopy(unassigned_dict)
            # mark it as assigned
            try_variable[top_grid[0]].assigned = True
            try_state = copy.deepcopy(puzzle_state)
            try_state.puzzle_arr[row][col] = water
            try_variable.pop(top_grid[0])

            test_result = search(try_variable, try_state)
            if test_result.satisfied:
                return test_result
        else:
            print("------Error in value in domain!------")

    #print("and then here? means not satisfied")
    puzzle_state.satisfied = False
    return puzzle_state

class PuzzleState:

    def __init__(self, puzzle_arr, curr_row_con, curr_col_con, ship_list, satisfied):
        self.puzzle_arr = puzzle_arr
        self.curr_row_con = curr_row_con
        self.curr_col_con = curr_col_con
        self.ship_list = ship_list
        self.satisfied = satisfied

    def debug_puzzle(self):
        print("----check this puzzle-----")
        print(self.curr_row_con)
        print(self.curr_col_con)
        print(self.ship_list)
        debug_print(self.puzzle_arr)
        print("-----------------------------")

class GridVariable:

    def __init__(self, assigned, position, domain, hint):
        self.assigned = assigned
        self.position = position
        self.domain = domain
        #hint is used for grid that has T/B?L/R/M hint around
        self.hint = hint

if __name__ == "__main__":
    start = time.time()
    input_file = open(sys.argv[1], 'r')
    input_string = input_file.read()
    input_file.close()
    mediate_arr = input_string.split("\n")

    initial_state = analyze_input(mediate_arr)
    prepare_variable()
    #debug_variable()
    final_state = search(variable_dict, initial_state)

    write_out(sys.argv[2], covert_output(final_state.puzzle_arr))

    # end = time.time()
    # time_used = end - start
    # print("Time in sec:", time_used)
    # print("---------solution---------")
    # final_state.debug_puzzle()