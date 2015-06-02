from player import Player
from evaluator import Evaluator
from card import Card
import random
import itertools

class John(Player):
    agent_count = 0
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

    # Tuples
    # key = pair rank eg 'A': {H|H is a tuple of 2 cards with rank = 'A'}
    _PAIRS = {}
    # Key = higherRank + lowerRank eg. 'AK'
    _SUITED = {}
    _UNSUITED = {}
    # Is this worth it at all?
    _SUITED_CONNECTORS = {}

    def __init__(self):
        John.agent_count += 1
        self.name = 'John' + str(John.agent_count)
        self.hand = set()
        self.betting_order = []
        self.round_number = 0
        self.current_round = ''
        self.raises_this_round = 0
        self.hands_seen = 0
        self.update_history = []
        self.eval = Evaluator()
        self.short_stack = False
        self.slow_play = False
        self.check_raise = False
        self.three_bet = False

        # ========================================
        # Base Ranges
        # ========================================
        # Open Ranges:
        self.UTG_open_range = set()
        self.mid_open_range = set()
        self.late_open_range = set()
        self.BB_open_range = set()
        self.LB_open_range = set()
        # Generate tables
        self._initiate_opening_hands()
        self._generate_ranges()
    

    def bet(self, game_view):
        g = game_view
        self.hand = {tuple(g.hole_cards)}
        cards = g.hole_cards
        print(tuple(cards) in self.value_hands)

        if self.hand <= self.value_hands:
            print('Trying to raise with', Card.int_to_str(cards[0]), Card.int_to_str(cards[1]))
            return min(g.my_chips, max(g.amount_to_stay_in, g.big_blind * 3, g.amount_to_stay_in + g.minimum_raise))
        else:
            print('Trying to fold')
            return None

        if g.my_chips < 25 * g.big_blind:
            self.short_stack = True

        if self.check_raise:
            return min(g.my_chips, g.pots[0] * 2 // 3)

        check_ev = 0
        call_ev = 0
        raise_ev = 0
        for player in g.players_in_hand:
            call_ev += self._call_ev(player, g)
            raise_ev += self._raise_ev(player, g)

        if self.slow_play:
            check_ev

        if random.random() < 0.03:
            call_ev += 500
        
        elif raise_ev == max(check_ev, call_ev, raise_ev):
            return min(g.my_chips, self._raise_amount(g))
        elif call_ev == max(check_ev, call_ev):
            return min(g.my_chips, g.amount_to_stay_in)
        else:
            return None if g.amount_to_stay_in > 0 else 0

        return game_view.chips[self.name]

    def on_bet(self, player_name, action, amount, game_view):
        """
        Called when another player makes a bet.
        @param player_name - unique name of the player 
        @param action - One of the strings: "check" "call" "fold" "raise"
        @param amount - The amount put in to call or the amount raised by or None (fold).
        @param game_view - A game view with all the data.
        """
        player = self.opponent[player_name]
        # Note, no previous action in round. Should be bot's strongest play area
        if self.current_round == 'Preflop':
            if action == 'check':
                pass  # not even remotely possible
            elif action == 'fold':
                if self.raises_this_round == 1:
                    player.fv_steal_count += 1
                elif self.raises_this_round == 2:
                    player.fv_three_bet_count += 1
            elif action == 'raise':
                player.preflop_raise_count += 1
                if player_name in self.betting_order[-3:-2] and self.raises_this_round == 0:
                    player.ats_count += 1
                if self.raises_this_round == 0:
                    player.flop_cb_count += 1
                elif self.raises_this_round == 1:
                    player.three_bet_count += 1
            elif action == 'call':
                pass

        elif self.current_round == 'Postflop':
            if action == 'check':
                pass
            elif action == 'fold':
                player.fv_flop_cb_count += 1
            elif action == 'raise' and self.raises_this_round == 0:
                player.flop_cb_count += 1
            elif action == 'call':
                pass

        elif self.current_round == 'Turn':
            if action == 'check':
                pass
            elif action == 'fold':
                player.fv_flop_cb_count += 1
            elif action == 'raise' and self.raises_this_round == 0:
                player.flop_cb_count += 1
            elif action == 'call':
                pass

        elif self.current_round == 'River':
            if action == 'check':
                pass
            elif action == 'fold':
                player.fv_flop_cb_count += 1
            elif action == 'raise' and self.raises_this_round == 0:
                player.flop_cb_count += 1
            elif action == 'call':
                pass

        player.action_history[-1].append((action, amount))
        player.actions_this_round += 1
        if action == 'raise':
            self.raises_this_round += 1

    def on_new_round(self, game_view):
        """Called at the beginning of a new round of betting."""
        self.betting_order = game_view.players
        self.round_number += 1
        self.current_round = John.round_names[len(game_view.community_cards)]
        self.raises_this_round = 0
        for player in game_view.players_in_hand:
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
        self.hand = game_view.hole_cards
 
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

    def _raise_ev(self, villain_name, game):
        ev = 0
        if self.hand <= self.value_hands:
            return 1000

        return 1

    def _call_ev(self, villain_name, game):
        call = game.amount_to_stay_in
        pot = game.pots[0]
        return 10    

    def _fold_equity(self, villain_name, bet_size):
        return 10
   
    def _pot_odds(self, game):
        return 0.3

    def _implied_pot_odds(self, villain, game):
        aggression = villain.aggression()
        return 30

    def _raise_amount(self, game):
        pot_size = game.pots[0]
        base = game.amount_to_stay_in

        if self.current_round == 'Preflop':
            if self.three_bet:
                return pot_size + pot_size // 2
            if self.hand <= self.value_hands:
                return pot_size + pot_size // 2
            #TODO
            #if set(game.hole_cards)
            return base + game.big_blind * 3 + game.big_blind // 2
        elif current_round == 'Postflop':
            return pot_size
        elif current_round == 'Turn':
            return pot_size * 2 + pot_size // 2
        elif current_round == 'River':
            hand = self.eval.evaluate()
            return 10

        return 0

    def _generate_ranges(self):
        self.value_hands = John._PAIRS['A'].union( 
                John._PAIRS['K'],
                John._PAIRS['Q'], 
                John._PAIRS['J'],
                John._SUITED['AK'],
                John._UNSUITED['AK'])
                #John._SUITED['AQ'],
                #John._SUITED['AJ'])

        print((Card.new('Qc'), Card.new('As')) in self.value_hands)

    def _initiate_opening_hands(self):
        for rank in Card.STR_RANKS:
            for suit,val in Card.CHAR_SUIT_TO_INT_SUIT.items():
                John._FULL_DECK.append(Card.new(rank + suit))
        for combo in itertools.combinations(John._FULL_DECK, 2):
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
        self.ats_count = 0
        self.fv_steal_count = 0

        self.flops_seen = 0
        self.flop_cr_count = 0
        # % of times limp pre and fold flop to aggression
        self.limp_fold_count = 0
        self.flop_cb_count = 0
        self.fv_flop_cb_count = 0

        self.turns_seen = 0
        self.turn_cb_count = 0
        self.fv_turn_cb_count = 0
        self.rivers_seen = 0

        self.label = (5, 5, 2)
        # loose, aggressive, pro
        
    def get_vpip(self):
        """ """
        pass 

    def get_label(self):
        return self.label

    def get_3_bet(self):
        return self.three_bet_count / self.three_bet_opp_count

    def get_flop_cb(self):
        return self.flop_cb_count / self.flops_seen

    def get_turn_cb(self):
        return self.turn_cb_count / self.turns_seen

    def aggression(self):
        return self.get_vpip() + self.get_3_bet() + self.get_flop_cb() + self.get_turn_cb()