from player import Player

class Simon(Player):
    agent_count = 0
    def __init__(self):
        Simon.agent_count += 1
        self.name = 'Simon' + str(Simon.agent_count)

    def bet(self, game_view, minimum_bet, minimum_raise):
        return min(minimum_bet, game_view.chips[self])