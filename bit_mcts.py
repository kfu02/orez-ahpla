import random, sys, time
from math import log, sqrt
global_start_time = time.time()
### core game methods ###
EMPTY_BOARD = 0x00000000000000
FULL_MASK = 0xffffffffffffffff #cuts off overflow to negatives
LEFT_MASK = 0xfefefefefefefefe #nothing can go left into right col
RIGHT_MASK = 0x7f7f7f7f7f7f7f7f #nothing can go right into left col

CORNERS = 0x8100000000000081
CENTERS = 0x0000001818000000

def start():
    return 0x00000810000000, 0x00001008000000

def flip_neg_diag(bb):
    #adapted from www.chessprogramming.org
    #masks
    k1 = 0x5500550055005500
    k2 = 0x3333000033330000
    k4 = 0x0F0F0F0F00000000
    #flipping
    t = k4&(bb^(bb<<28))
    bb ^= t^(t>>28)
    t = k2&(bb^(bb<<14))
    bb ^= t^(t>>14)
    t = k1&(bb^(bb<<7))
    bb ^= t^(t>>7)
    return bb

def flip_pos_diag(bb):
    #masks
    k1 = 0xaa00aa00aa00aa00
    k2 = 0xcccc0000cccc0000
    k4 = 0xf0f0f0f00f0f0f0f
    #flipping
    t = bb^(bb<<36)
    bb ^= k4&(t^(bb>>36))
    t = k2&(bb^(bb<<18))
    bb ^= t^(t>>18)
    t = k1&(bb^(bb<<9))
    bb ^= t^(t>>9)
    return bb

def flip_both(bb):
    return flip_neg_diag(flip_pos_diag(bb))

#helper method for get_poss()
BIT_POSS_CACHE = {}
def bit_poss_to_moves(bit_moves):
    if bit_moves in BIT_POSS_CACHE:
        return BIT_POSS_CACHE[bit_moves]
    moves = set()
    s = format(bit_moves, '064b')
    for i in range(64):
        if s[i] == '1':
            moves.add(i)

    BIT_POSS_CACHE[bit_moves] = moves
    return BIT_POSS_CACHE[bit_moves]

#move a candidate fliter by 1 step in dir,
#see if candidates match the criteria of having opp token,
#if no but end tile is empty, add to moves, if no but end tile is full, ignore
#apply masking as needed to keep in bounds
POSS_CACHE = {}
def get_poss(pieces, token):
    if (pieces, token) in POSS_CACHE:
        return POSS_CACHE[(pieces, token)]

    #E, S, SW, SE >>
    #W, N, NE, NW <<
    dirs = [1, 8, 7, 9]
    moves = EMPTY_BOARD
    full = pieces[0] | pieces[1]
    empty = ~full & FULL_MASK
    opp = ~token & 1 #flip 0 to 1 and vice-versa (& 1 cuts off all non-first digit bits)
    for dir in dirs:
        if dir == 1 or dir == 9:
            candidates = pieces[opp] & ((pieces[token] >> dir) & RIGHT_MASK)
        elif dir == 7:
            candidates = pieces[opp] & ((pieces[token] >> dir) & LEFT_MASK)
        else:
            candidates = pieces[opp] & ((pieces[token] >> dir) & FULL_MASK)

        while candidates:
            cand_shift = candidates >> dir
            if dir == 1 or dir == 9:
                cand_shift &= RIGHT_MASK
            elif dir == 7:
                cand_shift &= LEFT_MASK
            else:
                cand_shift &= FULL_MASK
            moves |= empty & cand_shift
            candidates = pieces[opp] & cand_shift

        #search in both directions
        if dir == 1 or dir == 9:
            candidates = pieces[opp] & ((pieces[token] << dir) & LEFT_MASK)
        elif dir == 7:
            candidates = pieces[opp] & ((pieces[token] << dir) & RIGHT_MASK)
        else:
            candidates = pieces[opp] & ((pieces[token] << dir) & FULL_MASK)

        while candidates:
            cand_shift = (candidates << dir)
            if dir == 1 or dir == 9:
                cand_shift &= LEFT_MASK
            elif dir == 7:
                cand_shift &= RIGHT_MASK
            else:
                cand_shift &= FULL_MASK
            moves |= empty & cand_shift
            candidates = pieces[opp] & cand_shift

    POSS_CACHE[(pieces, token)] = bit_poss_to_moves(moves)
    #account for reflections
    POSS_CACHE[((flip_neg_diag(pieces[0]), flip_neg_diag(pieces[1])), token)] = bit_poss_to_moves(flip_neg_diag(moves))
    POSS_CACHE[((flip_pos_diag(pieces[0]), flip_pos_diag(pieces[1])), token)] = bit_poss_to_moves(flip_pos_diag(moves))
    POSS_CACHE[((flip_both(pieces[0]), flip_both(pieces[1])), token)] = bit_poss_to_moves(flip_both(moves))
    return POSS_CACHE[(pieces, token)]

