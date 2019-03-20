from neural_net import *
from player import *
from game import *
import os, time, pickle, random

from keras.models import *

#takes two players
def run_adversarial_episode(a, b, games=100):
    wins = 0
    value = 0
    for i in range(games//2):
        print(i)
        g1 = play_game(a, b, False)
        g2 = play_game(b, a, False)
        if g1 == 1:
            wins += 1
        if g2 == 1:
            wins += 1
        value += g1 + g2
        print("results: ", g1, g2)
    return wins/(2*games), value/(2*games) #start player win pct

#pits one player against itself for training_examples
#then trains said player with random examples from games
def run_training_episode(player, games=1000):
    nnet = player.nnet
    #play games
    training_examples = load_training_examples() #will return empty list if none
    if len(training_examples) > (games*10)*60:
        print("training history cleared")
        training_examples = [] #clear history if games are too old
    for i in range(games):
        print(i)
        training_examples += play_game(player, player)
    #save games after episode
    save_training_examples(training_examples)
    #train nnet
    batch = random.sample(training_examples, games)
    nnet.train(batch)
    nnet.save_model()

#takes two instantiated players and plays a game between them from start to finish
#return type changes depending on training flag
#if true, returns training_examples taken from mcts trees
#if false, returns final eval of board (for win/loss counting)
def play_game(a, b, training=True, verbose=False):
    game_start = time.time()
    if training:
        training_examples = []
    state = (start(), 0)
    players = [a, b]
    while is_terminal(state) == -2:
        board, token = state
        if verbose:
            print('mod')
            display_board(board)
            print(state)
        move, probs = players[token].get_best_move(state)
        if verbose:
            print(move)
            print(probs)
            print()
        if training:
            training_examples.append([state, probs, None])
        #update state (make move on board, switch token)
        if move == 65:
            state = (board, ~token&1)
        else:
            state = (place(state, move), ~token&1)

    #-1, 1, or 0
    #corresponding to loss/win/tie from start player's perspective
    print("last game (s): ", time.time()-game_start)
    eval = is_terminal(state)
    if verbose:
        display_board(state[0])
        print(state)
        print(eval)
    if training:
        for tup in training_examples:
            #print(tup[0][1])
            if tup[0][1] == state[1]: #if matches final token, keep that eval
                tup[2] = eval
            else: #otherwise flip it
                tup[2] = -eval
        return training_examples
    else:
        return eval #give a win/loss/tie from start player's perspective

def save_training_examples(training_examples, folder='saved_examples', filename="latest_examples.exmp"):
    if not filename.endswith(".exmp"):
        filename += ".exmp"
    filepath = os.path.join(folder, filename)
    if not os.path.exists(folder):
        os.mkdir(folder)
    print("Saving training examples to:", filepath)
    f = open(filepath, 'wb')
    pickle.dump(training_examples, f)
    f.close()

def load_training_examples(folder='saved_examples', filename="latest_examples.exmp"):
    if not filename.endswith(".exmp"):
        filename += ".exmp"
    filepath = os.path.join(folder, filename)
    if not os.path.exists(filepath):
        print("No weights exist on:", filepath)
        return []
    print("Loading training examples from:", filepath)
    f = open(filepath, 'rb')
    saved = pickle.load(f)
    f.close()
    return saved

#constantly updating rather than running batches of self-play for training followed by self-play for eval
def main():
    #hyperparameters for Player
    C = 1.414
    iters = 25
    stm = 15

    self_player = Player(NeuralNet(), C=C, it=iters, stm=stm)
    last_nnet = NeuralNet()
    last_nnet.model.set_weights(self_player.nnet.model.get_weights())

    #opp = Rand_Player()
    opp = Rand_MCTS(C=C, it=iters, stm=stm)
    while True:
        print("training started")
        #run a training episode (self play followed by nnet training)
        ep_start = time.time()
        run_training_episode(self_player, 1) #saves model
        print("training ep time:", time.time()-ep_start)

        #double check
        print("are nnet models same?")
        print(self_player.nnet.model.get_weights()[1][0]==last_nnet.model.get_weights()[1][0])

        #plays random as benchmark
        ad_start = time.time()
        win_pct, value = run_adversarial_episode(self_player, opp, 1)
        print("vs. random MCTS:")
        print(win_pct, value)
        print("Ad time:", time.time()-ad_start)

        #plays itself to see improvement
        ad_start = time.time()
        win_pct, value = run_adversarial_episode(self_player, Player(last_nnet, C=C, it=iters, stm=stm), 1)
        print("vs. past self:")
        print(win_pct, value)
        print("Ad time:", time.time()-ad_start)

        if win_pct > 0.55: #keep updated model
            print("keep updated nnet")
            last_nnet.model.set_weights(self_player.nnet.model.get_weights())
        else: #or revert
            print("reverting nnet")
            self_player.nnet = NeuralNet()
            self_player.nnet.model.set_weights(last_nnet.model.get_weights())

        #print time for one iteration
        print("\nfull training block time: ", time.time()-ep_start)
        print()

if __name__ == '__main__':
    main_start = time.time()
    main()
    print("Total time: ", time.time()-main_start)

"""
if __name__ == '__main__':
    player_a = Player(NeuralNet())
    player_b = Player(NeuralNet())
    start_time = time.time()
    play_game(player_a, player_b)
    print('time for one game', time.time()-start_time) #~3 min on my laptop
"""
