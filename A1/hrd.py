import sys
import heapq as hq
import copy

TWO_BY_TWO = 1
ONE_BY_ONE = 4
ONE_BY_TWO_HOR = 2
ONE_BY_TWO_VER = 3

def write_out(list, cost, output_file):
    with open(output_file, 'a') as f:
        f.truncate(0)
        f.write('Cost of the solution: ' + str(cost) + '\n')
        for i, moves in enumerate(list):
            for j, line in enumerate(moves):
                f.write(''.join([str(item) for item in line]))
                if not (i == len(list) - 1 and j == len(moves) - 1):
                    f.write('\n')
            f.write('\n')

def recognize_positions(current_puzzle):
#given a puzzle array, return a dictionary that contains{element_integer: [top-left position, (horizontal or vertical)]}
    block_dict = {7: []}
    found_two_by_two = False
    for i, rows in enumerate(current_puzzle):
        for j, element in enumerate(rows):
            if element == 0:
                continue
            if element == 1:
                if not found_two_by_two:
                    block_dict[1] = [i, j]
                    found_two_by_two = True
                else:
                    continue
            elif element == 7:
                block_dict[7].append([i, j])
            elif (i != len(current_puzzle) - 1) and current_puzzle[i][j] == current_puzzle[i + 1][j]:
                block_dict[current_puzzle[i][j]] = [[i, j], ONE_BY_TWO_VER]
            elif (j != len(rows) - 1) and current_puzzle[i][j] == current_puzzle[i][j + 1]:
                block_dict[current_puzzle[i][j]] = [[i, j], ONE_BY_TWO_HOR]
    return block_dict

def calculate_heuristic(position):
    #for now:use manhattan
    return abs(3 - position[0]) + abs(1 - position[1])

def within_bound(position):
    return 0 <= position[0] <= 4 and 0 <= position[1] <= 3


def check_move(type, position, current_puzzle, possible_moves):
    hor_width = 0
    ver_width = 0
    if type == ONE_BY_ONE:
        hor_width = 1
        ver_width = 1
    elif type == ONE_BY_TWO_HOR:
        hor_width = 2
        ver_width = 1
    elif type == TWO_BY_TWO:
        hor_width = 2
        ver_width = 2
    elif type == ONE_BY_TWO_VER:
        hor_width = 1
        ver_width = 2

    #up
    found_up = True
    for check_time in range(hor_width):
        if not within_bound([position[0] - 1, position[1] + check_time]):
            found_up = False
            break
        if not current_puzzle[position[0] - 1][position[1] + check_time] == 0:
            found_up = False
            break
    if found_up:
        after_move = copy.deepcopy(current_puzzle) # we need shallow deepcopy to not modify the original content in puzzle
        for move_time_ver in range(ver_width):
            for move_time in range(hor_width):
                after_move[position[0] - 1 + move_time_ver][position[1] + move_time] \
                    = current_puzzle[position[0] + move_time_ver][position[1] + move_time]
                after_move[position[0] + move_time_ver][position[1] + move_time] = 0
        possible_moves.append(after_move)

    #down
    found_down = True
    for check_time in range(hor_width):
        if not within_bound([position[0] + ver_width, position[1] + check_time]):
            found_down = False
            break
        if not current_puzzle[position[0] + ver_width][position[1] + check_time] == 0:
            found_down = False
            break
    if found_down:
        after_move = copy.deepcopy(current_puzzle)
        for move_time_ver in range(ver_width - 1, -1, -1):
            for move_time in range(hor_width):
                after_move[position[0] + 1 + move_time_ver][position[1] + move_time] \
                    = current_puzzle[position[0] + move_time_ver][position[1] + move_time]
                after_move[position[0] + move_time_ver][position[1] + move_time] = 0
        possible_moves.append(after_move)

    # left
    found_left = True
    for check_time in range(ver_width):
        if not within_bound([position[0] + check_time, position[1] - 1]):
            found_left = False
            break
        if not current_puzzle[position[0] + check_time][position[1] - 1] == 0:
            found_left = False
            break
    if found_left:
        after_move = copy.deepcopy(current_puzzle)
        for move_time in range(hor_width):
            for move_time_ver in range(ver_width):
                after_move[position[0] + move_time_ver][position[1] - 1 + move_time] \
                    = current_puzzle[position[0] + move_time_ver][position[1] + move_time]
                after_move[position[0] + move_time_ver][position[1] + move_time] = 0
        possible_moves.append(after_move)

    # right
    found_right = True
    for check_time in range(ver_width):
        if not within_bound([position[0] + check_time, position[1] + hor_width]):
            found_right = False
            break
        if not current_puzzle[position[0] + check_time][position[1] + hor_width] == 0:
            found_right = False
            break
    if found_right:
        after_move = copy.deepcopy(current_puzzle)
        for move_time in range(hor_width - 1, -1, -1):
            for move_time_ver in range(ver_width):
                after_move[position[0] + move_time_ver][position[1] + 1 + move_time] \
                    = current_puzzle[position[0] + move_time_ver][position[1] + move_time]
                after_move[position[0] + move_time_ver][position[1] + move_time] = 0
        possible_moves.append(after_move)



