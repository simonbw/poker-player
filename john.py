from player import Player
from evaluator import Evaluator

class John(Player):
    agent_count = 0

    def __init__(self):
        John.agent_count += 1
        self.name = 'John' + str(John.agent_count)
        evaluator = Evaluator()

    def bet(self, game_view):
        return game_view.chips[self.name]

    def on_bet(self, player_name, action, amount, game_view):
        """
        Called when another player makes a bet.
        @param player_name - unique name of the player 
        @param action - One of the strings: "check" "call" "fold" "raise"
        @param amount - The amount put in to call or the amount raised by or None (fold).
        @param game_view - A game view with all the data.
        """
        pass

    def on_new_round(self, game_view):
        """Called at the beginning of a new round of betting."""
        pass

    def on_new_hand(self, game_view):
        """Called at the beginning of a new hand."""
        pass

    def on_new_game(self, players):
        """Called at the beginning of a new game."""
        pass


class Villain():
    '''Models an opponent'''
    count = 0
    def __init__(self):
        Villain.count += 1
        self.id = Villain.count
        self.vpip = 0

    def update(action, amount, game_view):
        