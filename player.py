class Player:
	#
    player_count = 0


    def __init__(self):
        Player.player_count += 1
        self.name = self.__class__.__name__ + str(Player.player_count)

    def bet(self, game_view, minimum_bet, minimum_raise):
    	"""
        Called when asking how much a player would like to bet.
        Returning None folds.
        """
        return None

    def on_bet(self, player_name, action, amount, game_view):
    	"""
        Called when another player makes a bet.
        @param player_name - unique name of the player 
        @param action - One of the strings: "check" "call" "fold" "raise"
        @param amount - The amount put in to call or the amount raised by or None (fold).
        @param game_view - A game view with all the data.
        """
    	pass

    def on_new_round(self, game_view):
    	"""Called at the beginning of a new round of betting."""
    	pass

    def on_new_hand(self, game_view):
    	"""Called at the beginning of a new hand."""
    	pass

    def on_new_game(self, players):
    	"""Called at the beginning of a new game."""
    	pass