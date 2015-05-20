from player import Player

class Human(Player):
    agent_count = 0
    def __init__(self):
        Human.agent_count += 1
        self.name = 'Human' + str(Human.agent_count)

    def bet(self, game_view, minimum):
        return minimum + 1