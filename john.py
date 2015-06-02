from player import Player
from evaluator import Evaluator
from card import Card
import random
import itertools

class John(Player):
    round_names = { 
        0: 'Preflop',
        3: 'Postflop',
        4: 'Turn',
        5: 'River'
    }
    # In order of 2 - A, s-c-h-d
    _FULL_DECK = []
    # In order of 2:deck, 3: deck-2, 4: deck-2,3
    # d-c-s-h
    _ALL_HOLE_CARDS = []
    # Tuples
    # key = pair rank eg 'A': {H|H is a tuple of 2 cards with rank = 'A'}
    _PAIRS = {}
    # Key = higherRank + lowerRank eg. 'AK'
    _SUITED = {}
    _UNSUITED = {}
    # Is this worth it at all?
    _SUITED_CONNECTORS = {}

    def __init__(self, name):
        self.name = name
        self.hand = set()
        self.betting_order = []
        self.round_number = 0
        self.current_round = ''
        self.my_raises_this_round = 0
        self.my_actions_this_tound = 0
        self.total_raises_this_round = 0
        self.total_actions_this_round = 0
        self.hands_seen = 0
        self.update_history = []
        self.eval = Evaluator()
        self.short_stack = False
        self.check_raise = False
        self.check_call = False
        self.three_bet = False

        # ========================================
        # Base Ranges
        # ========================================
        # Opening Ranges:
        self.early_open_range = set()
        self.mid_open_range = set()
        self.late_open_range = set()

        # Generate tables
        self._initiate_opening_hands()
        self._generate_initial_ranges()
    

    def bet(self, game_view):
        g = game_view
        self.hand = tuple(g.hole_cards)
        self.short_stack = g.my_chips < 25 * g.big_blind
        self.short_handed = len(g.players) <= 3
        self.total_actions_this_round += 1
        self.my_actions_this_tound += 1

        check_rating = 0
        call_rating = 0
        raise_rating = 0
        raise_total = 0
        for player in g.players_in_round:
            call_rating += self._call_rating(player, g)
            r1, r2 = self._raise_rating(player, g)
            raise_rating += r1
            raise_total += r2
        raise_amount = raise_total // len(g.players_in_round)

        if raise_rating == max(check_rating, call_rating, raise_rating) or self.check_raise:
            self.my_raises_this_round += 1
            return max(g.min_bet, raise_amount, g.min_raise)
        elif call_rating == max(check_rating, call_rating) or self.check_call:
            return g.min_bet
        else:
            return None if g.min_bet != 0 else 0

    def on_bet(self, player_name, action, amount, game_view):
        """
        Called when another player makes a bet.
        @param player_name - unique name of the player 
        @param action - One of the strings: "check" "call" "fold" "raise"
        @param amount - The amount put in to call or the amount raised by or None (fold).
        @param game_view - A game view with all the data.
        """
        self.total_actions_this_round += 1
        player = self.opponent[player_name]
        if self.current_round == 'Preflop':
            if action == 'fold':
                if self.total_raises_this_round == 1:
                    player.fv_steal_count += 1
                elif self.total_raises_this_round == 2:
                    player.fv_three_bet_count += 1
            elif action == 'raise':
                player.preflop_raise_count += 1
                if player_name in self.betting_order[-3:-2] and self.total_raises_this_round == 0:
                    player.ats_count += 1
                if self.total_raises_this_round == 0:
                    player.flop_cb_count += 1
                elif self.total_raises_this_round == 1:
                    player.three_bet_count += 1
            elif action == 'call':
                if self.total_raises_this_round == 2:
                    player.cv_three_bet_count += 1

        elif self.current_round == 'Postflop':
            if action == 'fold':
                player.fv_flop_cb_count += 1
            elif action == 'raise' and self.total_raises_this_round == 0:
                player.flop_cb_count += 1
            elif action == 'call':
                player.cv_flop_cb_count += 1

        elif self.current_round == 'Turn':
            if action == 'fold':
                player.fv_turn_cb_count += 1
            elif action == 'raise' and self.total_raises_this_round == 0:
                player.turn_cb_count += 1
            elif action == 'call':
                player.cv_turn_cb_count += 1

        elif self.current_round == 'River':
            if action == 'fold':
                player.fv_river_cb_count += 1
            elif action == 'raise' and self.total_raises_this_round == 0:
                player.river_cb_count += 1
            elif action == 'call':
                player.cv_river_cb_count += 1

        player.action_history[-1].append((action, amount))
        player.actions_this_round += 1
        if action == 'raise':
            self.total_raises_this_round += 1

    def on_new_round(self, game_view):
        """Called at the beginning of a new round of betting."""
        self.betting_order = game_view.players
        self.round_number += 1
        self.current_round = John.round_names[len(game_view.community_cards)]
        self.total_raises_this_round = 0
        self.total_actions_this_round = 0
        self.my_raises_this_round = 0
        self.my_actions_this_tound = 0
        for player in game_view.players_in_round:
            villain = self.opponent[player]
            villain.actions_this_round = 0
            if self.current_round == 'Postflop':
                villain.flops_seen += 1
            elif self.current_round == 'Turn':
                villain.turns_seen += 1
            elif self.current_round == 'River':
                villain.rivers_seen += 1
            villain.action_history.append([])

    def on_new_hand(self, game_view):
        """Called at the beginning of a new hand."""
        self.hands_seen += 1
        self.hand = tuple(game_view.hole_cards)
 
        for villain in self.opponent:
            self.opponent[villain].hands_seen += 1

    def on_new_game(self, players):
        """Called at the beginning of a new game."""
        self.opponent = {player: Villain(player) for player in players}

    def _position_advantage(self, villain_name):
        villain_position = self.betting_order.index(villain_name)
        my_position = self.betting_order.index(self.name)
        if self.current_round == 'Preflop':
            if self.name == self.betting_order[-1]:
                my_position = 0
            elif self.name == self.betting_order[-2]:
                my_position = 1

        return my_position > villain_position

    # return a tuple
    def _raise_rating(self, villain_name, g):
        villain = self.opponent[villain_name]
        # TODO: for possible_hand in John._ALL_HOLE_CARDS:

        if self.current_round == 'Preflop':

            if self.total_raises_this_round == 1:  # 3 bet?
                if self.hand in self.three_bet_range:
                    return (1, 6 * g.big_blind)
            elif self.total_raises_this_round == 2:  # 4 bet?
                pass # 4-bet?
            elif self.total_raises_this_round == 3:  # 5 bet?
                pass
            if self.hand in self.early_open_range:
                return (1, round(g.big_blind * 3.5))
        elif self.current_round == 'Postflop':
            pass
        elif self.current_round == 'Turn':
            pass
        elif self.current_round == 'River':
            pass

        return (-1, 2)

    def _call_rating(self, villain_name, game):
        call = game.amount_to_stay_in
        pot = game.pots[0]
        if self.hand in self.three_bet_calling_range:
            return 1
        return -1    

    def _fold_equity(self, villain_name, bet_size):
        return 2
   
    def _pot_odds(self, game):
        return 0.3

    def _implied_pot_odds(self, villain, game):
        aggression = villain.aggression()
        return 30

    def _generate_initial_ranges(self):
        self.early_open_range = John._PAIRS['A'].union( 
                John._PAIRS['K'],
                John._PAIRS['Q'],
                John._SUITED['AK'],
                John._SUITED['AQ'],
                John._SUITED['KQ'],
                John._UNSUITED['AK'])

        self.mid_open_range = self.early_open_range.union(
                John._PAIRS['J'], John._PAIRS['9'],
                John._PAIRS['T'], John._PAIRS['8'],
                John._SUITED['AJ'], John._SUITED['A2'],
                John._SUITED['AT'], John._SUITED['KJ'],
                John._SUITED['A5'], John._SUITED['KT'],
                John._SUITED['A4'], John._SUITED['QJ'],
                John._SUITED['A3'], John._SUITED['JT'],
                John._UNSUITED['AQ'],
                John._UNSUITED['AJ'],
                John._UNSUITED['AT'])
                
        self.late_open_range = self.mid_open_range.union(
                John._PAIRS['7'], John._PAIRS['6'],
                John._SUITED['A9'], John._SUITED['T9'],
                John._SUITED['A8'], John._SUITED['98'],
                John._SUITED['A7'], John._SUITED['87'],
                John._SUITED['A6'], John._SUITED['76'],
                John._SUITED['K9'], John._SUITED['65'],
                John._SUITED['QT'], John._SUITED['54'],
                John._SUITED['Q9'], John._SUITED['T8'],
                John._SUITED['J9'], John._SUITED['97'],
                John._SUITED['J8'], John._SUITED['86'],
                John._SUITED['75'],
                John._UNSUITED['KQ'], John._UNSUITED['KJ'],
                John._UNSUITED['KQ'], John._UNSUITED['KT'],
                John._UNSUITED['QJ'])

        self.three_bet_range = John._PAIRS['A'].union( 
                John._PAIRS['K'],
                John._PAIRS['Q'],
                John._SUITED['AK'],
                John._SUITED['AQ'])

        self.four_bet_range = John._PAIRS['A'].union( 
                John._PAIRS['K'],
                John._PAIRS['Q'])

        self.five_bet_range = John._PAIRS['A']

        self.three_bet_calling_range = self.three_bet_range - self.four_bet_range
        self.four_bet_calling_range = self.four_bet_range - self.five_bet_range


    def _initiate_opening_hands(self):
        for rank in Card.STR_RANKS:
            for suit,val in Card.CHAR_SUIT_TO_INT_SUIT.items():
                John._FULL_DECK.append(Card.new(rank + suit))
        for combo in itertools.combinations(John._FULL_DECK, 2):
            John._ALL_HOLE_CARDS.append(combo)
            cards = Card.int_to_str(combo[0]) + Card.int_to_str(combo[1])
            c1_rank, c1_suit, c2_rank, c2_suit = cards
            # Check for pairs
            if c1_rank == c2_rank:
                for rank in Card.STR_RANKS:
                    if c1_rank == rank:
                        if rank not in John._PAIRS:
                            John._PAIRS[rank] = set()
                        John._PAIRS[rank].add(combo)
            else:
                for rank_pair in itertools.combinations(Card.STR_RANKS[::-1], 2):
                    ranks = rank_pair[0] + rank_pair[1]
                    if rank_pair == (c2_rank, c1_rank) or rank_pair == (c1_rank, c2_rank):
                        if c1_suit == c2_suit:  # Suited!
                            if ranks not in John._SUITED:
                                John._SUITED[ranks] = set()
                            John._SUITED[ranks].add(combo)
                            if Card.STR_RANKS.index(rank_pair[0]) == 1 + Card.STR_RANKS.index(rank_pair[1]):
                                if ranks not in John._SUITED_CONNECTORS:
                                    John._SUITED_CONNECTORS[ranks] = set()
                                John._SUITED_CONNECTORS[ranks].add(combo)
                            # DEBUGGING
                            # print(ranks, Card.int_to_str(combo[0]), Card.int_to_str(combo[1]))
                        else:
                            if ranks not in John._UNSUITED:
                                John._UNSUITED[ranks] = set()
                            John._UNSUITED[ranks].add(combo)
                            # DEBUGGING
                            # print(ranks, Card.int_to_str(combo[0]), Card.int_to_str(combo[1]))

