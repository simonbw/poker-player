from player import Player
from card import Card
import time

class Human(Player):

    def __init__(self, name):
        self.name = name

    def bet(self, game_view):
        """
        Called when asking how much a player would like to bet.
        Returning None folds.
        """
        g = game_view
        print('Action to you', self.name)
        print('You have', g.my_chips, 'chips.')
        print('Your cards are:', Card.int_to_str(g.hole_cards[0]), Card.int_to_str(g.hole_cards[1]))
        prompt = ("It's {0} to stay in and minimum raise is {1}." 
                    + "\nWhat would you like to do? " 
                    + "").format(g.min_bet if g.min_bet > 0 else 'free', g.minimum_raise)
        n = input(prompt).split(' ')
        if len(n) == 1:
            action = n[0]
        else:
            action, amount = n

        if action == 'fold':
            return None
        if action == 'check':
            return 0
        if action == 'call':
            return g.min_bet
        if action in ('raise', 'bet'):
            return max(g.min_bet, g.min_raise, int(amount))


        return None

    def on_bet(self, player_name, action, amount, game_view):
        """
        Called when another player makes a bet.
        @param player_name - unique name of the player 
        @param action - One of the strings: "check" "call" "fold" "raise"
        @param amount - The amount put in to call or the amount raised by or None (fold).
        @param game_view - A game view with all the data.
        """
        #time.sleep(2)

    def on_new_round(self, game_view):
        """Called at the beginning of a new round of betting."""
        pass

    def on_new_hand(self, game_view):
        """Called at the beginning of a new hand."""
        pass

    def on_new_game(self, players):
        """Called at the beginning of a new game."""
        pass

    def on_bust(self):
        time.sleep(120)