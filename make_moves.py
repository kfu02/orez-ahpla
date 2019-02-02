import sys, time
global_start_time = time.time()
EMPTY_BOARD = 0x00000000000000
FULL_MASK = 0xffffffffffffffff #cuts off overflow to negatives
LEFT_MASK = 0xfefefefefefefefe #nothing can go left into right col
RIGHT_MASK = 0x7f7f7f7f7f7f7f7f #nothing can go right into left col

def start():
    x = 0x00000810000000
    o = 0x00001008000000
    #display_bitboard(x)
    #display_bitboard(o)
    #display_board(x,o)
    return x, o

def get_poss(pieces, token):
    #E, S, SW, SE >>
    #W, N, NE, NW <<
    dirs = [1, 8, 7, 9]
    moves = EMPTY_BOARD
    full = pieces[0] | pieces[1]
    empty = ~full & FULL_MASK
    opp = ~token & 1 #flip 0 to 1 and vice-versa (& 1 cuts off all non-first digit bits)
    #display_bitboard(empty)
    for dir in dirs:
        if dir == 1 or dir == 9:
            candidates = pieces[opp] & ((pieces[token] >> dir) & RIGHT_MASK)
        elif dir == 7:
            candidates = pieces[opp] & ((pieces[token] >> dir) & LEFT_MASK)
        else:
            candidates = pieces[opp] & ((pieces[token] >> dir) & FULL_MASK)
        #print(dir)
        #display_bitboard(pieces[token])
        #display_bitboard(pieces[opp])
        while candidates:
            """
            print('loop', dir)
            display_bitboard(pieces[0])
            display_bitboard(pieces[1])
            display_bitboard(candidates)
            display_bitboard(empty)
            display_bitboard(candidates >> dir)
            display_bitboard(empty& (candidates>>dir))
            """
            cand_shift = candidates >> dir
            if dir == 1 or dir == 9:
                moves |= empty & (cand_shift & RIGHT_MASK)
                candidates = pieces[opp] & (cand_shift & RIGHT_MASK)
            elif dir == 7:
                moves |= empty & (cand_shift & LEFT_MASK)
                candidates = pieces[opp] & (cand_shift & LEFT_MASK)
            else:
                moves |= empty & cand_shift
                candidates = pieces[opp] & (cand_shift & FULL_MASK)
            #print('m')
            #display_bitboard(moves)
        #print('mf')
        #display_bitboard(moves)

        if dir == 1 or dir == 9:
            candidates = pieces[opp] & ((pieces[token] << dir) & LEFT_MASK)
        elif dir == 7:
            candidates = pieces[opp] & ((pieces[token] << dir) & RIGHT_MASK)
        else:
            candidates = pieces[opp] & ((pieces[token] << dir) & FULL_MASK)

        while candidates:

            #print('loop 2', dir)
            #display_bitboard(pieces[0])
            #display_bitboard(pieces[1])
            #display_bitboard(candidates)
            #print("cshift", dir)
            cand_shift = (candidates << dir)
            #display_bitboard(cand_shift)
            #display_bitboard(empty)
            if dir == 1 or dir == 9:
                moves |= empty & (cand_shift & LEFT_MASK)
                candidates = pieces[opp] & (cand_shift & LEFT_MASK)
            elif dir == 7:
                moves |= empty & (cand_shift & RIGHT_MASK)
                candidates = pieces[opp] & (cand_shift & RIGHT_MASK)
            else:
                moves |= empty & (cand_shift & FULL_MASK)
                candidates = pieces[opp] & (cand_shift & FULL_MASK)
            #print('m')
            #display_bitboard(moves)
        #print('mf')
        #display_bitboard(moves)
    return moves

def place(pieces, token, move):
#move in normal 8x8 int, not as bitboard
#internally, a union should suffice
    move_applied = (1 << (63-move)) & FULL_MASK
    display_bitboard(move_applied)
    display_bitboard(pieces[0])
    if token == 0:
        return (pieces[0] | move_applied, pieces[1])
    else:
        return (pieces[0], pieces[1] | move_applied)

def s_board_to_bitboard(s_board):
    x_list = ['1' if ch == "X" else '0' for ch in s_board]
    o_list = ['1' if ch == "O" else '0' for ch in s_board]
    x = int(''.join(x_list), 2)
    o = int(''.join(o_list), 2)
    return x, o

def s_token_to_bit(token):
    return 0 if token == 'X' else 1

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

"""
remove this
"""
def find_next_token(board):
    return "X" if sum([1 for ch in board if ch == "X" or ch == "O"])%2==0 else "O"
"""
def main():
    board = '.'*27+'OX......XO'+'.'*27
    token = find_next_token(board)
    if len(sys.argv) > 2: #if two args
        if len(sys.argv[1]) == 1:
            token = sys.argv[1].upper()
            board = sys.argv[2].upper()
        else:
            token = sys.argv[2].upper()
            board = sys.argv[1].upper()
        if token != find_next_token(board):
            print("Token input error")
    elif len(sys.argv) == 2: #one arg
        if len(sys.argv[1]) == 1:
            token = sys.argv[1].upper()
        else:
            board = sys.argv[1].upper()
            token = find_next_token(board)

    print("Starting board:")
    pieces = s_board_to_bitboard(board)
    display_board(pieces)
    b_token = s_token_to_bit(token)
    next_moves = get_poss(pieces, b_token)
    display_bitboard(next_moves)
    if next_moves:
        print("Possible moves for {}:".format(token))
        print(bit_moves_to_s_moves(next_moves))
    else:
        print("No moves possible for {}.".format(token))
    brd_lst = list(board)
    for move in bit_moves_to_s_moves(next_moves):
        brd_lst[move] = "*"
    display_board(''.join(brd_lst))
"""

def main():
    board = '.'*27+'OX......XO'+'.'*27
    token = 'X'
    print("starting board:")
    pieces = s_board_to_bitboard(board)
    b_tkn = s_token_to_bit(token)

    pieces = place(pieces, b_tkn, 19)
    display_board(pieces)
    poss = get_poss(pieces, b_tkn)
    if poss:
        print("Possible moves for {}:".format(token))
        print(bit_moves_to_s_moves(poss))
    else:
        print("No moves possible for {}.".format(token))



if __name__ == '__main__':
    main()
    #display_bitboard(RIGHT_MASK)
