from player import Player
from evaluator import Evaluator

class Bluffer(Player):
    agent_count = 0
    def __init__(self):
        Bluffer.agent_count += 1
        self.name = 'BigBalls' + str(Bluffer.agent_count)
        evaluator = Evaluator()

    def bet(self, game_view):
        print('minimum_raise =', game_view.minimum_raise)
        return min(game_view.my_chips, game_view.minimum_bet + game_view.minimum_raise)

    def update(self, game_view):
    	return