#move in normal 8x8 int, not as bitboard
#assumes move is legal
#similar to get poss:
#move a candidate fliter by 1 step in dir,
#see if candidates match the criteria of having opp token,
#if yes, add to flippables
#if no, stop moving candidates
def place(pieces, token, move):
    move_applied = (1 << (63-move)) & FULL_MASK
    dirs = [1, 8, 7, 9]
    flips = move_applied
    full = pieces[0] | pieces[1]
    empty = ~full & FULL_MASK
    opp = ~token & 1 #flip 0 to 1 and vice-versa (& 1 cuts off all non-first digit bits)
    for dir in dirs: #find pieces to flip
        if dir == 1 or dir == 9:
            candidates = pieces[opp] & ((move_applied >> dir) & RIGHT_MASK)
        elif dir == 7:
            candidates = pieces[opp] & ((move_applied >> dir) & LEFT_MASK)
        else:
            candidates = pieces[opp] & ((move_applied >> dir) & FULL_MASK)

        my_flips = candidates
        flippable = True
        while candidates:
            cand_shift = candidates >> dir
            if dir == 1 or dir == 9:
                cand_shift &= RIGHT_MASK
            elif dir == 7:
                cand_shift &= LEFT_MASK
            else:
                cand_shift &= FULL_MASK
            flippable = pieces[token] & cand_shift #only flip if last candidate has a token piece
            candidates = pieces[opp] & cand_shift
            my_flips |= candidates

        if flippable:
            flips |= my_flips

        #search in both directions
        if dir == 1 or dir == 9:
            candidates = pieces[opp] & ((move_applied << dir) & LEFT_MASK)
        elif dir == 7:
            candidates = pieces[opp] & ((move_applied << dir) & RIGHT_MASK)
        else:
            candidates = pieces[opp] & ((move_applied << dir) & FULL_MASK)

        my_flips = candidates
        flippable = True
        while candidates:
            cand_shift = candidates << dir
            if dir == 1 or dir == 9:
                cand_shift &= LEFT_MASK
            elif dir == 7:
                cand_shift &= RIGHT_MASK
            else:
                cand_shift &= FULL_MASK
            flippable = pieces[token] & cand_shift #only flip if last candidate has a token piece
            candidates = pieces[opp] & cand_shift
            my_flips |= candidates

        if flippable:
            flips |= my_flips

    #apply flips to board, return
    if token == 0: #X
        return (pieces[0]|flips, pieces[1]&(~flips))
    else: #O
        return (pieces[0]&(~flips), pieces[1]|flips)

SCORE_CACHE = {}
def get_score(pieces, token):
    if (pieces, token) in SCORE_CACHE:
        return SCORE_CACHE[(pieces, token)]
    SCORE_CACHE[(pieces, token)] = (format(pieces[token], '064b').count('1')-format(pieces[(~token&1)], '064b').count('1'))
    return SCORE_CACHE[(pieces, token)]

