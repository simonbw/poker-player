from player import Player
from evaluator import Evaluator

class Bluffer(Player):
    def __init__(self, name):
        self.name = name
        evaluator = Evaluator()

    def bet(self, game_view):
        return min(game_view.my_chips, game_view.minimum_bet + game_view.minimum_raise)

    def update(self, game_view):
    	return