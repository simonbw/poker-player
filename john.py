from player import Player

class John(Player):
    agent_count = 0
    def __init__(self):
        John.agent_count += 1
        self.name = 'John' + str(John.agent_count)

    def bet(self, game_view, minimum):
        return game_view.chips[self] - game_view.money_for_pot[self]