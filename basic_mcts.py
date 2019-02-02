import sys, time, random
from math import log, sqrt
#import pickle

global_start_time = time.time()

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

CORNERS = {0, 7, 56, 63}
CORNER_ADJS = {1:0, 8:0, 9:0, 6:7, 15:7, 14:7, 57:56, 48:56, 49:56, 62:63, 55:63, 54:63}
CENTERS = {27, 28, 35, 36}

POSS_CACHE = {} #state recursion for get_poss()
#is there a way to make get_poss return corners at front of set?
def get_poss(board, token): #improvement from lab_1 (not updated for labs 2-4)
    if (board, token) in POSS_CACHE:
        return POSS_CACHE[(board, token)]
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
    POSS_CACHE[(board, token)] = poss
    return POSS_CACHE[(board, token)]

#places given token on given board on given space (move), while checking if move is valid w/ given poss
def place(board, token, move):
    new_board = list(board)
    new_board[move] = token
    opp = "O" if token == "X" else "X"
    for cstr_set, move_pos in POS_TO_CSTRS[move]:
        fwd = ''.join([board[i] for i in cstr_set])
        next_tokens = [i for i in range(len(fwd)) if fwd[i] == token] #board w/out new move
        if len(next_tokens) == 0: continue
        for next_token in next_tokens:
            #if all pieces in between move and closest token are opponent token, flip all those tokens
            #meaning it will stop for any holes or intervening sim tokens
            if next_token > move_pos:
                bound = fwd[move_pos+1: next_token]
                if "." not in bound and token not in bound:
                    for i in range(move_pos+1, next_token):
                        new_board[cstr_set[i]] = token
            else:
                bound = fwd[next_token+1: move_pos]
                if "." not in bound and token not in bound:
                    for i in range(next_token+1, move_pos):
                        new_board[cstr_set[i]] = token
    return ''.join(new_board)

def is_terminal(board):
    x_poss = get_poss(board, "X")
    o_poss = get_poss(board, "O")
    if not x_poss and not o_poss: #game over
        score = board.count("X")-board.count("O")
        if score == 0: return -1 #tie
        return "X" if score > 0 else "O" #return whichever token is the winner
    return 0 #game not over

def switch_turn(token):
    return "O" if token == "X" else "X"

def start():
    return '.'*27+'OX......XO'+'.'*27

#monte carlo tree search
class MonteCarlo(object):
    def __init__(self, saved, **kwargs):
    #takes Game object, keyword args, and initializes game_history and stats dicts accordingly
        print('inputs')
        print(kwargs)
        #self.game = game
        #self.state_history = [kwargs.get('brd', start())] #[start()]
        self.current_state = kwargs.get('brd', start())
        self.time_given = kwargs.get('time', 10) #10 by default
        self.max_lookahead = kwargs.get('max_fwd', 10000)
        self.start_token = kwargs.get('tkn', "X") #starting token of board, X by default
        self.max_depth = 0
        self.C = kwargs.get('C', 1.414) #sqrt 2

        self.reward = {}
        self.plays = {}
        """
        self.cached = saved if saved else ({}, {}) #reward, plays
        self.reward = self.cached[0]
        self.plays = self.cached[1]
        """

    def find_best_move(self):
    #find next best move based on current tree
        state = self.current_state
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
        while time.time()-start_time < self.time_given-0.01:
            self.run_simulation(token)
            games_played += 1

        #print(self.plays)
        #print(self.reward)

        """
        for tup, rwd in self.reward.items():
            if tup not in self.cached[0]:
                self.cached[0][tup] = 0
            self.cached[0][tup] += rwd

        for tup, plys in self.plays.items():
            if tup not in self.cached[1]:
                self.cached[1][tup] = 0
            self.cached[1][tup] += plys

        f = open('cached_tree.pkl', 'wb') #reward, plays
        pickle.dump(self.cached, f)
        f.close()
        """

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
        #my_history = self.state_history[:] #important not to mess up state_history
        #state = my_history[-1] #current state
        #token = find_next_token(state) #token of the next state after move played (not of current state)
        board = self.current_state
        expand = True
        for d in range(self.max_lookahead):
            #token = find_next_token(board) #update token before next state played thru
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
                token = switch_turn(token)
                poss = get_poss(board, token)
            move = random.sample(poss, 1).pop()
            state = place(board, token, move)

            board = state
            #print(board == self.current_state) #check if self.current_state was unintentionally modified
            #token that GOT TO a certain state stored
            if expand and (token, state) not in self.plays: #expand until a leaf node is hit
                expand = False
                self.plays[(token, state)] = 0
                self.reward[(token, state)] = 0
                if d > self.max_depth:
                    self.max_depth = d

            seen_states.add((token, state))

            #token = find_next_token(state) #update token bc next loop will go thru states a move down
            token = switch_turn(token)
            #print(token)
            winner = is_terminal(board)
            if winner: #end if terminal game reached
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

def display_board(board):
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

board = start()
TIME_INPUT = float(sys.argv[1]) if len(sys.argv) > 1 else 5
saved = None
token = "X"
moves_played = []
while not is_terminal(board):
    """
    try:
        f = open('cached_tree.pkl', 'rb')
        saved = pickle.load(f)
        f.close()
    except FileNotFoundError:
        saved = None
    """
    display_board(board)
    #token = find_next_token(board) #doesn't work bc of passes
    #instead, assume no passes unless needed, switch every turn
    if not get_poss(board, token):
        token = switch_turn(token)
    mc = MonteCarlo(saved, brd=board, tkn=token, time=TIME_INPUT)
    best_move = mc.find_best_move()
    moves_played.append(best_move)
    print(board, token, best_move)
    board = place(board, token, best_move)
    token = switch_turn(token)

print('final')
display_board(board)
print(is_terminal(board))
print('moves')
for m in moves_played:
    print(m, end=' ')
print()
