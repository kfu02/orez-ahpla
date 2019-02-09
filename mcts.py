import sys, time, random
from math import log, sqrt
from game import *
from display import *
global_start_time = time.time()

def rand_policy(poss):
    prob = 1/len(poss)
    return [prob for move in poss]

class MonteCarlo(object):
    def __init__(self, **kwargs):
        #self.nnet = nnet
        print('inputs')
        print(kwargs)
        self.current_state = kwargs.get('brd', start()) #tuple now
        self.start_token = kwargs.get('tkn', 0) #starting token of board, X by default
        self.time_given = kwargs.get('time', 10) #10 by default

        self.max_depth = 0
        self.C = kwargs.get('C', 1.414) #sqrt 2

        self.nodes = {} #stores rolling evals (W), visits (N), and nnet evals (P)

    #def get_move_probs(self):
    def run_simulation(self, token):
        board = self.current_state
        #expand
        poss = get_poss(board, token)
        if not poss: #pass, presumably is_terminal called before this so no check needed
            token = ~token & 1
            poss = get_poss(board, token)
        moves_to_states = [(move, place(board, token, move)) for move in poss]
        #select
        #probs = self.nnet.get_policy(board)
        probs = rand_policy(poss)
        for move in poss:
            state = place(board, token, move)
            if (token, state) not in self.nodes:
                #self.nodes[(token, state)] = (0, 0, nnet.eval(state))
                self.nodes[(token, state)] = (0, 0, random.random())