class Villain():
    '''Models an opponent'''
    count = 0



    def __init__(self, name):
        Villain.count += 1
        self.id = Villain.count
        self.name = name
        self.actions_this_round = 0
        self.action_history = []

        # Statistics
        self.hands_seen = 0

        self.vpip_count = 0
        self.preflop_raise_count = 0
        self.af_count = 0
        self.three_bet_count = 0
        self.three_bet_opp_count = 0
        self.fv_three_bet_count = 0
        self.cv_three_bet_count = 0
        self.ats_count = 0
        self.fv_steal_count = 0

        self.flops_seen = 0
        self.flop_cr_count = 0
        # % of times limp pre and fold flop to aggression
        self.limp_fold_count = 0
        self.flop_cb_count = 0
        self.fv_flop_cb_count = 0
        self.cv_flop_cb_count = 0

        self.turns_seen = 0
        self.turn_cb_count = 0
        self.fv_turn_cb_count = 0
        self.cv_turn_cb_count = 0

        self.rivers_seen = 0
        self.river_cb_count = 0
        self.fv_river_cb_count = 0
        self.cv_river_cb_count = 0

        # 'calling station', 'shark', 'average', 'LAG', 'TAG'
        self.label = 'average'
        
    def get_vpip(self):
        return self.vpip_count / self.hands_seen

    def get_label(self):
        if get_call_rate() > .8:
            return 'calling station'
        return self.label

    def get_call_rate(self):
        calls = self.vpip_count + self.cv_flop_cb_count + self.cv_turn_cb_count + self.cv_river_cb_count
        approx_opportunities = self.rivers_seen + self.turns_seen + self.flops_seen + self.hands_seen
        return calls / approx_opportunities

    def get_three_bet(self):
        return self.three_bet_count / self.three_bet_opp_count

    def get_flop_cb(self):
        return self.flop_cb_count / self.flops_seen

    def get_turn_cb(self):
        return self.turn_cb_count / self.turns_seen

    def aggression(self):
        return self.get_vpip() + self.get_3_bet() + self.get_flop_cb() + self.get_turn_cb()