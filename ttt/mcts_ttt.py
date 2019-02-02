import random, sys, time
from math import log, sqrt
import pickle

#game logic
N = 3
ROWS = [{i for i in range(shift, shift+N)} for shift in range(0, N*N, N)]
COLS = [{i for i in range(N*N) if i%N==rem} for rem in range(N)]
DIAGS = [{i for i in range(N*N) if (i%N)==(i//N)}, {i for i in range(N*N) if (i%N)-(i//N) == (N-1) or (i%N)-(i//N) == -1*(N-1) or (i%N==i//N and i%N==(N//2))}]

def start():
    return "."*9

def find_next_token(board):
    return "O" if board.count("X") > board.count("O") else "X"

def place(board, token, index):
    temp = list(board)
    temp[index] = token
    return ''.join(temp)

def get_poss(board): #pass last state of state_history
    return {i for i in range(len(board)) if board[i] == "."}

def is_terminal(board): #pass last state of state_history
    x_pos = {i for i in range(len(board)) if board[i] == "X"}
    o_pos = {i for i in range(len(board)) if board[i] == "O"}
    #print(x_pos, o_pos)
    for win_condition in ROWS+COLS+DIAGS:
        if win_condition.issubset(x_pos):
            return "X"#1 #X wins
        if win_condition.issubset(o_pos):
            return "O" #-1 #O wins
    if "." not in board:
        return -1 #0 #tie
    return 0 #None #game not terminal

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
        self.max_depth = 0
        self.C = kwargs.get('C', 1.4)

        self.cached = saved if saved else ({}, {}) #reward, plays
        self.reward = self.cached[0]
        self.plays = self.cached[1]

    def find_best_move(self):
    #find next best move based on current tree
        #state = self.state_history[-1]
        state = self.current_state
        token = find_next_token(state)
        poss = get_poss(state)

        #if no moves or only one, no thinking needed
        if not poss:
            return
        if len(poss) == 1:
            return poss.pop()

        #decisive/anti-decisive moves
        #this is kind of tic-tac-toe specific bc so much of optimal play
        #is just decisive/anti-decisive moves
        """
        for move in poss:
            #if immediate win, play it
            temp_state = place(state, token, move)
            w = is_terminal(temp_state)
            if w == token:
                return move
            #if can prevent opponent from immediate win, do it
            opp = "X" if token == "O" else "O"
            temp_state = place(state, opp, move)
            w = is_terminal(temp_state)
            if w == opp:
                return move
        """
        #simulating games to find next move
        games_played = 0
        start_time = time.time()
        while time.time()-start_time < self.time_given-0.01:
            self.run_simulation()
            games_played += 1

        #print(self.plays)
        #print(self.reward)

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

    def run_simulation(self): #light playout
    #play a random game from current state, update stats
        #plays, reward = self.plays, self.reward #apparently local lookup faster than classvar lookup

        seen_states = set()
        #my_history = self.state_history[:] #important not to mess up state_history
        #state = my_history[-1] #current state
        #token = find_next_token(state) #token of the next state after move played (not of current state)
        board = self.current_state
        expand = True
        for d in range(self.max_lookahead):
            token = find_next_token(board) #update token before next state played thru
            poss = get_poss(board)
            moves_to_states = [(move, place(board, token, move)) for move in poss]

            if all(self.plays.get((move, state)) for move, state in moves_to_states): #if all moves/states seen, use known best
                log_total = log(sum(self.plays[(token, state)] for move, state in moves_to_states))
                value, move, state = max( \
                    (self.reward[(token, state)]/self.plays[(token, state)] + \
                    self.C * sqrt(log_total/self.plays[(token, state)]), move, state) \
                    for move, state in moves_to_states \
                )
            else:
                move = random.sample(poss, 1).pop()
                #print('temp: ',move, poss)
                state = place(board, token, move)

            """
            move = random.sample(poss, 1).pop()
            state = place(state, token, move)
            """
            board = state

            #token that GOT TO a certain state stored
            if expand and (token, state) not in self.plays: #expand until a leaf node is hit
                expand = False
                self.plays[(token, state)] = 0
                self.reward[(token, state)] = 0
                if d > self.max_depth:
                    self.max_depth = d

            seen_states.add((token, state))

            #token = find_next_token(state) #update token bc next loop will go thru states a move down
            winner = is_terminal(board)
            if winner: #end if terminal game reached
                break

        for tkn, state in seen_states:
            #if state == 'OX.X.OOX.':
            #    print(tkn, state)
            if (tkn, state) not in self.plays:
                continue
            self.plays[(tkn, state)] += 1
            if winner == -1: #draw
                self.reward[(tkn, state)] += 1 #trying to get it to prefer draws to losses
            elif winner == tkn:
                self.reward[(tkn, state)] += 1.5
            else:
                self.reward[(tkn, state)] -= 1

def display_board(board):
    ret = '\n'
    for i in range(N-1):
        row = board[i*N:(i+1)*N]
        for ch in range(len(row)-1):
            ret += row[ch] + "|"
        ret += str(row[-1])
        ret += "\n"+"-"*(N*2-1)+"\n"
    row = board[N*N-N:]
    for ch in range(len(row)-1):
        ret += row[ch] + "|"
    ret += str(row[-1])
    ret+"\n"
    print(ret)
    print()
"""
test = {1:2, 3:4, 5:6}
f = open('test', 'wb')
pickle.dump(test, f)
f.close()

f = open('test', 'rb')
input = pickle.load(f)
f.close()
print(input)
print(test==input)
print(type(input))
"""
#driver = Game()
board = start()
TIME_INPUT = float(sys.argv[1]) if len(sys.argv) > 1 else 5
while not is_terminal(board):
    try:
        f = open('cached_tree.pkl', 'rb')
        saved = pickle.load(f)
        f.close()
    except FileNotFoundError:
        saved = None

    #saved = None #caching tree doesn't really fix anything. twas the heuristic change that did it
    display_board(board)
    token = find_next_token(board)
    print(board, token)
    mc = MonteCarlo(saved, brd=board, time=TIME_INPUT) #decisive moves OP
    best_move = mc.find_best_move()
    print(best_move, token)
    board = place(board, token, best_move)

print('final')
display_board(board)
print(is_terminal(board))
