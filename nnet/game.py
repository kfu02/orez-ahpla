### core game methods ###
EMPTY_BOARD = 0x00000000000000
FULL_MASK = 0xffffffffffffffff #cuts off overflow to negatives
LEFT_MASK = 0xfefefefefefefefe #nothing can go left into right col
RIGHT_MASK = 0x7f7f7f7f7f7f7f7f #nothing can go right into left col

#CORNERS = 0x8100000000000081
#CENTERS = 0x0000001818000000

def start():
    return 0x00000810000000, 0x00001008000000

def flip_board_neg(pieces):
    #adapted from www.chessprogramming.org
    #masks
    k1 = 0x5500550055005500
    k2 = 0x3333000033330000
    k4 = 0x0F0F0F0F00000000
    #flipping
    out = []
    for bb in pieces:
        t = k4&(bb^(bb<<28))
        bb ^= t^(t>>28)
        t = k2&(bb^(bb<<14))
        bb ^= t^(t>>14)
        t = k1&(bb^(bb<<7))
        bb ^= t^(t>>7)
        out.append(bb)
    return tuple(out)

def flip_board_pos(pieces):
    #masks
    k1 = 0xaa00aa00aa00aa00
    k2 = 0xcccc0000cccc0000
    k4 = 0xf0f0f0f00f0f0f0f
    #flipping
    out = []
    for bb in pieces:
        t = bb^(bb<<36)
        bb ^= k4&(t^(bb>>36))
        t = k2&(bb^(bb<<18))
        bb ^= t^(t>>18)
        t = k1&(bb^(bb<<9))
        bb ^= t^(t>>9)
        out.append(bb)
    return tuple(out)

def flip_board_both(pieces):
    return flip_board_neg(flip_board_pos(pieces))

#helper method for get_poss()
BIT_POSS_CACHE = {}
def bit_poss_to_moves(bit_moves):
    if bit_moves in BIT_POSS_CACHE:
        #print('poss recur')
        return BIT_POSS_CACHE[bit_moves]
    s = format(bit_moves, '064b')
    moves = [i for i in range(64) if s[i] == '1']
    BIT_POSS_CACHE[bit_moves] = moves
    return BIT_POSS_CACHE[bit_moves]

#move a candidate fliter by 1 step in dir,
#see if candidates match the criteria of having opp token,
#if no but end tile is empty, add to moves, if no but end tile is full, ignore
#apply masking as needed to keep in bounds
POSS_CACHE = {}
def get_poss(state):
    if state in POSS_CACHE:
        #print('poss recur')
        return POSS_CACHE[state]
    pieces, token = state
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

    POSS_CACHE[state] = bit_poss_to_moves(moves)
    return POSS_CACHE[state]

"""
move in normal 8x8 int, not as bitboard
assumes move is legal
similar to get poss:
move a candidate fliter by 1 step in dir,
see if candidates match the criteria of having opp token,
if yes, add to flippables
if no, stop moving candidates

input: state (board, token), move
output: board
"""
def place(state, move):
    pieces, token = state
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
def get_score(state):
    if state in SCORE_CACHE:
        #print('score recur')
        return SCORE_CACHE[state]
    pieces, token = state
    score = (format(pieces[token], '064b').count('1')-format(pieces[(~token&1)], '064b').count('1'))
    SCORE_CACHE[state] = score
    return SCORE_CACHE[state]

"""
win for token = 1
loss for token = -1
tie = 0
not terminal = -2
"""
def is_terminal(state, p=None): #should take optional poss arg
    pieces, token = state
    if p:
        if token == 0:
            x_poss = p
            o_poss = get_poss((pieces, 1))
        else:
            x_poss = get_poss((pieces, 0))
            o_poss = p
    else:
        x_poss = get_poss((pieces, 0))
        o_poss = get_poss((pieces, 1))
    if not x_poss and not o_poss: #game over
        score = get_score(state) #score for token
        if score == 0:
            return 0
        return 1 if score > 0 else -1
    return -2 #game not over

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
