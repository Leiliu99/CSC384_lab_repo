import sys
import heapq as hq
import copy

#global variable to define turn value and piece value in checker
RED_TURN = 4
BLACK_TURN = -4

EMPTY = 0
RED_PIECE = 1
RED_KING = 3
BLACK_PIECE = -1
BLACK_KING = -3

UP = -1
DOWN = 1
BOTH = 0
LEFT = -1
RIGHT = 1

encode_dict = {
    '.': 0, #empty
    'r': 1, #red piece
    'R': 3, #red king
    'b': -1, #black piece
    'B': -3 #black king
}

decode_dict = {
    0: '.', #empty
    1: 'r', #red piece
    3: 'R', #red king
    -1: 'b', #black piece
    -3: 'B' #black king
}

boundary_list = [[1,0], [2,0], [3,0], [4,0], [5,0], [6,0],
                 [1,7], [2,7], [3,7], [4,7], [5,7], [6,7]]
onestep_red_list = [[1,0], [1,1], [1,2], [1,3], [1,4], [1,5], [1,6], [1,7]]
onestep_black_list = [[6,0], [6,1], [6,2], [6,3], [6,4], [6,5], [6,6], [6,7]]


def recognize_pieces(current_checkers):
#given a checkers array, return a dictionary that contains{piece type: position of the piece for this type}
    piece_dict = {RED_PIECE: [], RED_KING: [], BLACK_PIECE: [], BLACK_KING: []}
    for i, rows in enumerate(current_checkers):
        for j, element in enumerate(rows):
            if element == 0:
                continue
            if piece_dict.get(element) is not None:
                piece_dict[element].append([i, j])
            else:
                print("------Error in encoding the checker state------")
    return piece_dict

def calculate_utility(arr_board, current_pieces):
    utility = 0
    for piece_type, positions in current_pieces.items():
        # utility += piece_type * len(positions) simple utility previously used
        if piece_type == RED_KING or piece_type == BLACK_KING:
            utility += piece_type * len(positions)
        else:
            for piece_position in positions:
                if piece_position in boundary_list: #this piece is on the boundary
                    utility += piece_type * 2
                elif piece_type == RED_PIECE and piece_position in onestep_red_list:
                    if (not within_bound([piece_position[0]-1, piece_position[1]+1]) or (
                            arr_board[piece_position[0]-1][piece_position[1]+1] == EMPTY)) or \
                            (not within_bound([piece_position[0]-1, piece_position[1]-1]) or (
                                    arr_board[piece_position[0]-1][piece_position[1]-1] == EMPTY)):
                        #red piece is one step to be the king
                        utility += piece_type * 2
                    else:
                        utility += piece_type
                elif piece_type == BLACK_PIECE and piece_position in onestep_black_list:
                    if (not within_bound([piece_position[0] + 1, piece_position[1] + 1]) or (
                            arr_board[piece_position[0] + 1][piece_position[1] + 1] == EMPTY)) or \
                            (not within_bound([piece_position[0] + 1, piece_position[1] - 1]) or (
                                    arr_board[piece_position[0] + 1][piece_position[1] - 1] == EMPTY)):
                        # black piece is one step to be the king
                        utility += piece_type * 2
                    else:
                        utility += piece_type
                else:
                    utility += piece_type
    return utility

def within_bound(position):
    return 0 <= position[0] <= 7 and 0 <= position[1] <= 7

