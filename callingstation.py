from player import Player
from evaluator import Evaluator

class CallingStation(Player):
    agent_count = 0
    def __init__(self):
        CallingStation.agent_count += 1
        self.name = 'Fish' + str(CallingStation.agent_count)
        evaluator = Evaluator()

    def bet(self, game_view):
        return min(game_view.amount_to_stay_in, game_view.chips[self])

    def update(self, game_view):
    	return