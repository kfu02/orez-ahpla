def display_bitboard(bitboard):
    str_b = format(bitboard, '064b')
    for i in range(8):
        print(str_b[i*8:(i+1)*8])
    print()

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

def main():
    bb = 0x8100000000000000
    display_bitboard(bb)
    display_bitboard(flip_neg_diag(bb))
    display_bitboard(flip_pos_diag(bb))
    display_bitboard(flip_both(bb))

if __name__ == '__main__':
    main()
