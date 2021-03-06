import sys, time
global_start_time = time.time()
N = 8
EMPTY_BOARD = 0x00000000000000
FULL_MASK = 0xffffffffffffffff #cuts off overflow to negatives
LEFT_MASK = 0xfefefefefefefefe #nothing can go left into right col
RIGHT_MASK = 0x7f7f7f7f7f7f7f7f #nothing can go right into left col

def start():
    return 0x00000810000000, 0x00001008000000

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
                moves |= empty & (cand_shift & RIGHT_MASK)
                candidates = pieces[opp] & (cand_shift & RIGHT_MASK)
            elif dir == 7:
                moves |= empty & (cand_shift & LEFT_MASK)
                candidates = pieces[opp] & (cand_shift & LEFT_MASK)
            else:
                moves |= empty & cand_shift
                candidates = pieces[opp] & (cand_shift & FULL_MASK)

        if dir == 1 or dir == 9:
            candidates = pieces[opp] & ((pieces[token] << dir) & LEFT_MASK)
        elif dir == 7:
            candidates = pieces[opp] & ((pieces[token] << dir) & RIGHT_MASK)
        else:
            candidates = pieces[opp] & ((pieces[token] << dir) & FULL_MASK)

        while candidates:
            cand_shift = (candidates << dir)
            if dir == 1 or dir == 9:
                moves |= empty & (cand_shift & LEFT_MASK)
                candidates = pieces[opp] & (cand_shift & LEFT_MASK)
            elif dir == 7:
                moves |= empty & (cand_shift & RIGHT_MASK)
                candidates = pieces[opp] & (cand_shift & RIGHT_MASK)
            else:
                moves |= empty & (cand_shift & FULL_MASK)
                candidates = pieces[opp] & (cand_shift & FULL_MASK)

    return moves

def s_board_to_bitboard(s_board):
    return int(''.join(['1' if ch == "X" else '0' for ch in s_board]), 2), int(''.join(['1' if ch == "O" else '0' for ch in s_board]), 2)

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
    for i in range(N):
        print(str_b[i*N:(i+1)*N])
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
    ret = '-'*(N*2+1)+"\n"
    for i in range(N-1):
        row = board[i*N:(i+1)*N]
        for ch in range(len(row)-1):
            ret += "|" + row[ch]
        ret += "|"+str(row[-1])+"|"
        ret += "\n"+"-"*(N*2+1)+"\n"
    row = board[N*N-N:]
    for ch in range(len(row)-1):
        ret += "|" + row[ch]
    ret += "|"+str(row[-1])+"|\n"
    ret += '-'*(N*2+1)
    print(ret+"\n")

def find_next_token(board):
    return "X" if sum([1 for ch in board if ch == "X" or ch == "O"])%2==0 else "O"

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

if __name__ == '__main__':
    main()
