# orez-ahpla
Alpha Zero algorithm applied to the game Othello (aka Reversi).

Original paper: https://www.nature.com/articles/nature24270.epdf?author_access_token=VJXbVjaSHxFoctQQ4p2k4tRgN0jAjWel9jnR3ZoTv0PVW4gB86EEpGqTRDtpIz-2rmo8-KG06gqVobU5NSCFeHILHcVFUeMsbvwS-lxjqQGg98faovwjxeTUgZAUMnRQ

MCTS framework from: https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

Bitboard algorithm to find possible moves from: http://eprints.qut.edu.au/85005/1/__staffhome.qut.edu.au_staffgroupm$_meaton_Desktop_bits-7.pdf

$_
Bitboard algorithm to reflect over diagonals from: https://www.chessprogramming.org/index.php?title=Flipping_Mirroring_and_Rotating&mobileaction=toggle_view_mobile#FlipabouttheDiagonal

Neural network architecture adapted from: https://web.stanford.edu/~surag/posts/alphazero.html

# Changelog
## 0.1.0 - 2/1/19
### Added
 - Basic implementation of mcts for othello.
 - Basic implementation of mcts for ttt (in /ttt).

## 0.1.1 - 2/1/19
### Added
 - Links to sources used.
 - Punctuation to this log.

### Changed
 - Moved ttt mcts out of /ttt.

### Removed
 - /ttt.

## 0.2.0 - 2/2/19
### Added
 - Bitboard implementation of Othello 1 (show_poss.py, tested with AI Grader).
 - 64-char string to bitboard conversion methods.
 - Display methods for bitboards.

## 0.3.0 - 2/3/19
### Added
 - Bitboard implementation of Othello 3 (make_moves.py, tested with AI Grader).
 - Bitboard to str conversion methods.
 - Bitboard implementation of get_score.

### Changed
 - 0.2.0 README section wording.
 - Streamlined get_poss to match new place method (in make_moves.py).

## 0.3.1 - 2/3/19
### Changed
 - Turned start() and s_board_to_bitboard() into one-liners.

### Removed
 - Debug print/displays in show_poss and make_moves.

## 0.4.0 - 2/3/19
### Added
 - Bitboard implementation of Othello 6 (terminal_alphabeta.py, tested with AI Grader, 93.5).
 - State recursion for get_poss.
 - To-dos.

### Changed
 - Made bit_moves_to_s_moves() return a set rather than a list.
 - get_score() now returns score as a single +/- int from perspective of token rather than a pair of ints.

## 0.4.1 - 2/3/19
### Changed
 - bit_moves_to_s_moves renamed as bit_poss_to_moves.
 - bit_poss_to_moves now integrated into get_poss.

### Removed
 - To-dos (impractical).

## 0.4.2 - 2/3/19
### Added
 - Speed tested bitboard get_poss vs string get_poss (bitwise is faster by a factor of 5, results in speed_test.py).

## 0.4.3 - 2/3/19
### Added
 - Bitboards to check corners and center 4 squares added.

## 0.5.0 - 2/3/19
### Added
 - Bitboard implementation of MCTS (doubled the amount of positions searched in 5 s).

### Changed
 - Tweaked cutoff val from 0.01 to 0.1 in both MCTS searches.
 - Fixed small bug in make_moves.py.

## 0.6.0 - 2/6/19
### Added
 - Bitboard reflections across diagonals implemented.
 - Reflections added to state recursion in get_poss, unsure of speed upgrade.

### Removed
 - To-dos.

## 0.6.1 - 2/6/19
### Removed
 - Bitboard reflections removed from state recursion dicts (was slower).

## 0.7.0 - 2/9/19
### Changed
 - Organized files to start implementing neural net.
 - Fixed UCB-selection in bit_mcts.py.

## 0.8.0 - 2/9/19
### Added
 - New folder (/nnet) for neural net implementation.
 - Modified MCTS to use policy/eval funcs.
 - Separated game and display functions.

### Changed
 - (ONLY IN /NNET)
 - Game methods take a state arg instead of separate board, token args
 - Get_poss returns list

## 0.8.1 - 2/9/19
### Changed
 - (ONLY IN /NNET)
 - Shortened bit_poss_to_moves.
 - Added stochastic play option for early game mcts.

## 0.8.2 - 2/10/19
### Changed
 - Changed is_terminal to return -1, 0, or +1.

## 0.9.0 - 2/11/19
### Added
 - A working neural net for policy/eval funcs (neural_net.py)–currently assesses positions in conjunction with MCTS, albeit randomly.
 - To-do.

## 1.0.0 - 2/13/19
### Added
 - Methods for saving/loading weights of nnet.
 - Self_play.py, which handles the self_play for training the nnet.
 - Methods for saving/loading training_examples from self play.
 - Verbose/training flags for play_game (maybe this method is overloaded...).

### Changed
 - Made get_probs return a list of length 65 for probs.
 - Renamed mcts to player (more accurate).
 - Passes now indicated by 65 rather than -1 (to match prob vector).
 - Combined get_probs with get_best_move for clarity.
 - Merged display into game (no reason for sep file).
 - Reflect funcs now take a state arg rather than a single bitboard arg.

### Removed
 - To-dos.

## 1.0.1 - 2/14/19
### Changed
 - To-dos.

## 1.0.2 - 2/17/19
### Added
 - Reflecting boards/pis for training data.

## 1.0.3 - 2/17/19
### Changed
 - run_adversarial_episode() returns win_pct and win/loss/tie record

## 1.0.4 - 2/17/19
### Added
 - latest_weights.h5 added with git lfs.

### Training Results
 - After 100 games of self_play (~6000 states for training), nnet player beat completely random player in 18/25 games and beat random MCTS based player in 17/25 games.

# To-do
- [ ] Rework state recursion
- [ ] Make sure to sample from game states rather than training network on all of them
- [ ] Make terminal eval of mcts dependent on number of moves taken to get there.
- [ ] Figure out systematic way to load/save/clear training examples
- [ ] Since planning to use terminal_alphabeta competitively, enable for self-play and remove those training examples that alphabeta covers
