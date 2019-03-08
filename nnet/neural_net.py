import numpy as np
from keras.models import *
from keras.layers import *
from keras.optimizers import *
from game import *
import os, time, random

def flip_index_pos(normal_list):
    input = np.array(normal_list[:64]).reshape(8,8)
    return list(np.rot90(np.fliplr(input), -1).flat)+[normal_list[64]]

def flip_index_neg(normal_list):
    input = np.array(normal_list[:64]).reshape(8,8)
    return list(np.rot90(np.fliplr(input), 1).flat)+[normal_list[64]]

def flip_index_both(normal_list):
    input = np.array(normal_list[:64]).reshape(8,8)
    return list(np.rot90(np.fliplr(np.rot90(np.fliplr(input), -1)), 1).flat)+[normal_list[64]]

class NeuralNet():
    def __init__(self):
        #input/output consts
        board_size = 8
        output_actions = 65 #64 squares + pass
        #nnet consts
        #mostly from https://github.com/suragnair/alpha-zero-general/blob/master/othello/keras/NNet.py
        self.dropout_rate = 0.3
        self.alpha = 0.001 
        self.epochs = 10
        self.batch_size = 64
        self.hidden_layer = 512 #maybe decrease to 256 and increase layer num?
        #nnet structure:
        #similar to https://github.com/suragnair/self.alpha-zero-general/blob/master/othello/keras/OthelloNNet.py
        #consists of 5 blocks of convolutions with batch_norm and relu applied
        #followed by flattening for correct output state
        #with dropout applied to avoid overfitting

        #input is state (which is board and token bit)
        #output is pi (vector of len 65) and v (-1 to +1)

        #conv blocks
        input_state = Input(shape=(board_size, board_size, 1))
        conv_block_1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', data_format="channels_last", use_bias=False)(input_state)))
        conv_block_2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_1)))
        conv_block_3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_2)))
        conv_block_4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_3)))
        conv_block_5 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_4)))
        #flatten so data is usable
        flat = Flatten()(conv_block_5)
        #prevent overfitting
        drop_norm_1 = Dropout(self.dropout_rate)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024, use_bias=False)(flat))))
        drop_norm_1 = Dropout(self.dropout_rate)(Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(drop_norm_1))))
        #outputs
        pi = Dense(output_actions, activation='softmax', name='pi')(drop_norm_1)
        v = Dense(1, activation='tanh', name='v')(drop_norm_1)
        #piece together layers
        self.model = Model(inputs=input_state, outputs=[pi, v])
        self.model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=Adam(self.alpha))
        print("NNet instantiated, hyperparameters:")
        print(self.dropout_rate)
        print(self.alpha)
        print(self.epochs)
        print(self.batch_size)
        print(self.hidden_layer)
        print("conv blocks:", 5)
        print("drop_norm_blocks:", 2)
        print()

    #1 is token to move, -1 is opp, 0 is unoccupied
    #input: bitboards
    #output: 8x8x1 numpy array
    def state_to_arr(self, state):
        pieces, token = state
        board = [0 for i in range(64)]
        token_s = format(pieces[token], '064b')
        opp_s = format(pieces[(~token&1)], '064b')
        for i in range(64):
            if token_s[i] == '1':
                board[i] = 1
            elif opp_s[i] == '1':
                board[i] = -1
        a = np.array(board)
        return np.reshape(a, (8,8,1)) #make 3D

    #takes list of examples in form:
    #   (state, probs, eval)
    #only takes a sample of the example set
    def train(self, examples):
        x_boards = []
        y_pis = []
        y_vs = []
        for state, pi, v in examples:
            #print(state)
            #print(pi)
            #print(v)
            #random reflections
            pieces, token = state
            refl = random.randint(1,4)
            if refl == 1:
                refl_state = state
                refl_pi = pi
            elif refl == 2:
                refl_state = (flip_board_neg(pieces), token)
                refl_pi = flip_index_neg(pi)
            elif refl == 3:
                refl_state = (flip_board_pos(pieces), token)
                refl_pi = flip_index_pos(pi)
            else:
                refl_state = (flip_board_both(pieces), token)
                refl_pi = flip_index_both(pi)

            x_boards.append(self.state_to_arr(refl_state))
            y_pis.append(np.array(refl_pi))
            y_vs.append(np.array(v))
        self.model.fit(x=np.array(x_boards), y=[y_pis, y_vs], batch_size=self.batch_size, epochs=self.epochs)

    #takes state, returns probs, eval
    def assess(self, state):
        #start_time = time.time()
        board = self.state_to_arr(state)
        #print(board)
        pi, v = self.model.predict(board.reshape(1,8,8,1)) #batch size of 1
        #print(pi, v)
        #print("assess time", time.time()-start_time)
        return pi[0], v[0]

    #saves current weights to folder/filename
    def save_model(self, folder='saved_nnets', filename="latest_weights.h5"):
        if not filename.endswith(".h5"):
            filename += ".h5"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(folder):
            os.mkdir(folder)
        print("Saving weights to:", filepath)
        self.model.save_weights(filepath) #just saves weights bc architecture is defined in init

    #loads weights from folder/filename
    def load_model(self, folder='saved_nnets', filename="latest_weights.h5"):
        if not filename.endswith(".h5"):
            filename += ".h5"
        filepath = os.path.join(folder, filename)
        if not os.path.exists(filepath):
            print("No model exists on:", filepath)
            return
        print("Loading weights from:", filepath)
        self.model.load_weights(filepath) #not sure if should just save weights or not
