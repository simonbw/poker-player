import random
from copy import copy
from card import Card
from deck import Deck
from evaluator import Evaluator

evaluator = Evaluator()

class Game:
    """Describes one game of No-Limit Texas Hold'em as a single table tournament"""

    def __init__(self, players):
        """"""
        
        self.players = players
        self.busted_players = []
        print("New Game:", ', '.join([player.name for player in players]), "\n\n")

        self.big_blind = 2
        self.little_blind = 1

        self.chips = {}
        for player in players:
            self.chips[player] = 100

    def play(self):
        """Simulate an entire game of poker, playing hands until only one player has any chips left."""

        while len(self.players) > 1: # game not over
            self.reset_table()
            self.play_hand()
            for player in self.players:
                if self.chips[player] == 0:
                    print(player.name, 'has gone bust!')
                    self.busted_players.append(player)
                    self.players.remove(player)
                else:
                    print(player.name, 'has', self.chips[player], 'chips')


        print('The game has concluded.')
        for player in self.players:
            print(player.name, 'is the victor!')

        print('These players are ranked from 2nd to last:\n')
        for player in reversed(self.busted_players):
            print(player.name)


    def play_hand(self):
        """Play one hand of the game."""

        print("New Hand")
        print("Betting Order:", ", ".join([player.name for player in self.players]))

        # Reset table information
        self.reset_table()
        
        # TODO: Don't ask for bets when the hand should be over

        # Do the stuff
        self.deck = Deck()
        self.deal()
        for i in (3, 1, 1): # flop, turn, river reveal numbers
            # Detect if all players are all in.
            players_all_in = True
            for player in self.players_in_hand:
                if self.chips[player] != 0:
                    players_all_in = False
            if not players_all_in:
                self.round_of_betting(i == 3)
            self.reveal(i)

            # TODO: Add split pot detection?

            # Stop asking for bets if all but one player has folded
            if len(self.players_in_hand) == 1:
                break
        self.payout()
        self.rotate_players()
        print()


    def round_of_betting(self, antes=False):
        """Ask for bets from each player."""
        # NOTE: self.chips[player] is updated immediately after bets are validated.
        print("New Round Of Betting")

        if antes:
            self.antes()
            largest_bet = self.big_blind
            minimum_raise = self.big_blind
        else:
            largest_bet = 0 # minimum amount required to stay in
            minimum_raise = 0

        # TODO: Ask for betting in the right order.
        round_not_over = True
        players_left_to_act = copy(self.players_in_hand)
        while round_not_over:

            round_not_over = False
            for player in self.players_in_hand:
                amount_to_stay_in = largest_bet - self.money_for_pot[player]

                # Prompt player for the bet
                bet = player.bet(GameView(self, player), amount_to_stay_in, minimum_raise)

                # Validate the bet
                if bet < amount_to_stay_in:
                    if bet == self.chips[player]: # valid if all in
                        pass # ok
                    else: # didn't bet enough
                        raise Exception("Bad Bet: Too small")
                if bet > self.chips[player]:
                    raise Exception("Bad Bet: That's more than you have!")

                # Execute the bet
                if bet is None:                                     # Fold
                    self.folded.add(player)
                    self.players_in_hand.remove(player)
                    print(player.name, 'has folded')
                elif bet == 0:                                      # Check
                    print(player.name, 'checks')
                elif bet > amount_to_stay_in:                       # Raise
                    round_not_over = True
                    raise_amount = bet - amount_to_stay_in
                    players_left_to_act = copy(self.players_in_hand)
                    print(player.name, 'has raised', raise_amount)
                elif bet == amount_to_stay_in:                      # Call
                    print(player.name, 'has called for', bet)
                players_left_to_act.remove(player)

                # Adjust chip totals
                self.money_for_pot[player] += bet
                self.chips[player] -= bet
                print(player.name, 'has', self.chips[player], 'chips left.')

                """
                # Update the table
                    for player in self.players:
                        player.update(--Some update information--)
                """     

                largest_bet = max(largest_bet, bet)
                if len(players_left_to_act) == 0:
                    break

            round_not_over = not len(players_left_to_act) == 0

        # put all bets in pot
        for player in self.players:
            self.pot += self.money_for_pot[player]
            self.money_for_pot[player] = 0


    def reset_table(self):
        """Resets the table for a new hand"""

        self.pot = 0
        self.folded = set()
        self.money_for_pot = {player: 0 for player in self.players}
        self.community_cards = []
        self.players_in_hand = copy(self.players)


    def antes(self):
        """Apply the big and little blinds."""
        # TODO: make sure this doesn't make people go negative somehow
        self.players[0]


    def deal(self):
        """"""
        print("Dealing")
        self.hole_cards = {}
        for player in self.players:
            self.hole_cards[player] = self.deck.draw(2)
            print("  ", player.name, [Card.int_to_str(card) for card in self.hole_cards[player]])
        print()


    def reveal(self, n_cards):
        """Reveals a n_cards from the deck and place them in the common cards."""
        for i in range(n_cards):
            self.community_cards.append(self.deck.draw())
        print('community_cards:', [Card.int_to_str(card) for card in self.community_cards], "\n")


    def payout(self):
        """Find winner and give out pot."""
        print("\nFinding Winner")
        best_player = None
        best_score = 999999999
        for player in self.players:

            score = evaluator.evaluate(self.community_cards, self.hole_cards[player])
            if score < best_score:
                best_player = player
                best_score = score

            print(player.name, score, evaluator.class_to_string(evaluator.get_rank_class(score)))
        self.chips[best_player] += self.pot
        print(best_player.name, 'won pot of', self.pot, 'chips.')


    def rotate_players(self):
        """Change the list of players so the """
        self.players.append(self.players.pop(0))



# What is passed to a player on their turn
class GameView:
    """The data that is passed to an agent."""
    def __init__(self, game_state, player):
        self.hole_cards = game_state.hole_cards[player][:]

        self.community_cards = game_state.community_cards[:]
        self.pot = game_state.pot
        # TODO: Security
        self.chips = copy(game_state.chips)
        self.players = game_state.players
        self.money_for_pot = game_state.money_for_pot



if __name__ == '__main__':
    from simon import Simon
    from john import John
    players = [Simon(), John()]
    game = Game(players)

    game.play()
