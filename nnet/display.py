EMPTY_BOARD = 0x00000000000000

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
