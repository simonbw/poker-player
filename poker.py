from card import Card
from deck import Deck
from evaluator import Evaluator
from itertools import cycle

evaluator = Evaluator()


class Game:

    """Describes one game of No-Limit Texas Hold'em as a single table tournament"""

    def __init__(self, players):
        """"""

        # Set up the table
        self.players = players
        self.busted_players = []
        self.folded_players = set()
        self.big_blind = 2
        self.little_blind = 1
        self.pots = [0]
        self.odd_chips = 0
        self.hole_cards = {}
        self.deck = Deck()

        # Starting chips for each player
        self.chips = {}
        for player in players:
            self.chips[player] = 300

        for player in self.players:
            player.on_new_game([p.name for p in self.players])

        print("New game created with the following players:\n ",
              ', '.join([player.name for player in players]), "\n")

    def play(self):
        """Simulate an entire game of poker, playing hands until only one player has any chips left."""

        print("Game start:")
        while len(self.players) != 1:
            self.reset_table()
            self.play_hand()
            self.remove_busted_players()
        self.report_end_standings()

    def reset_table(self):
        """Resets the table for a new hand"""

        self.pots[0] = 0
        self.pots[0] += self.odd_chips
        self.folded_players = set()
        self.money_for_pot = {player: 0 for player in self.players}
        self.community_cards = []
        self.deck = Deck()

    def play_hand(self):
        """Plays one hand of the game."""

        print("New Hand")
        self.deal()
        for player in self.players:
            player.on_new_hand(GameView(self, player))
        for i in (3, 1, 1, 0):  # flop, turn, river reveal number
            if self.enough_players_have_chips():
                self.round_of_betting(i == 3)
            self.reveal(i)

            if len(self.players) == len(self.folded_players) + 1:
                break  # go to payout
        remaining_players = set(self.players) - self.folded_players
        self.payout(remaining_players, self.pots[0])
        self.rotate_players()
        print()

    def remove_busted_players(self):
        """Reports and removes busted players from the players list"""

        for player in self.players:
            if self.chips[player] == 0:
                print(player.name, 'is out!')
                if player not in self.busted_players:
                    self.busted_players.append(player)
            else:
                print(player.name, 'has', self.chips[player], 'chips')

        for player in self.busted_players:
            if player in self.players:
                self.players.remove(player)
            print(player.name, 'is currently busted')

    def report_end_standings(self):
        """Reports the results of the tournament"""

        print('The game has concluded.')
        print(self.players[0].name, 'is the victor!')

        print('These players are ranked from 2nd to last:\n')
        for player in reversed(self.busted_players):
            print(player.name)

    def enough_players_have_chips(self):
        players_with_chips = 0
        for player in self.players:
            if player not in self.folded_players and self.chips[player] != 0:
                players_with_chips += 1
        return players_with_chips >= 2

    def round_of_betting(self, first_round=False):
        """Ask for bets from each player."""
        print("New Round Of Betting")

        for player in self.players:
            player.on_new_round(GameView(self, player))

        if first_round:
            self.antes()
            largest_bet = self.big_blind
            last_aggressor = self.players[1 if len(self.players) > 2 else 0]
            if len(self.players) > 2:
                self.players.append(self.players.pop(0))
            self.players.append(self.players.pop(0))
        else:
            largest_bet = 0
            last_aggressor = None
        print("Betting Order:", ", ".join(
                    [player.name for player in self.players]))
        minimum_raise = self.big_blind

        for player in cycle(self.players):
            if first_round and largest_bet == self.big_blind and player is self.players[-1]:
                last_aggressor = self.players[2 % len(self.players)]
            if len(self.folded_players) + 1 == len(self.players) or player is last_aggressor:
                break
            if player in self.folded_players:
                continue
            if not first_round and last_aggressor is None:
                last_aggressor = player

            print('Action to', player.name)
            amount_to_stay_in = largest_bet - self.money_for_pot[player]

            if amount_to_stay_in == 0:
                print('0 to stay in. Check or bet?')
            else:
                print(amount_to_stay_in, 'to stay in.\nCall, raise, or fold.')
            bet = player.bet(GameView(self, player, amount_to_stay_in, minimum_raise))

            # Detect folding
            if bet is None:
                # notify other players
                for p in self.players:
                    if p is not player:
                        p.on_bet(player.name, "fold", None, GameView(self, player))
                self.folded_players.add(player)
                print(player.name, 'has folded with', self.chips[player], 'chips left.')
                continue  # go to next player

            self.validate_bet_amount(player, bet, amount_to_stay_in, minimum_raise)

            # Adjust chip totals
            self.money_for_pot[player] += bet
            self.chips[player] -= bet
            print(player.name, 'has', self.chips[player], 'chips left.')

            if bet == 0:    
                for p in self.players:
                    if p is not player:
                        p.on_bet(player.name, "check", 0, GameView(self, player))                                    # Check
                print(player.name, 'checks')
            elif bet > amount_to_stay_in:                       # Raise
                raise_amount = bet - amount_to_stay_in
                # Only reopen betting if the raise is sufficiently large
                #   (matters when someone raises less than min_raise by going all-in)
                if bet >= minimum_raise / 2:
                    last_aggressor = player
                largest_bet = self.money_for_pot[player] + bet
                for p in self.players:
                    if p is not player:
                        p.on_bet(player.name, "raise", raise_amount, GameView(self, player))
                print(player.name, 'has raised', raise_amount)
            elif bet == amount_to_stay_in:                      # Call
                for p in self.players:
                    if p is not player:
                        p.on_bet(player.name, "call", bet, GameView(self, player))
                print(player.name, 'has called for', bet)

            print('The largest bet is currently', largest_bet)

        # put all bets in pot
        for player in self.players:
            self.pots[0] += self.money_for_pot[player]
            self.money_for_pot[player] = 0

        if first_round:
            if len(self.players) > 2:
                self.players.insert(0, self.players.pop())
            self.players.insert(0, self.players.pop())

    def antes(self):
        """Apply the big and little blinds."""

        if len(self.players) > 2:
            LB = self.players[0]
            BB = self.players[1]
        else:
            LB = self.players[1]
            BB = self.players[0]
        if self.chips[LB] < self.little_blind:
            self.money_for_pot[LB] = self.chips[LB]
            self.chips[LB] = 0
        else:
            self.money_for_pot[LB] += self.little_blind
            self.chips[LB] -= self.little_blind

        if self.chips[BB] < self.big_blind:
            self.money_for_pot[BB] = self.chips[BB]
            self.chips[BB] = 0
        else:
            self.money_for_pot[BB] += self.big_blind
            self.chips[BB] -= self.big_blind

    def deal(self):
        """Deals 2 random cards to each player"""
        # Does not need to be dealt in "correct order" since random is random
        print("Dealing")
        self.hole_cards = {}
        for player in self.players:
            self.hole_cards[player] = self.deck.draw(2)
            print("  ", player.name, [Card.int_to_str(card) for card in self.hole_cards[player]])
        print()

    def validate_bet_amount(self, player, bet, amount_to_stay_in, minimum_raise):
        
        if bet != self.chips[player]:
            if bet < amount_to_stay_in:
                raise Exception("Bad Bet: Too small")
            # More chips than possible
            if bet > self.chips[player]:
                raise Exception("Bad Bet: That's more than you have!\nYou tried to bet:", bet)
            # Didn't raise enough
            if amount_to_stay_in < bet < amount_to_stay_in + minimum_raise:
                raise Exception("Bad Bet: Minimum raise is", minimum_raise, "Tried to bet", bet)

    def reveal(self, n_cards):
        """Reveals a n_cards from the deck and place them in the common cards."""

        if n_cards == 0:
            return
        for i in range(n_cards):
            self.community_cards.append(self.deck.draw())
        print('community_cards:', [Card.int_to_str(card) for card in self.community_cards], "\n")

    def payout(self, players_in_pot, pot, pot_name='main pot'):
        """Find winner and give out pot."""
        print("Resulting Hands:")
        best_players = []
        best_score = 999999999
        for player in players_in_pot:

            score = evaluator.evaluate(self.community_cards, self.hole_cards[player])
            if score < best_score:
                best_players = [player]
                best_score = score
            elif score == best_score:
                best_players.append(player)

            print(player.name, 'has a', evaluator.class_to_string(evaluator.get_rank_class(score)))

        reward = pot // len(best_players)
        self.odd_chips = pot % len(best_players)
        for player in best_players:
            self.chips[player] += reward

        print([player.name for player in best_players], 'won', pot_name, 'of', pot, 'chips.')

    def rotate_players(self):
        """Change the list of players so the """
        self.players.append(self.players.pop(0))


