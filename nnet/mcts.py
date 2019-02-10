import sys, time, random
from math import log
from game import *
from display import *
global_start_time = time.time()

def rand_policy(poss):
    prob = 1/len(poss)
    return [prob for move in poss]

#intending to call this with < 10 moves left
#theoretically, could ignore this
def alphabeta(state, lower, upper):
    #pieces, token = state
    poss = get_poss(state)
    if not poss:
        state = (state[0], ~state[1]&1)
        poss = get_poss(state)
        if not poss: #terminal
            return [get_score(state)]
        ab = alphabeta(state, -upper, -lower)
        return [-ab[0]]+ab[1:]+[-1] #token passed, returns opp's eval

    best = [lower-1]
    for move in poss:
        state = (place(state, move), ~state[1]&1)
        ab = alphabeta(state, -upper, -lower)
        score = -ab[0]
        if score > upper: return [score]
        if score < lower: continue
        best = [score]+ab[1:]+[move]
        lower = score+1
    return best

class MonteCarlo(object):
    def __init__(self, nnet, **kwargs):
        self.nnet = nnet
        print('inputs')
        print(kwargs)
        self.move_time = kwargs.get('time', 5) #seconds
        self.C = kwargs.get('C', 1.414) #sqrt 2

        #nodes (states) hold poss moves
        #edges (state, move from state) hold N, W, Q, P vals
        self.nodes = {}
        self.edges = {}

    def pick_move(self, state):
        start = time.time()
        pieces, token = state
        moves_left = 64-str(pieces[0]|pieces[1]).count('1')
        if moves_left <= 10: #count tokens
            return alphabeta(state, -65, 65) #let alphabeta pick the move
        #mcts until no time
        it = 0
        while time.time()-start < self.move_time-0.1:
            it += 1
            self.search_to_leaf(state)
        print('mcts iterations', it)
        #will always pick most-visited node (no stochastical play)
        poss = self.nodes[state]
        best_move = None
        best_N = -1
        for m in poss: #find max N
            edge = self.edges[(state, m)]
            if edge[0] > best_N:
                best_move = m
                best_N = edge[0]
        return best_move

    #searches until leaf hit, needs to be called by a loop to set time/iterations
    #state = (board, token)
    def search_to_leaf(self, state):
        selected_edges = set()
        eval = 0
        while True:
            if state not in self.nodes: #leaf, expand
                poss = get_poss(state)
                term = is_terminal(state, poss)
                if term != -2:
                    eval = term #-64 to +64
                    break #no edges to expand

                if not poss: #not term but no moves = pass
                    state = (state[0], ~state[1]&1)
                    break

                #probs, eval = self.nnet.assess(state)
                probs, eval = rand_policy(poss), random.random()*128-64
                self.nodes[state] = poss
                for i in range(len(poss)):
                    self.edges[(state, poss[i])] = [0, 0, 0, probs[i]]
                break #stop progressing down tree, go to backup

            #expanded before, select best move with puct and continue down tree
            max_puct = -float('inf')
            best_move = None
            poss = self.nodes[state]
            # parent_N = 0
            # for move in poss:
            #     parent_N += self.edges[(state, move)]
            # parent_N /= len(poss)
            parent_N = sum(self.edges[(state, m)][0] for m in self.nodes[state])/len(self.nodes[state])
            for move in poss:
                N, W, Q, P = self.edges[(state, move)]
                U = self.C*P*((parent_N**0.5)/(1+N)) if parent_N else 0
                puct = Q+U
                if puct > max_puct:
                    max_puct = puct
                    best_move = move
            selected_edges.add((state, best_move)) #track choice for backup
            state = (place(state, best_move), ~state[1]&1) #move state one down, flip token

        #backup stats for selected_edges
        for edge in selected_edges:
            stats = self.edges[edge]
            stats[0] += 1
            stats[1] += eval
            stats[2] = stats[1]/stats[0]

player = MonteCarlo(None)
m = player.pick_move((start(), 0))
print(m)