def check_jump(piece_type, direction, current_checkers, position, possible_jumps):
    #recognize enemy piece
    enemy_list = []
    if piece_type == RED_PIECE or piece_type == RED_KING:
        enemy_list.extend([BLACK_PIECE, BLACK_KING])
    elif piece_type == BLACK_PIECE or BLACK_KING:
        enemy_list.extend([RED_PIECE, RED_KING])
    else:
        print("------Error in recognizing enemy piece------")

    found_jump = False
    #up jump
    if direction == UP or direction == BOTH:
        #up left
        position_one = [position[0] + UP, position[1] + LEFT]
        position_two = [position_one[0] + UP, position_one[1] + LEFT]
        if within_bound(position_one) and within_bound(position_two):
            if current_checkers[position_two[0]][position_two[1]] == EMPTY and \
                    (current_checkers[position_one[0]][position_one[1]] == enemy_list[0] or
                     current_checkers[position_one[0]][position_one[1]] == enemy_list[1]):
                found_jump = True
                after_jump = copy.deepcopy(current_checkers)
                after_jump[position[0]][position[1]] = 0
                after_jump[position_one[0]][position_one[1]] = 0
                if piece_type == RED_PIECE and position_two[0] == 0:
                    #change to king
                    after_jump[position_two[0]][position_two[1]] = RED_KING
                    possible_jumps.append(after_jump)
                else:
                    after_jump[position_two[0]][position_two[1]] = piece_type
                    if piece_type == RED_KING or piece_type == BLACK_KING:
                        further_jump = check_jump(piece_type, BOTH, after_jump, position_two, possible_jumps)
                    else:
                        further_jump = check_jump(piece_type, UP, after_jump, position_two, possible_jumps)
                    if not further_jump:
                        possible_jumps.append(after_jump)

        #up right
        position_one = [position[0] + UP, position[1] + RIGHT]
        position_two = [position_one[0] + UP, position_one[1] + RIGHT]
        if within_bound(position_one) and within_bound(position_two):
            if current_checkers[position_two[0]][position_two[1]] == EMPTY and \
                    (current_checkers[position_one[0]][position_one[1]] == enemy_list[0] or
                     current_checkers[position_one[0]][position_one[1]] == enemy_list[1]):
                found_jump = True
                after_jump = copy.deepcopy(current_checkers)
                after_jump[position[0]][position[1]] = 0
                after_jump[position_one[0]][position_one[1]] = 0
                if piece_type == RED_PIECE and position_two[0] == 0:
                    #change to king
                    after_jump[position_two[0]][position_two[1]] = RED_KING
                    possible_jumps.append(after_jump)
                else:
                    after_jump[position_two[0]][position_two[1]] = piece_type
                    if piece_type == RED_KING or piece_type == BLACK_KING:
                        further_jump = check_jump(piece_type, BOTH, after_jump, position_two, possible_jumps)
                    else:
                        further_jump = check_jump(piece_type, UP, after_jump, position_two, possible_jumps)
                    if not further_jump:
                        possible_jumps.append(after_jump)
    #down jump
    if direction == DOWN or direction == BOTH:
        # down left
        position_one = [position[0] + DOWN, position[1] + LEFT]
        position_two = [position_one[0] + DOWN, position_one[1] + LEFT]
        if within_bound(position_one) and within_bound(position_two):
            if current_checkers[position_two[0]][position_two[1]] == EMPTY and \
                    (current_checkers[position_one[0]][position_one[1]] == enemy_list[0] or
                     current_checkers[position_one[0]][position_one[1]] == enemy_list[1]):
                found_jump = True
                after_jump = copy.deepcopy(current_checkers)
                after_jump[position[0]][position[1]] = 0
                after_jump[position_one[0]][position_one[1]] = 0
                if piece_type == BLACK_PIECE and position_two[0] == 7:
                    #change to king
                    after_jump[position_two[0]][position_two[1]] = BLACK_KING
                    possible_jumps.append(after_jump)
                else:
                    after_jump[position_two[0]][position_two[1]] = piece_type
                    if piece_type == RED_KING or piece_type == BLACK_KING:
                        further_jump = check_jump(piece_type, BOTH, after_jump, position_two, possible_jumps)
                    else:
                        further_jump = check_jump(piece_type, DOWN, after_jump, position_two, possible_jumps)
                    if not further_jump:
                        possible_jumps.append(after_jump)

        # down right
        position_one = [position[0] + DOWN, position[1] + RIGHT]
        position_two = [position_one[0] + DOWN, position_one[1] + RIGHT]
        if within_bound(position_one) and within_bound(position_two):
            if current_checkers[position_two[0]][position_two[1]] == EMPTY and \
                    (current_checkers[position_one[0]][position_one[1]] == enemy_list[0] or
                     current_checkers[position_one[0]][position_one[1]] == enemy_list[1]):
                found_jump = True
                after_jump = copy.deepcopy(current_checkers)
                after_jump[position[0]][position[1]] = 0
                after_jump[position_one[0]][position_one[1]] = 0
                if piece_type == BLACK_PIECE and position_two[0] == 7:
                    # change to king
                    after_jump[position_two[0]][position_two[1]] = BLACK_KING
                    possible_jumps.append(after_jump)
                else:
                    after_jump[position_two[0]][position_two[1]] = piece_type
                    if piece_type == RED_KING or piece_type == BLACK_KING:
                        further_jump = check_jump(piece_type, BOTH, after_jump, position_two, possible_jumps)
                    else:
                        further_jump = check_jump(piece_type, DOWN, after_jump, position_two, possible_jumps)
                    if not further_jump:
                        possible_jumps.append(after_jump)
    return found_jump

