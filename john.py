from player import Player
from evaluator import Evaluator

class John(Player):
    agent_count = 0
    def __init__(self):
        John.agent_count += 1
        self.name = 'John' + str(John.agent_count)
        evaluator = Evaluator()

    def bet(self, game_view, minimum_bet, minimum_raise):
        return game_view.chips[self]