"""
MAJOR CHANGE FROM BASIC_MCTS.PY
win for X = 0
win for O = 1
tie = -1
not terminal = -2
"""
def is_terminal(pieces):
    x_poss = get_poss(pieces, 0)
    o_poss = get_poss(pieces, 1)
    if not x_poss and not o_poss: #game over
        score = get_score(pieces, 0) #score for X
        if score == 0: return -1 #tie
        return 0 if score > 0 else 1 #return whichever token is the winner
    return -2 #game not over

### conversion methods ###
def s_brd_to_bitboard(s_board):
    return int(''.join(['1' if ch == "X" else '0' for ch in s_board]), 2), int(''.join(['1' if ch == "O" else '0' for ch in s_board]), 2)

def bitboard_to_s_brd(pieces):
    s_brd = ['.' for i in range(64)]
    x_str = format(pieces[0], '064b')
    o_str = format(pieces[1], '064b')
    for i in range(64):
        if x_str[i] == '1':
            s_brd[i] = "X"
        elif o_str[i] == '1':
            s_brd[i] = "O"
    return ''.join(s_brd)

def s_tkn_to_bit(token):
    return 0 if token == 'X' else 1

def bit_to_s_tkn(bit):
    return "X" if bit == 0 else "O"

### display methods ###
def display_bitboard(bitboard):
    str_b = format(bitboard, '064b')
    for i in range(8):
        print(str_b[i*8:(i+1)*8])
    print()

def display_board(pieces): #handles bitboard and str_board representations
    if type(pieces) == tuple: #bitboard
        x_board, o_board = pieces
        board = list(format(EMPTY_BOARD, '064b'))
        str_x = format(x_board, '064b')
        str_o = format(o_board, '064b')
        for i in range(64):
            if str_x[i] == '1':
                board[i] = "X"
            elif str_o[i] == '1':
                board[i] = "O"
            else:
                board[i] = '.'
    else: #str_board
        board = pieces
    ret = '-'*(8*2+1)+"\n"
    for i in range(8-1):
        row = board[i*8:(i+1)*8]
        for ch in range(len(row)-1):
            ret += "|" + row[ch]
        ret += "|"+str(row[-1])+"|"
        ret += "\n"+"-"*(8*2+1)+"\n"
    row = board[8*8-8:]
    for ch in range(len(row)-1):
        ret += "|" + row[ch]
    ret += "|"+str(row[-1])+"|\n"
    ret += '-'*(8*2+1)
    print(ret+"\n")

