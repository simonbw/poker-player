from player import Player
from evaluator import Evaluator

class Folder(Player):
    agent_count = 0
    def __init__(self):
        Folder.agent_count += 1
        self.name = 'Weeny' + str(Folder.agent_count)
        evaluator = Evaluator()

    def bet(self, game_view):
        return None

    def update(self, game_view):
    	return