def check_move(piece_type, current_checkers, position, possible_moves):
    #up direction
    if piece_type == RED_PIECE or piece_type == RED_KING or piece_type == BLACK_KING:
        #up left
        if within_bound([position[0] + UP, position[1] + LEFT]) and \
            current_checkers[position[0] + UP][position[1] + LEFT] == EMPTY:
            after_move = copy.deepcopy(current_checkers)
            after_move[position[0]][position[1]] = 0
            if piece_type == RED_PIECE and position[0] + UP == 0:
                #change to king
                after_move[position[0] + UP][position[1] + LEFT] = RED_KING
            else:
                after_move[position[0] + UP][position[1] + LEFT] = piece_type
            possible_moves.append(after_move)

        #up right
        if within_bound([position[0] + UP, position[1] + RIGHT]) and \
            current_checkers[position[0] + UP][position[1] + RIGHT] == EMPTY:
            after_move = copy.deepcopy(current_checkers)
            after_move[position[0]][position[1]] = 0
            if piece_type == RED_PIECE and position[0] + UP == 0:
                #change to king
                after_move[position[0] + UP][position[1] + RIGHT] = RED_KING
            else:
                after_move[position[0] + UP][position[1] + RIGHT] = piece_type
            possible_moves.append(after_move)

    #down direction
    if piece_type == BLACK_PIECE or piece_type == RED_KING or piece_type == BLACK_KING:
        #down left
        if within_bound([position[0] + DOWN, position[1] + LEFT]) and \
            current_checkers[position[0] + DOWN][position[1] + LEFT] == EMPTY:
            after_move = copy.deepcopy(current_checkers)
            after_move[position[0]][position[1]] = 0
            if piece_type == BLACK_PIECE and position[0] + DOWN == 7:
                #change to king
                after_move[position[0] + DOWN][position[1] + LEFT] = BLACK_KING
            else:
                after_move[position[0] + DOWN][position[1] + LEFT] = piece_type
            possible_moves.append(after_move)

        #down right
        if within_bound([position[0] + DOWN, position[1] + RIGHT]) and \
            current_checkers[position[0] + DOWN][position[1] + RIGHT] == EMPTY:
            after_move = copy.deepcopy(current_checkers)
            after_move[position[0]][position[1]] = 0
            if piece_type == BLACK_PIECE and position[0] + DOWN == 7:
                #change to king
                after_move[position[0] + DOWN][position[1] + RIGHT] = BLACK_KING
            else:
                after_move[position[0] + DOWN][position[1] + RIGHT] = piece_type
            possible_moves.append(after_move)




