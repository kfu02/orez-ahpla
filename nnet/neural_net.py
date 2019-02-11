import numpy as np
from keras.models import *
from keras.layers import *
from keras.optimizers import *
#need to build a neural net that takes in board states and outputs prob vectors and values of the board
class NeuralNet():
    def __init__(self):
        #input/output consts
        board_size = 8
        output_actions = 65 #64 squares + pass
        #other consts
        self.dropout_rate = 0.1
        self.alpha = 0.01
        self.epochs = 10
        self.batch_size = 100
        self.hidden_layer = 512
        #nnet: similar to https://github.com/suragnair/self.alpha-zero-general/blob/master/othello/keras/OthelloNNet.py
        #consists of 5 blocks of convolutions with batch_norm and relu applied
        #followed by some dropout and batch_norm to get it to the right output state
        #input is state (which is board and token bit)
        #output is pi (vector of len 65) and v (-1 to +1)
        #conv blocks
        input_state = Input(shape=(board_size, board_size, 1))
        print(input_state.shape)
        conv_block_1 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', data_format="channels_last", use_bias=False)(input_state)))
        print(conv_block_1.shape)
        conv_block_2 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_1)))
        print(conv_block_2.shape)
        conv_block_3 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_2)))
        print(conv_block_3.shape)
        conv_block_4 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_3)))
        print(conv_block_4.shape)
        conv_block_5 = Activation('relu')(BatchNormalization(axis=3)(Conv2D(self.hidden_layer, 3, padding='same', use_bias=False)(conv_block_4)))
        print(conv_block_5.shape)
        #flatten so data is usable
        flat = Flatten()(conv_block_5)
        #prevent overfitting
        drop_norm_1 = Dropout(self.dropout_rate)(Activation('relu')(BatchNormalization(axis=1)(Dense(1024, use_bias=False)(flat))))
        drop_norm_1 = Dropout(self.dropout_rate)(Activation('relu')(BatchNormalization(axis=1)(Dense(512, use_bias=False)(drop_norm_1))))
        
        pi = Dense(output_actions, activation='softmax', name='pi')(drop_norm_1)
        v = Dense(1, activation='tanh', name='v')(drop_norm_1)

        self.model = Model(inputs=input_state, outputs=[pi, v])
        #shouldn't this be custom loss func?
        self.model.compile(loss=['categorical_crossentropy','mean_squared_error'], optimizer=Adam(self.alpha))

    #1 is token to move, -1 is opp, 0 is unoccupied
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
    #need to convert state ints to np arrays of size 8x8
    def train(self, examples):
        x_boards = []
        y_pis = []
        y_vs = []
        for state, pi, v in examples:
            x_boards.append(self.state_to_arr(state))
            y_pis.append(np.array(probs))
            y_vs.append(np.array(probs))
        self.model.fit(x=x_boards, y=[y_pis, y_vs], batch_size=self.batch_size, epochs=self.epochs)

    #takes state, returns probs, eval
    def assess(self, state):
        board = self.state_to_arr(state)
        #print(board)
        pi, v = self.model.predict(board.reshape(1,8,8,1)) #batch size of 1
        print(pi, v)
        return pi[0], v[0]

    #saves current training to folder/filename
    def save_progress(self, folder, filename):
        pass

    #loads weights from folder/filename
    def load_previous(self, folder, filename):
        pass
