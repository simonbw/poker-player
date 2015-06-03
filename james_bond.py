from player import Player
from card import Card
from util import Util
util = Util()

class JamesBond(Player):
    def __init__(self):
        # Constants
        self.c = {}
        self._generate_constants()

        # Game data
        self.name = 'James Bond'
        self.opponents = {}
        self.pot_evs = {}

        # Hand data
        self.hand = ()
        self.betting_order = []

        # Round data
        self.round_number = 0
        self.current_round = ''
        self.my_raises_this_round = 0
        self.my_actions_this_tound = 0
        self.total_raises_this_round = 0
        self.total_actions_this_round = 0
        self.hands_seen = 0

        # Toggles
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

        # Generate ranges
        self._generate_initial_ranges()

    def bet(self, g):
        self.hand = tuple(g.hole_cards)
        self.short_stack = g.my_chips < 25 * g.big_blind
        self.short_handed = len(g.players) <= 3
        self.total_actions_this_round += 1
        self.my_actions_this_tound += 1

        raise_ev, raise_amount = self._raise_ev(g)
        call_ev = self._call_ev(g)

        if self.current_round == 'Preflop' and self.hand not in self.mid_open_range:
            return None if g.min_bet != 0 else 0

        if raise_ev == max(0, call_ev, raise_ev) or self.check_raise:
            self.my_raises_this_round += 1
            return max(g.min_bet, raise_amount, g.min_raise + g.min_bet)
        elif call_ev == max(0, call_ev) or self.check_call:
            return g.min_bet
        else:
            return None if g.min_bet != 0 else 0

    def on_bet(self, player_name, action, amount, g):
        """
        Called when another player makes a bet.
        @param player_name - unique name of the player 
        @param action - One of the strings: "check" "call" "fold" "raise"
        @param amount - The amount put in to call or the amount raised by or None (fold).
        @param g - A game view with all the data.
        """
        self.total_actions_this_round += 1
        player = self.opponents[player_name]

        if self.current_round == 'Preflop':
            if action == 'fold':
                if self.total_raises_this_round == 1:
                    # Not quite fv steal, but close enough.
                    player.three_bet_opp_count += 1
                    player.fv_steal_count += 1
                elif self.total_raises_this_round == 2:
                    player.fv_three_bet_count += 1
            elif action == 'raise':
                player.preflop_raise_count += 1
                if (player_name in self.betting_order[-3:-2] 
                        and self.total_raises_this_round == 0):
                    player.ats_count += 1
                if self.total_raises_this_round == 0:
                    player.open_count += 1
                elif self.total_raises_this_round == 1:
                    player.three_bet_count += 1
            elif action == 'call':
                if self.total_raises_this_round == 1:
                    player.three_bet_opp_count += 1
                if self.total_raises_this_round == 2:
                    player.cv_three_bet_count += 1

        elif self.current_round == 'Postflop':
            if action == 'fold':
                if (player.actions_this_round == 0 and 
                        player.action_history[-2][-1][0] == 'call'):
                    player.limp_fold_count += 1
                if total_actions_this_round == 1:
                    player.fv_flop_cb_count += 1
            elif action == 'raise':           
                if (player.actions_this_round > 1 and 
                        player.last_action()[0] == 'check'):
                    player.flop_cr_count += 1
                if self.total_raises_this_round == 0:
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

        if player.actions_this_round == 0 and action in ('raise', 'call'):
            player.vpip_count += 1
        if action == 'raise':
            if player.actions_this_round > 0:
                if player.last_action()[0] == 'check':
                    player.cr_count += 1
        if action == 'call':
            self.total_raises_this_round += 1
            if player.actions_this_round == 0:
                player.vpip_count += 1

        player.action_history[-1].append((action, amount))
        player.actions_this_round += 1

        # Updating P(hand|action taken)
        player.update_range()

    def on_new_round(self, g):
        """Called at the beginning of a new round of betting."""
        self.betting_order = g.players
        self.round_number += 1
        self.current_round = util.ROUND_NAMES[len(g.community_cards)]
        self.total_raises_this_round = 0
        self.total_actions_this_round = 0
        self.my_raises_this_round = 0
        self.my_actions_this_tound = 0

        for player in g.players_in_round:
            opponent = self.opponents[player]
            opponent.actions_this_round = 0
            if self.current_round == 'Postflop':
                opponent.flops_seen += 1
            elif self.current_round == 'Turn':
                opponent.turns_seen += 1
            elif self.current_round == 'River':
                opponent.rivers_seen += 1
            opponent.action_history.append([])

    def on_new_hand(self, g):
        """Called at the beginning of a new hand."""
        self.hands_seen += 1
        self.hand = tuple(g.hole_cards)
 
        for opponent in self.opponents:
            self.opponents[opponent].hands_seen += 1

    def on_new_game(self, players):
        """Called at the beginning of a new game."""
        self.opponents = {player: opponent(player) for player in players}

    def _pa(self, opponent_name):
        """Returns true if self has positional advantage on opponent_name"""
        opponent_position = self.betting_order.index(opponent_name)
        my_position = self.betting_order.index(self.name)
        if self.current_round == 'Preflop':
            if self.name == self.betting_order[-1]:
                my_position = 0
            elif self.name == self.betting_order[-2]:
                my_position = 1

        return my_position > opponent_position

    def _raise_ev(self, g):
        """Returns an ev and value for raising"""
        final_rating = 0
        final_amount = 0
        total_amount_ratings = 0

        for opponent_name in g.players_in_round:
            if opponent_name != self.name and self._pa(opponent_name):
                rating, amount, amount_rating = self._raise_vs(self.opponents[opponent_name], g)
                final_rating += rating
                final_amount += round(amount * amount_rating)
                total_amount_ratings += amount_rating
        final_amount = final_amount / max(1, abs(total_amount_ratings))

        return (final_rating, final_amount)

    def _raise_vs(self, opponent, g):
        """Returns a tuple (rating, raise_amount, amount_rating)

        rating := how good is raising against opponent?
        raise_amount := if raise, how much?
        amount_rating := if raise, how good is raise_amount?
                         ie."number of votes"
        """
        rating = 1
        raise_amount = g.min_raise
        amount_rating = 1
        num_players = len(g.players_in_round) - 1
        BB = g.big_blind

        if self.current_round == 'Preflop':
            if self.total_raises_this_round == 1:  # 3 bet?
                if self.hand in self.three_bet_range:
                    rating *= self.c['3betEv'+str(num_players)]
                    raise_amount = c['3betValue'+str(num_players)] * BB
                    amount_rating = 3
            elif self.total_raises_this_round == 2:  # 4 bet?
                if self.hand in self.four_bet_range:
                    # TODO better constants
                    rating *= 3
                    raise_amount = 9 * BB
                    amount_rating = 5
            elif self.total_raises_this_round == 3:  # 5 bet?
                if self.hand in self.five_bet_range:
                    rating *= 4
                    raise_amount = 20 * BB
                    amount_rating = 4
            if self.hand in self.early_open_range:
                return (10, round(g.big_blind * 4), 5)
        else:
            raise_amount = g.pot_size // 2
            if (raise_amount, opponent.label) not in self.pot_evs:
                self.pot_evs[(raise_amount, opponent.label)] = self._pot_ev(raise_amount, opponent, g)
            rating = self.pot_evs[(raise_amount, opponent.label)]

            rating += self._fold_equity(opponent, g.pot_size)
            amount_rating = rating
        return (rating, raise_amount, amount_rating)

    def _call_ev(self, g):
        """Returns an ev and value for raising"""
        final_rating = 0

        for opponent_name in g.players_in_round:
            if opponent_name != self.name and self._pa(opponent_name):
                final_rating += self._call_vs(self.opponents[opponent_name], g)
        final_rating = final_rating / (len(g.players_in_round) - 1)

        return final_rating

    def _call_vs(self, opponent, g):
        rating = 1
        num_players = len(g.players_in_round) - 1
        if self.current_round == 'Preflop':
            rating *= self.c['flattingValue'+str(num_players)]
        else:
            if (g.min_bet, opponent.label) not in self.pot_evs:
                self.pot_evs[(g.min_bet, opponent.label)] = self._pot_ev(g.min_bet, opponent, g)
            rating = self.pot_evs[(g.min_bet, opponent.label)]

        return rating

    def _fold_equity(self, opponent, pot_size):
        if self.current_round == 'Preflop':
            return pot_size * opponent.fv_three_bet()
        elif self.current_round == 'Postflop':
            return pot_size * opponent.fv_flop_cb()
        elif self.current_round == 'Turn':
            return pot_size * opponent.fv_turn_cb()
        elif self.current_round == 'River':
            return pot_size * opponent.fv_river_cb()
        else:
            return 0
    
    def _pot_ev(self, into_pot, opponent, g):
        own = into_pot / (into_pot + g.pot_size)
        range_ = opponent.get_probable_hands()
        equity = util.my_equity(self.hand, g.community_cards, range_)
        return (equity - own) * g.pot_size

    # def _implied_pot_odds(self, opponent, g):
    #     aggression = opponent.aggression()
    #     return 30

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
                
        self.late_open_range = self.mid_open_range.union(
                Util.PAIRS['7'], Util.PAIRS['6'],
                Util.SUITED['A9'], Util.SUITED['T9'],
                Util.SUITED['A8'], Util.SUITED['98'],
                Util.SUITED['A7'], Util.SUITED['87'],
                Util.SUITED['A6'], Util.SUITED['76'],
                Util.SUITED['K9'], Util.SUITED['65'],
                Util.SUITED['QT'], Util.SUITED['54'],
                Util.SUITED['Q9'], Util.SUITED['T8'],
                Util.SUITED['J9'], Util.SUITED['97'],
                Util.SUITED['J8'], Util.SUITED['86'],
                Util.SUITED['75'],
                Util.UNSUITED['KQ'], Util.UNSUITED['KJ'],
                Util.UNSUITED['KQ'], Util.UNSUITED['KT'],
                Util.UNSUITED['QJ'])

        self.three_bet_range = Util.PAIRS['A'].union( 
                Util.PAIRS['K'],
                Util.PAIRS['Q'],
                Util.SUITED['AK'],
                Util.SUITED['AQ'])

        self.four_bet_range = Util.PAIRS['A'].union( 
                Util.PAIRS['K'],
                Util.PAIRS['Q'])

        self.five_bet_range = Util.PAIRS['A']

        self.three_bet_calling_range = self.three_bet_range - self.four_bet_range
        self.four_bet_calling_range = self.four_bet_range - self.five_bet_range

    def _generate_constants(self):
        
        for x in range(1, 24):
            self.c['3betEv' + str(x)] = 0.6 * abs(x - x / 2)
            self.c['flattingValue' + str(x)] = 1 / x
            self.c['3betValue' + str(x)] = 3.5

