import sys, time
global_start_time = time.time()
EMPTY_BOARD = 0x00000000000000
FULL_MASK = 0xffffffffffffffff #cuts off overflow to negatives
LEFT_MASK = 0xfefefefefefefefe #nothing can go left into right col
RIGHT_MASK = 0x7f7f7f7f7f7f7f7f #nothing can go right into left col

def start():
    return 0x00000810000000, 0x00001008000000

#move a candidate fliter by 1 step in dir,
#see if candidates match the criteria of having opp token,
#if no but end tile is empty, add to moves, if no but end tile is full, ignore
#apply masking as needed to keep in bounds
def get_poss(pieces, token):
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

    return moves

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
    opp = ~token & 1 #flip 0 to 1 and vice-versa (& 1 cuts off all non-first digit bits)    for dir in dirs:
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
    SCORE_CACHE[(pieces, token)] = (format(pieces[token], '064b').count('1'), format(pieces[(~token&1)], '064b').count('1'))
    return SCORE_CACHE[(pieces, token)]

def s_board_to_bitboard(s_board):
    return int(''.join(['1' if ch == "X" else '0' for ch in s_board]), 2), int(''.join(['1' if ch == "O" else '0' for ch in s_board]), 2)

def bitboard_to_s_board(pieces):
    s_brd = ['.' for i in range(64)]
    x_str = format(pieces[0], '064b')
    o_str = format(pieces[1], '064b')
    for i in range(64):
        if x_str[i] == '1':
            s_brd[i] = "X"
        elif o_str[i] == '1':
            s_brd[i] = "O"
    return ''.join(s_brd)

def s_token_to_bit(token):
    return 0 if token == 'X' else 1

def bit_to_s_token(bit):
    return "X" if bit == 0 else "O"

def bit_moves_to_s_moves(bit_moves):
    s_moves = []
    s = format(bit_moves, '064b')
    for i in range(64):
        if s[i] == '1':
            s_moves.append(i)
    return s_moves

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

def find_next_token(board):
    return "X" if sum([1 for ch in board if ch == "X" or ch == "O"])%2==0 else "O"

def A1_style_to_std(move):
    return (int(move[1].upper())-1)*8+(ord(move[0].upper())-65)

#displays 2D board, 1D board, and score (x/y)
def snapshot(pieces):
    if type(pieces) == tuple: #bitboard
        board = bitboard_to_s_board(pieces)
    else: #s_board
        board = pieces
        pieces = s_board_to_bitboard(board)
    display_board(pieces)
    score = get_score(pieces, 0)
    print(board, str(score[0])+"/"+str(score[1]))

#finds the possible moves of the next token with possible moves
#if both have to pass, prints game over and returns None
#also, returns the poss found (with associated token)
def show_poss(pieces, token):
    poss = get_poss(pieces, token)
    opp = ~token & 1
    if poss:
        print("Possible moves for {}: {}".format(bit_to_s_token(token), bit_moves_to_s_moves(poss)))
        return poss, token
    else:
        print("No possible moves for {}.".format(bit_to_s_token(token)))
        poss = get_poss(pieces, opp)
        if not poss: #both have no next moves
            print("No possible moves for {}.".format(bit_to_s_token(opp)))
            print("Game over.")
            return (None, None)
        print("Possible moves for {}: {}".format(bit_to_s_token(opp), bit_moves_to_s_moves(poss)))
        return poss, opp

def main():
    s_brd, s_tkn, moves = None, None, []

    if len(sys.argv) > 1:
        if len(sys.argv[1]) > 5:
            s_brd = sys.argv[1].upper()

    if len(sys.argv) > 2:
        if len(sys.argv[2]) == 1:
            s_tkn = sys.argv[2].upper()

    if s_brd == None and s_tkn == None:
        moves = [int(a) if a[0].upper() not in set("ABCDEFG") else A1_style_to_std(a) for a in sys.argv[1:]]
    elif s_brd == None or s_tkn == None: #XOR
        moves = [int(a) if a[0].upper() not in set("ABCDEFG") else A1_style_to_std(a) for a in sys.argv[2:]]
    else:
        moves = [int(a) if a[0].upper() not in set("ABCDEFG") else A1_style_to_std(a) for a in sys.argv[3:]]

    moves = [i for i in moves if i >= 0] #remove negatives

    if s_brd == None:
        s_brd = '.'*27+'OX......XO'+'.'*27

    if s_tkn == None:
        s_tkn = find_next_token(s_brd)

    print("Starting board:")
    snapshot(s_brd)
    pieces = s_board_to_bitboard(s_brd)
    token = s_token_to_bit(s_tkn)
    poss, token = show_poss(pieces, token)
    while moves:
        s_tkn = bit_to_s_token(token)
        if not poss: break
        move = moves.pop(0)
        next_pieces = place(pieces, token, move)
        if not next_pieces: return
        print("\n{} moves to {}:".format(s_tkn, move))
        snapshot(next_pieces)

        pieces = next_pieces
        opp = ~token & 1
        poss, token = show_poss(pieces, opp)

def callable():
    print("Starting board:")
    snapshot(s_brd)
    pieces = s_board_to_bitboard(s_brd)
    token = s_token_to_bit(s_tkn)
    poss, token = show_poss(pieces, token)
    while moves:
        s_tkn = bit_to_s_token(token)
        if not poss: break
        move = moves.pop(0)
        next_pieces = place(pieces, token, move)
        if not next_pieces: return
        print("\n{} moves to {}:".format(s_tkn, move))
        snapshot(next_pieces)

        pieces = next_pieces
        opp = ~token & 1
        poss, token = show_poss(pieces, opp)
        
if __name__ == '__main__':
    main()
    #display_bitboard(RIGHT_MASK)
