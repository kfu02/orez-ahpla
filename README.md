# orez-ahpla
Alpha Zero algorithm applied to the game Othello (aka Reversi).

Original paper: https://www.nature.com/articles/nature24270.epdf?author_access_token=VJXbVjaSHxFoctQQ4p2k4tRgN0jAjWel9jnR3ZoTv0PVW4gB86EEpGqTRDtpIz-2rmo8-KG06gqVobU5NSCFeHILHcVFUeMsbvwS-lxjqQGg98faovwjxeTUgZAUMnRQ

MCTS framework from: https://jeffbradberry.com/posts/2015/09/intro-to-monte-carlo-tree-search/

Bitboard algorithm to find possible moves from: http://eprints.qut.edu.au/85005/1/__staffhome.qut.edu.au_staffgroupm$_meaton_Desktop_bits-7.pdf

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
 - Bitboard implementation of get_poss (tested in show_poss.py with AI Grader).
 - 64-char string to bitboard conversion methods.
 - Display methods for bitboards.

# To-do
- [ ] Apply bitboards to mcts
- [ ] Add mcts with policy/eval funcs (feature)
- [ ] Figure out neural net structure for policy/eval funcs
- [ ] Apply neural net to mcts funcs
