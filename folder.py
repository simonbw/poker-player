from player import Player
from evaluator import Evaluator

class Folder(Player):
    def __init__(self, name):
        self.name = name
        evaluator = Evaluator()

    def bet(self, game_view):
        return None

    def update(self, game_view):
    	return