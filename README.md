# poker-player
Play a game of poker with some AI.
Written in Python 3.4

Classes for use by your own ai:
- card.py
- deck.py
- lookup.py
- player.py
- evaluator.py

## Usage
Run poker.py from command line.

In poker.py, LOG_LEVEL 1 will print the game. LOG_LEVEL 2 will only print the winner.
In the game class, STARTING_CHIPS, LITTLE_BLIND, and BIG_BLIND adjust their in game meanings.

At the bottom of poker.py, you can adjust how the games actually run and with which AIs.
Here is where you will import your ai to run against others.

### Game_view Object
The Game_view object is the primary method by which an ai sees the game.
Game_view objects are unique for each player.
These are the fields the object has: (note, all cards are as integers defined in card.py)

- hole_cards
  - list of 2 cards that are the player's hole cards
- community_cards
  - list of n cards that are the community cards
- my_chips
  - The amount of chips the player has infront of them
- chips
  - A dictionary mapping from opponent's name -> opponent's chips
- players
  - A list of all the player's names who are in the game still
- players_in_hand
  - A list of all the player's names who haven't folded this hand
- folded_players 
  - A list of players who have folded this hand
- money_for_pot
  - A dictionary mapping from players' names -> money they have in front of them ready for the pot
- big_blind
  - The current big blind
- pot_size
  - The amount of money total in the pot
- min_bet
  - The minimum amount of money required to stay in on this bet
- min_raise
  - The minimum amount the player must raise if she decides to do so. Note that a player may put all their chips into the pot at any betting opportunity.
- players_in_round
  - Same as players_in_hand

## Playing the Human
human.py is used for humans to interface with the game.

'Raise 10' will reduce your chip total by min_bet + 10.
This is assuming 10 >= min_raise.
