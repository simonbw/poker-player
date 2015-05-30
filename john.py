from player import Player
from evaluator import Evaluator

class John(Player):
    agent_count = 0

    def __init__(self):
        John.agent_count += 1
        self.name = 'John' + str(John.agent_count)
        evaluator = Evaluator()

    def bet(self, game_view, minimum_bet, minimum_raise):
        return game_view.my_chips

    def update(self, game_view, event):

    	return

class Villain():
	'''Models an opponent'''
	count = 0
	def __init__(self):
		Villain.count += 1
		self.id = Villain.count
		self.vpip = 0