class CheckerState:

    def __init__(self, checkers_arr, checkers_turn):
        self.state_arr = checkers_arr
        self.piece_dict = recognize_pieces(checkers_arr)
        self.turn = checkers_turn
        self.utility = calculate_utility(checkers_arr, self.piece_dict)

        self.string_arr = ""
        for row in checkers_arr:
            for item in row:
                self.string_arr += str(item)

    def is_terminate(self):
        #here we only consider the first situation which is one side has on pieces remaining
        if (len(self.piece_dict[RED_PIECE]) == 0 and len(self.piece_dict[RED_KING]) == 0) or \
                (len(self.piece_dict[BLACK_PIECE]) == 0 and len(self.piece_dict[BLACK_KING]) == 0):
            return True
        else:
            return False

    def find_successors(self, turn):
        #first check jump possibles, if there is at least jump available, return this jump list as successors
        #since jumping is mandatory
        jump_list = []
        if turn == RED_TURN:
            for position in self.piece_dict[RED_PIECE]:
                check_jump(RED_PIECE, UP, self.state_arr, position, jump_list)
            for position in self.piece_dict[RED_KING]:
                check_jump(RED_KING, BOTH, self.state_arr, position, jump_list)
                #check_jump(RED_KING, DOWN, self.state_arr, position, jump_list)
        elif turn == BLACK_TURN:
            for position in self.piece_dict[BLACK_PIECE]:
                check_jump(BLACK_PIECE, DOWN, self.state_arr, position, jump_list)
            for position in self.piece_dict[BLACK_KING]:
                check_jump(BLACK_KING, BOTH, self.state_arr, position, jump_list)
                #check_jump(BLACK_KING, UP, self.state_arr, position, jump_list)
        if not len(jump_list) == 0:
            return jump_list


        #if no jump available, find available moves
        #call helper function check_move, insert possible moves into move_list based on turn value
        move_list = []
        if turn == RED_TURN:
            for position in self.piece_dict[RED_PIECE]:
                check_move(RED_PIECE, self.state_arr, position, move_list)
            for position in self.piece_dict[RED_KING]:
                check_move(RED_KING, self.state_arr, position, move_list)
        elif turn == BLACK_TURN:
            for position in self.piece_dict[BLACK_PIECE]:
                check_move(BLACK_PIECE, self.state_arr, position, move_list)
            for position in self.piece_dict[BLACK_KING]:
                check_move(BLACK_KING, self.state_arr, position, move_list)
        return move_list


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

def alpha_beta_search(checker_state, checker_alpha, checker_beta, search_depth):
    best_move = None
    value = 0
    next_turn = 0
    #base case 1
    if checker_state.is_terminate() or search_depth >= 8:
        return checker_state.state_arr, checker_state.utility
    # base case 2
    successor_list = checker_state.find_successors(checker_state.turn)
    if len(successor_list) == 0:#no possible move for this turn
        return checker_state.state_arr, checker_state.utility

    if checker_state.turn == RED_TURN:
        value = float('-inf')
        next_turn = BLACK_TURN
    if checker_state.turn == BLACK_TURN:
        value = float('inf')
        next_turn = RED_TURN

    for possible_moves in successor_list:
        next_state = CheckerState(possible_moves, next_turn)
        _, next_value = alpha_beta_search(next_state, checker_alpha, checker_beta, search_depth + 1)
        if checker_state.turn == RED_TURN:
            if value < next_value:
                value = next_value
                best_move = next_state.state_arr
            if value >= checker_beta: #alpha cut
                return best_move, value
            checker_alpha = max(checker_alpha, value)

        if checker_state.turn == BLACK_TURN:
            if value > next_value:
                value = next_value
                best_move = next_state.state_arr
            if value <= checker_alpha: #beta cut
                return best_move, value
            checker_beta = min(checker_beta, value)
    return best_move, value



if __name__ == "__main__":

    #read input text and convert input to a 2d array that contains integer
    input_arr = []
    input_file = open(sys.argv[1], 'r')
    input_string = input_file.read()
    input_file.close()
    mediate_arr =  input_string.split("\n")
    i = 0
    for element in mediate_arr:
        if i == 8:  # in case input contains a newline character at the end
            break
        rows = []
        for char in element:
            rows.append(encode_dict[char])
        input_arr.append(rows)
        i += 1

    #initialize input into state presentation
    init_state = CheckerState(input_arr, RED_TURN)

    #search begins
    alpha = float('-inf')
    beta = float('inf')
    decided_move, decided_value = alpha_beta_search(init_state, alpha, beta, 0)
    write_out(sys.argv[2], covert_output(decided_move))
