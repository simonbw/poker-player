from player import Player
from evaluator import Evaluator
from util import Util
util = Util()

class Bluffer(Player):
    def __init__(self, name):
        self.name = name
        self.hand = ()
        self.bets_this_round = 0
        evaluator = Evaluator()
        self.early_open_range = set()
        self.mid_open_range = set()
        self._generate_initial_ranges()

    def bet(self, game_view):
        # print('minimum_raise =', game_view.minimum_raise)
        self.hand = tuple(game_view.hole_cards)
        if self.hand not in self.mid_open_range:
            return None
        if self.bets_this_round < 3:
            self.bets_this_round += 1
            return max(game_view.pot_size, game_view.min_raise + game_view.min_bet)
        return game_view.min_bet

    def on_new_round(self, game_view):
        self.bets_this_round = 0

    def _generate_initial_ranges(self):
        self.early_open_range = Util.PAIRS['A'].union( 
                Util.PAIRS['K'],
                Util.PAIRS['Q'],
                Util.SUITED['AK'],
                Util.SUITED['AQ'],
                Util.SUITED['KQ'],
                Util.UNSUITED['AK'])

        self.mid_open_range = self.early_open_range.union(
                Util.PAIRS['J'], Util.PAIRS['9'],
                Util.PAIRS['T'], Util.PAIRS['8'],
                Util.SUITED['AJ'], Util.SUITED['A2'],
                Util.SUITED['AT'], Util.SUITED['KJ'],
                Util.SUITED['A5'], Util.SUITED['KT'],
                Util.SUITED['A4'], Util.SUITED['QJ'],
                Util.SUITED['A3'], Util.SUITED['JT'],
                Util.UNSUITED['AQ'],
                Util.UNSUITED['AJ'],
                Util.UNSUITED['AT'])