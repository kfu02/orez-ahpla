import sys, time, random
from math import log
from game import *
from neural_net import *
from numpy.random import choice #for weighted prob choice
global_start_time = time.time()

def rand_policy(poss):
    prob = 1/len(poss)
    return [prob for move in poss]

#intending to call this with < 10 moves left
#only for comp play
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

class Player(object): #MCTS combined with nnet policy/evals
    def __init__(self, nnet, **kwargs):
        self.nnet = nnet
        self.move_time = kwargs.get('time', 5) #seconds
        self.C = kwargs.get('C', 4) #higher exploration than normal (sqrt2)
        self.iterations = kwargs.get('it', 25)
        self.stoch_moves = kwargs.get('stm', 15)
        #nodes (states) hold poss moves
        #edges (state, move from state) hold N, W, Q, P vals
        self.nodes = {}
        self.edges = {}
        self.terms = {}

    #find prob vector, return a move and that vector
    #details below
    def get_best_move(self, state, competitive=False):
        start = time.time()
        pieces, token = state
        moves_made = format((pieces[0]|pieces[1]), '064b').count('1')-4
        if competitive and moves_made <= 10:
            return alphabeta(state, -65, 65) #let alphabeta pick the move

        if competitive:
            #mcts until no time
            #it = 0
            while time.time()-start < self.move_time-0.2:
            #    it += 1
                self.search_to_leaf(state)
            #print('mcts iterations:', it)
        else:
            for i in range(self.iterations):
                self.search_to_leaf(state)

        poss = self.nodes.get(state, {})
        #print("player")
        #print(state)
        #print(poss)
        #return a prob vector that has probs for all moves (non-poss means pass forced)
        if not poss:
            return 65, [0 for _ in range(64)]+[1] #100% chance of a pass

        total_N = 0
        for move in poss:
            edge = self.edges[(state, move)]
            total_N += edge[0]
        probs = [0 for _ in range(65)] #64 moves, 1 pass
        for move in poss:
            edge = self.edges.get((state, move), 0)
            probs[move] = edge[0]/total_N

        #play deterministically after first 15 moves (play highest probability)
        if moves_made > self.stoch_moves or competitive:
            max_prob = -1
            best_move = -1
            for move in range(65):
                if probs[move] > max_prob:
                    max_prob = probs[move]
                    best_move = move
        #first 15 moves, explore stochastically (weighted rand sample from prob dist)
        else:
            best_move = choice([i for i in range(65)], 1, p=probs).item() #thanks numpy
        # print(best_move)
        return best_move, probs

    #searches until leaf hit, needs to be called by a loop to set time/iterations
    #state = (board, token)
    def search_to_leaf(self, state):
        selected_edges = set()
        eval = 0
        while True:
            if state not in self.nodes: #leaf, expand
                poss = get_poss(state)
                if state not in self.terms:
                    self.terms[state] = is_terminal(state, poss)
                term = self.terms[state]
                if term != -2:
                    eval = term #-1, 0, 1
                    break #no edges to expand

                if not poss: #not term but no moves = pass
                    state = (state[0], ~state[1]&1)
                    break

                probs, eval = self.nnet.assess(state)
                #print(eval)
                # print('yes')
                # print(probs)
                # print(probs.shape)
                # print(eval)
                # print(eval.shape)
                #probs, eval = rand_policy(poss), random.random()*128-64
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

#for testing
class Rand_Player(object):
    def get_best_move(self, state, competitive=False):
        poss = get_poss(state)
        if poss:
            return random.choice(poss), []
        else:
            return -1, []

if __name__ == '__main__':
    player = Player(NeuralNet())
    m = player.get_best_move((start(), 0))
    print(m)
    print("time taken:", time.time()-global_start_time)
