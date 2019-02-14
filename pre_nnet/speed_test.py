import time
bit_setup_start = time.time()
EMPTY_BOARD = 0x00000000000000
FULL_MASK = 0xffffffffffffffff #cuts off overflow to negatives
LEFT_MASK = 0xfefefefefefefefe #nothing can go left into right col
RIGHT_MASK = 0x7f7f7f7f7f7f7f7f #nothing can go right into left col
bit_setup_time = time.time()-bit_setup_start

pieces = (0x00000810000000, 0x00001008000000)
board = '.'*27+'OX......XO'+'.'*27

setup_start = time.time()
N = 8
#all in order
ROWS = [[i for i in range(shift, shift+N)] for shift in range(0, N*N, N)] #top to bottom
COLS = [[i for i in range(m, N*N, N)] for m in range(N)] #left to right
POS = [[i for i in range(N*N) if i//N+i%N == d] for d in range(N*2-1)] #top left down to bottom right
NEG = [[i for i in range(N*N) if N+(i%N-i//N)-1 == d] for d in range(N*2-1)] #bottom left up to top right
CSTRS = ROWS + COLS + POS + NEG

POS_TO_CSTRS = {i:[] for i in range(N*N)} #each pos has 4 tuples, of (cstr_set, index of move in cstr_set)
for i in range(N*N):
    for r in range(len(ROWS)):
        if i in ROWS[r]:
            POS_TO_CSTRS[i].append((ROWS[r], ROWS[r].index(i)))
    for c in range(len(COLS)):
        if i in COLS[c]:
            POS_TO_CSTRS[i].append((COLS[c], COLS[c].index(i)))
    for p in range(len(POS)):
        if i in POS[p]:
            POS_TO_CSTRS[i].append((POS[p], POS[p].index(i)))
    for n in range(len(NEG)):
        if i in NEG[n]:
            POS_TO_CSTRS[i].append((NEG[n], NEG[n].index(i)))

def get_nbrs(pos):
    #left, right, up, down, upper-left, upper-right, lower-left, lower-right
    nbrs = {pos-1, pos+1, pos-N, pos+N, pos-N-1, pos-N+1, pos+N-1, pos+N+1}
    if pos in ROWS[0]: #top row
        nbrs -= {pos-N, pos-N-1, pos-N+1} #remove aboves
    if pos in ROWS[N-1]: #bottom row
        nbrs -= {pos+N, pos+N-1, pos+N+1}
    if pos in COLS[0]: #left col
        nbrs -= {pos-1, pos-N-1, pos+N-1}
    if pos in COLS[N-1]: #right col
        nbrs -= {pos+1, pos-N+1, pos+N+1}
    return nbrs
POS_TO_NBRS = {i:get_nbrs(i) for i in range(N*N)}
setup_time = time.time()-setup_start

#is there a way to make get_poss return corners at front of set?
def get_poss(board, token): #improvement from lab_1 (not updated for labs 2-4)
    poss = set()
    opp = "O" if token == "X" else "X"
    useful = set()
    for pos in range(len(board)):
        ch = board[pos]
        if ch != ".": continue
        for nbr in POS_TO_NBRS[pos]:
            if board[nbr] == opp:
                useful.add((pos, nbr))
    for hole_pos, opp_pos in useful: #holes with opp adjacent, meaning possible poss members
        sim_cstr_set = [] #find sim cstr_set
        move_pos = -1
        for cstr_set, mp in POS_TO_CSTRS[hole_pos]:
            if opp_pos in cstr_set:
                sim_cstr_set = cstr_set
                move_pos = mp
                break
        #print(hole_pos, opp_pos, sim_cstr_set)
        if opp_pos > hole_pos: #either right or down
        #    print(sim_cstr_set[sim_cstr_set.index(hole_pos)+1:], sim_cstr_set.index(hole_pos)+1)
            for pos in sim_cstr_set[move_pos+1:]:
                ch = board[pos]
        #        print("\t", ch)
                if ch == token:
                    poss.add(hole_pos)
                    break
                if ch == ".": break
        else: #either left or up
        #    print(sim_cstr_set[:sim_cstr_set.index(opp_pos)][::-1], sim_cstr_set.index(opp_pos))
            for pos in sim_cstr_set[:move_pos-1][::-1]:
                ch = board[pos]
        #        print("\t", ch)
                if ch == token:
                    poss.add(hole_pos)
                    break
                if ch == ".": break
    return poss


def bit_poss_to_moves(bit_moves):
    moves = set()
    s = format(bit_moves, '064b')
    for i in range(64):
        if s[i] == '1':
            moves.add(i)
    return moves

#move a candidate fliter by 1 step in dir,
#see if candidates match the criteria of having opp token,
#if no but end tile is empty, add to moves, if no but end tile is full, ignore
#apply masking as needed to keep in bounds
def get_bit_poss(pieces, token):
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

    return bit_poss_to_moves(moves)

trials = 10000
bit_start = time.time()
for i in range(trials):
    get_bit_poss(pieces, 0)
print("Bit time:", time.time()-bit_start)
print("setup:", bit_setup_time)

s_start = time.time()
for i in range(trials):
    get_poss(board, "X")
print("S time:", time.time()-s_start)
print("setup:", setup_time)