class opponent():
    '''Models an opponent'''
    count = 0

    def __init__(self, name):
        opponent.count += 1
        self.id = opponent.count
        self.name = name
        self.actions_this_round = 0
        self.action_history = []

        # Betting Statistics
        self.hands_seen = 0
        self.cr_count = 0

        self.vpip_count = 0
        self.preflop_raise_count = 0
        self.three_bet_count = 0
        self.three_bet_opp_count = 0
        self.fv_three_bet_count = 0
        self.cv_three_bet_count = 0
        self.ats_count = 0
        self.fv_steal_count = 0
        self.open_count = 0

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
        self.probable_hands = {}
        self._generate_label_hands()
    
    def last_action(self):
        return self.action_history[-1][-1]
        
    def get_vpip(self):
        return self.vpip_count / max(self.hands_seen, 1)

    def get_call_rate(self):
        calls = self.vpip_count + self.cv_flop_cb_count + self.cv_turn_cb_count + self.cv_river_cb_count
        approx_opportunities = self.rivers_seen + self.turns_seen + self.flops_seen + self.hands_seen
        return calls / max(approx_opportunities, 1)

    def get_three_bet(self):
        return self.three_bet_count / max(1, self.three_bet_opp_count)

    def get_flop_cb(self):
        return self.flop_cb_count / max(1, self.flops_seen)

    def get_turn_cb(self):
        return self.turn_cb_count / max(1, self.turns_seen)

    def get_probable_hands(self):
        return self.probable_hands[self.label]

    def fv_three_bet(self):
        return self.fv_three_bet_count / max(1, self.three_bet_opp_count)

    def fv_flop_cb(self):
        return self.fv_flop_cb_count / max(1, self.flops_seen)

    def fv_turn_cb(self):
        return self.fv_turn_cb_count / max(1, self.turns_seen)

    def fv_river_cb(self):
        return self.fv_river_cb_count / max(1, self.rivers_seen)

    def aggression(self):
        return self.get_vpip() + self.get_3_bet() + self.get_flop_cb() + self.get_turn_cb()

    def update_label(self):
        pass

    def update_range(self):
        self.update_label()
        pass

    def _generate_label_hands(self):
        #'calling station', 'average', 'shark', 'LAG', 'TAG'
        average_range= set()
        for set_ in Util.PAIRS.values():
            average_range |= set_
        for set_ in Util.SUITED.values():
            average_range |= set_
        average_range |= (Util.UNSUITED['AK'] | Util.UNSUITED['K8'] | 
                         Util.UNSUITED['AQ'] | Util.UNSUITED['QJ'] | 
                         Util.UNSUITED['AJ'] | Util.UNSUITED['QT'] | 
                         Util.UNSUITED['AT'] | 
                         Util.UNSUITED['A9'] | 
                         Util.UNSUITED['A8'] | 
                         Util.UNSUITED['KQ'] | 
                         Util.UNSUITED['KJ'] | 
                         Util.UNSUITED['T9'])
        self.probable_hands['average'] = average_range

