from player import Player

class Simon(Player):
    agent_count = 0
    def __init__(self):
        Simon.agent_count += 1
        self.name = 'Simon' + str(Simon.agent_count)

    def bet(self, game_view, minimum):
        return minimum + 1