class PuzzleState:

    def __init__(self, puzzle_arr, move):
        self.state_arr = puzzle_arr
        self.block_dict = recognize_positions(puzzle_arr)
        self.move_cost = move
        self.heuristic = calculate_heuristic(self.block_dict[1])
        #Advanced heuristic implementation (make it as a comment)#
        # if not self.heuristic == 0 and not self.heuristic == 1:
        #     caocao_position = self.block_dict[1]
        #     if within_bound([caocao_position[0] - 1, caocao_position[1]]) \
        #         and puzzle_arr[caocao_position[0] - 1][caocao_position[1]] == 0:
        #         pass
        #     elif within_bound([caocao_position[0] - 1, caocao_position[1] + 1]) \
        #         and puzzle_arr[caocao_position[0] - 1][caocao_position[1] + 1] == 0:
        #         pass
        #     elif within_bound([caocao_position[0], caocao_position[1] + 2]) \
        #         and puzzle_arr[caocao_position[0]][caocao_position[1] + 2] == 0:
        #         pass
        #     elif within_bound([caocao_position[0] + 1, caocao_position[1] + 2]) \
        #         and puzzle_arr[caocao_position[0] + 1][caocao_position[1] + 2] == 0:
        #         pass
        #     elif within_bound([caocao_position[0] + 2, caocao_position[1]]) \
        #         and puzzle_arr[caocao_position[0] + 2][caocao_position[1]] == 0:
        #         pass
        #     elif within_bound([caocao_position[0] + 2, caocao_position[1] + 1]) \
        #         and puzzle_arr[caocao_position[0] + 2][caocao_position[1] + 1] == 0:
        #         pass
        #     elif within_bound([caocao_position[0], caocao_position[1] - 1]) \
        #         and puzzle_arr[caocao_position[0]][caocao_position[1] - 1] == 0:
        #         pass
        #     elif within_bound([caocao_position[0] + 1, caocao_position[1] - 1]) \
        #         and puzzle_arr[caocao_position[0] + 1][caocao_position[1] - 1] == 0:
        #         pass
        #     else:
        #         self.heuristic += 0.5
        self.string_arr = ""
        for row in puzzle_arr:
            for item in row:
                self.string_arr += str(item)

    def find_goal(self):
        if self.state_arr[3][1] == 1 and self.state_arr[3][2] == 1 and \
                self.state_arr[4][1] == 1 and self.state_arr[4][2] == 1:
            return True
        else:
            return False

    def find_successors(self):
        #interate through the block dictionary, find possible movesx
        successor_list = []
        for key, value in self.block_dict.items():
            if key == 7:
                for positions in value:
                    check_move(ONE_BY_ONE, positions, self.state_arr, successor_list)
            elif key == 1:
                check_move(TWO_BY_TWO, value, self.state_arr, successor_list)
            else:
                if value[1] == ONE_BY_TWO_HOR:
                    check_move(ONE_BY_TWO_HOR, value[0], self.state_arr, successor_list)
                elif value[1] == ONE_BY_TWO_VER:
                    check_move(ONE_BY_TWO_VER, value[0], self.state_arr, successor_list)

        return successor_list

    def __lt__(self, nxt):
        return self.move_cost + self.heuristic < nxt.move_cost + nxt.heuristic

