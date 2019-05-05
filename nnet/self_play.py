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
        g1, log1 = play_game(a, b, False)
        g2, log2 = play_game(b, a, False)
        if g1 == 1:
            wins += 1
        if g2 == 1:
            wins += 1
        value += g1 + g2
        print("results: ", g1, g2)
    return wins/games, value/games #start player win pct

#pits one player against itself for training_examples
#then trains said player with random examples from games
def run_training_episode(player, games=1000):
    model = player.model
    #play games
    training_examples = load_training_examples() #will return empty list if none
    if len(training_examples) > (games*10)*60:
        print("training history cleared")
        training_examples = [] #clear history if games are too old
    for i in range(games):
        print(i)
        examples, log = play_game(player, player)
        training_examples += examples #combine training_examples together
        if games-i <= games*0.01:
            print("saving game", i)
            save_game_log(game_log, filename=str(int(time.time()))) #save last 1% of games

    #save games after episode
    save_training_examples(training_examples)
    #train nnet
    batch = random.sample(training_examples, games)
    train_model(model, batch)
    # save_model(model)

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
    game_log = []
    while is_terminal(state) == -2:
        board, token = state
        if verbose:
            print('mod')
            display_board(board)
            print(state)
        move, probs = players[token].get_best_move(state)
        game_log.append(move)
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
        return training_examples, game_log
    else:
        return eval, game_log #give a win/loss/tie from start player's perspective

def save_game_log(game_log, folder='saved_games', filename='last_games.gml'):
    if not filename.endswith(".gml"):
        filename += ".gml"
    filepath = os.path.join(folder, filename)
    if not os.path.exists(folder):
        os.mkdir(folder)
    print("Saving last {} games to: {}".format(len(game_log), filepath))
    f = open(filepath, 'wb')
    pickle.dump(game_log, f)
    f.close()

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

#running batches of self-play for training followed by self-play for eval
def main():
    #hyperparameters
    C = 1.414
    iters = 25
    stm = 15
    training_games = 10
    eval_games = 20
    win_thresh = 0.55

    print("creating models")
    old_model = create_model()
    player_model = create_model()
    old_model.set_weights(player_model.get_weights())
    # self_player = Player(player_model, C=C, it=iters, stm=stm)

    # self_player = Player(NeuralNet(), C=C, it=iters, stm=stm)
    # last_nnet = NeuralNet()
    # last_nnet.model.set_weights(self_player.nnet.model.get_weights())

    #opp = Rand_Player()
    opp = Rand_MCTS(C=C, it=iters, stm=stm)
    while True:
        self_player = Player(player_model, C=C, it=iters, stm=stm)
        print("training started")
        #run a training episode (self play followed by nnet training)
        ep_start = time.time()
        run_training_episode(self_player, training_games) #saves model
        print("training ep time:", time.time()-ep_start)

        #double check
        print("are nnet models same?")
        print(player_model.get_weights()[1][0]==old_model.get_weights()[1][0])

        #plays random as benchmark
        ad_start = time.time()
        win_pct, value = run_adversarial_episode(self_player, opp, eval_games)
        print("vs. random MCTS:")
        print(win_pct, value)
        print("Ad time:", time.time()-ad_start)

        #plays itself to see improvement
        ad_start = time.time()
        win_pct, value = run_adversarial_episode(self_player, Player(old_model, C=C, it=iters, stm=stm), eval_games)
        print("vs. past self:")
        print(win_pct, value)
        print("Ad time:", time.time()-ad_start)

        if win_pct > win_thresh: #keep updated model
            print("keep updated nnet")
            old_model.set_weights(player_model.get_weights())
        else: #revert training
            print("reverting nnet")
            player_model.set_weights(old_model.get_weights())

        #print time for one iteration
        print("\nfull training block time: ", time.time()-ep_start)
        print()

if __name__ == '__main__':
    main_start = time.time()
    main()
    print("Total time: ", time.time()-main_start)