# What is passed to a player on their turn
class GameView:
    """The data that is passed to an agent."""
    def __init__(self, game_state, player, amount_to_stay_in=None, minimum_raise=None):
        self.hole_cards = game_state.hole_cards[player][:]

        self.community_cards = game_state.community_cards[:]
        self.pots = game_state.pots
        self.my_chips = game_state.chips[player]
        self.amount_to_stay_in = amount_to_stay_in
        self.minimum_bet = amount_to_stay_in
        self.chips = {player.name: game_state.chips[player] for player in list(game_state.chips)}
        self.players = [player.name for player in game_state.players]
        players_in_hand = list(set(game_state.players) - game_state.folded_players)
        self.players_in_hand = [player.name for player in players_in_hand]
        self.folded_players = [player.name for player in game_state.folded_players]
        self.money_for_pot = {player.name: game_state.money_for_pot[player] for player in list(game_state.money_for_pot.keys())}
        self.minimum_raise = minimum_raise
        self.big_blind = game_state.big_blind


if __name__ == '__main__':
    from simon import Simon
    from john import John
    from callingstation import CallingStation
    from folder import Folder
    from bluffer import Bluffer
    players = [John(), CallingStation(), CallingStation(), CallingStation(), CallingStation(), Bluffer(), Folder()]
    game = Game(players)

    game.play()
