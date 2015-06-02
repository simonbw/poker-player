from player import Player
from evaluator import Evaluator

class CallingStation(Player):
    def __init__(self, name):
        self.name = name
        evaluator = Evaluator()

    def bet(self, game_view):
        return min(game_view.amount_to_stay_in, game_view.my_chips)

    def update(self, game_view):
    	return