def covert_output(output_state):
    output_arr = copy.deepcopy(output_state.state_arr)

    for key, value in output_state.block_dict.items():
        if key == 7:
            for position in value:
                output_arr[position[0]][position[1]] = 4
        elif key == 1:
            continue
        else:
            if value[1] == ONE_BY_TWO_HOR:
                output_arr[value[0][0]][value[0][1]] = ONE_BY_TWO_HOR
                output_arr[value[0][0]][value[0][1] + 1] = ONE_BY_TWO_HOR
            elif value[1] == ONE_BY_TWO_VER:
                output_arr[value[0][0]][value[0][1]] = ONE_BY_TWO_VER
                output_arr[value[0][0] + 1][value[0][1]] = ONE_BY_TWO_VER
    return output_arr

def search_Astar(initial_state):
    frontier = []
    # key: string version of board positions, value: the previous state that can directly reach to this
    visited = {}
    end_state = None
    record_path = []
    hq.heappush(frontier, initial_state)

    while not len(frontier) == 0:
        analyze_state = hq.heappop(frontier)
        analyze_cost = analyze_state.move_cost
        if analyze_state.find_goal():
            end_state = analyze_state
            break
        # analyze_state can directly move one step to the following position arrs
        successor_list = analyze_state.find_successors()
        for moves in successor_list:
            possible_state = PuzzleState(moves, analyze_cost + 1)
            if possible_state.string_arr in visited:
                # multiple path pruning: ignore this possible moves since we have visited before
                continue
            else:
                hq.heappush(frontier, possible_state)
                # record it in visited
                visited[possible_state.string_arr] = analyze_state

    if not end_state is None:
        record_path.append(covert_output(end_state))
        curr_state = end_state
        while not curr_state.string_arr == initial_state.string_arr:  # while we not backtrack to the start yet
            prev_state = visited[curr_state.string_arr]
            record_path.append(covert_output(prev_state))
            curr_state = prev_state

    record_path.reverse()  # reverse path to start from initial stage
    # generate output
    write_out(record_path, end_state.move_cost, sys.argv[3])

def search_DFS(initial_state):
    frontier_stack = []
    # key: string version of board positions, value: the previous state that can directly reach to this
    visited = {}
    end_state = None
    record_path = []
    frontier_stack.append(initial_state)

    while not len(frontier_stack) == 0:
        analyze_state = frontier_stack.pop()
        analyze_cost = analyze_state.move_cost
        if analyze_state.find_goal():
            end_state = analyze_state
            break
        # analyze_state can directly move one step to the following position arrs
        successor_list = analyze_state.find_successors()
        for moves in successor_list:
            possible_state = PuzzleState(moves, analyze_cost + 1)
            if possible_state.string_arr in visited:
                # multiple path pruning: ignore this possible moves since we have visited before
                continue
            else:
                frontier_stack.append(possible_state)
                # record it in visited
                visited[possible_state.string_arr] = analyze_state

    if not end_state is None:
        record_path.append(covert_output(end_state))
        curr_state = end_state
        while not curr_state.string_arr == initial_state.string_arr:  # while we not backtrack to the start yet
            prev_state = visited[curr_state.string_arr]
            record_path.append(covert_output(prev_state))
            curr_state = prev_state

    record_path.reverse()  # reverse path to start from initial stage
    # generate output
    write_out(record_path, end_state.move_cost, sys.argv[2])


if __name__ == "__main__":

    #read input text and convert input to a 2d array that contains integer
    input_arr = []
    input_file = open(sys.argv[1], 'r')
    input_string = input_file.read()
    input_file.close()
    mediate_arr =  input_string.split("\n")
    i = 0
    for element in mediate_arr:
        if i == 5:  # in case input contains newline character at the end
            break
        rows = []
        for char in element:
            rows.append(int(char))
        input_arr.append(rows)
        i += 1

    #search content begins
    init_state = PuzzleState(input_arr, 0)
    search_Astar(init_state)
    search_DFS(init_state)