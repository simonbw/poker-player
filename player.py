class Player:
    agent_count = 0
    def __init__(self):
        Player.agent_count += 1
        self.name = 'Player' + str(Player.agent_count)

    def bet(self, game_view, minimum):
        return minimum + 1