### MCTS methods ###
#monte carlo tree search
class MonteCarlo(object):
    def __init__(self, **kwargs):
    #takes Game object, keyword args, and initializes game_history and stats dicts accordingly
        print('inputs')
        print(kwargs)
        self.current_state = kwargs.get('brd', start()) #tuple now
        self.time_given = kwargs.get('time', 10) #10 by default
        self.max_lookahead = kwargs.get('max_fwd', 10000)
        self.start_token = kwargs.get('tkn', 0) #starting token of board, X by default
        self.max_depth = 0
        self.C = kwargs.get('C', 1.414) #sqrt 2

        self.reward = {}
        self.plays = {}

    def find_best_move(self):
    #find next best move based on current tree
        state = self.current_state
        print(state)
        token = self.start_token
        poss = get_poss(state, token)

        #if no moves or only one, no thinking needed
        if not poss:
            return
        if len(poss) == 1:
            return poss.pop()

        #simulating games to find next move
        games_played = 0
        start_time = time.time()
        while time.time()-start_time < self.time_given-0.1:
            self.run_simulation(token)
            games_played += 1

        #print(self.plays)
        #print(self.reward)

        print(games_played, time.time()-start_time) #games simulated, time taken

        moves_to_states = [(move, place(state, token, move)) for move in poss]
        """
        best_move = -1
        best_avg_reward = -1
        for move, state in moves_to_states:
            reward = self.reward.get((token, state), 0) #0 if not in dict
            plays = self.plays.get((token, state), 1)
            pct = reward/plays
            print(move, reward, plays, pct)
            if pct > best_avg_reward:
                best_avg_reward = pct
                best_move = move
        """
        #find best move based on win_pct
        best_avg_reward, best_move = max( \
            (self.reward.get((token, state), 0)/self.plays.get((token, state), 1), move) \
            for move, state in moves_to_states \
        )

        debug_stats = [ \
            (self.reward.get((token, state), 0)/self.plays.get((token, state),1), \
            self.reward.get((token, state), 0), \
            self.plays.get((token, state), 0), \
            move) for move, state in moves_to_states \
        ]

        for tup in sorted(debug_stats)[::-1]:
            print(tup)

        print("best_move", best_move)
        print("best_avg_reward", best_avg_reward)
        print("max_depth", self.max_depth)
        return best_move

    def run_simulation(self, token): #light playout
    #play a random game from current state, update stats
        #plays, reward = self.plays, self.reward #apparently local lookup faster than classvar lookup

        seen_states = set()
        board = self.current_state
        expand = True
        for d in range(self.max_lookahead):
            poss = get_poss(board, token)
            moves_to_states = [(move, place(board, token, move)) for move in poss]

            """
            if all(self.plays.get((move, state)) for move, state in moves_to_states): #if all moves/states seen, use known best
                log_total = log(sum(self.plays[(token, state)] for move, state in moves_to_states))
                value, move, state = max( \
                    (self.reward[(token, state)]/self.plays[(token, state)] + \
                    self.C * sqrt(log_total/self.plays[(token, state)]), move, state) \
                    for move, state in moves_to_states \
                )
            else: #otherwise, pick randomly
                move = random.sample(poss, 1).pop()
                #print('temp: ',move, poss)
                state = place(board, token, move)
            """
            #print(poss)
            if not poss:
                token = ~token & 1 #flip token bit
                poss = get_poss(board, token)
            move = random.sample(poss, 1).pop()
            state = place(board, token, move)

            board = state #why this line???
            #token that GOT TO a certain state stored
            if expand and (token, state) not in self.plays: #expand until a leaf node is hit
                expand = False
                self.plays[(token, state)] = 0
                self.reward[(token, state)] = 0
                if d > self.max_depth:
                    self.max_depth = d

            seen_states.add((token, state))

            token = ~token & 1 #flip token bit
            winner = is_terminal(board)
            if winner > -2: #break if game over
                break

        for tkn, state in seen_states:
            if (tkn, state) not in self.plays:
                continue
            self.plays[(tkn, state)] += 1
            if winner == -1: #draw
                self.reward[(tkn, state)] += 0
            elif winner == tkn:
                self.reward[(tkn, state)] += 1
            else:
                self.reward[(tkn, state)] -= 1

### testing ###
#removed pickling from basic_mcts.py
def main():
    board = start()
    TIME_INPUT = float(sys.argv[1]) if len(sys.argv) > 1 else 5
    token = 0
    moves_played = []
    while is_terminal(board) == -2:
        display_board(board)
        #token = find_next_token(board) #doesn't work bc of passes
        #instead, assume no passes unless needed, switch every turn
        if not get_poss(board, token):
            token = ~token & 1
        mc = MonteCarlo(brd=board, tkn=token, time=TIME_INPUT)
        best_move = mc.find_best_move()
        moves_played.append(best_move)
        print(bitboard_to_s_brd(board), token, best_move)
        board = place(board, token, best_move)
        token = ~token & 1

    print('final')
    display_board(board)
    print(is_terminal(board))
    print('moves')
    for m in moves_played:
        print(m, end=' ')
    print()

if __name__ == '__main__':
    main()
