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
        
        # Set up the table
        # players in order starting left of dealer
        self.players = copy(players)
        self.active_players = copy(players)
        self.busted_players = []
        self.players_in_hand = []
        self.players_left_to_act = []
        self.big_blind = 2
        self.little_blind = 1
        # pots[0] is the main pot
        self.pots = [0]
        self.all_in_players = []
        self.deck = Deck()

        # Starting chips for each player
        self.chips = {}
        for player in players:
            self.chips[player] = 100

        print("New game created with the following players:\n ", ', '.join([player.name for player in players]), "\n")

    def play(self):
        """Simulate an entire game of poker, playing hands until only one player has any chips left."""
        print("Game start:")

        # while game is not over
        while not (len(self.busted_players) + 1 == len(self.players)):
            self.reset_table()
            self.play_hand()

            # Remove busted players from the active game after each hand
            for player in self.players:
                if self.chips[player] == 0:
                    print(player.name, 'is out!')
                    if player not in self.busted_players:
                        self.busted_players.append(player)
                        self.active_players.remove(player)

                else:
                    print(player.name, 'has', self.chips[player], 'chips')

        print('The game has concluded.')
        for player in self.players:
            if player not in self.busted_players:
                print(player.name, 'is the victor!')

        print('These players are ranked from 2nd to last:\n')
        for player in reversed(self.busted_players):
            print(player.name)


    def play_hand(self):
        """Plays one hand of the game."""

        print("New Hand")
        print("Betting Order:", ", ".join([player.name for player in self.players_in_hand]))

        self.reset_table()
        # Makes a new shuffled deck
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

            if len(self.players_in_hand) == 1:
                break # go to payout
        self.payout(self.players_in_hand, self.pots[0])
        self.rotate_players()
        print()


    def round_of_betting(self, first_round=False):
        """Ask for bets from each player."""
        print("New Round Of Betting")

        if first_round:
            self.antes()
            largest_bet = self.big_blind
            minimum_raise = self.big_blind
        else:
            largest_bet = 0 
            minimum_raise = 0

        round_not_over = True
        if first_round:
            self.players_in_hand.append(self.players_in_hand.pop(0))
            self.players_in_hand.append(self.players_in_hand.pop(0))           
        players_left_to_act = copy(self.players_in_hand)

        while round_not_over:

            round_not_over = False
            for player in self.players_in_hand:
                amount_to_stay_in = largest_bet - self.money_for_pot[player]

                # Prompt player for the bet
                bet = player.bet(GameView(self, player), amount_to_stay_in, minimum_raise)

                if bet is None:
                    self.folded.add(player)
                    self.players_in_hand.remove(player)
                    print(player.name, 'has folded')
                    print(player.name, 'has', self.chips[player], 'chips left.')
                    players_left_to_act.remove(player)
                    continue # go to next player
                print(player.name, 'has', self.chips[player], 'chips')
                print('bet amount is', bet)

                # Validate the bet
                if bet < amount_to_stay_in:
                    if bet == self.chips[player]: # valid if all in
                        pass # ok
                    else: # didn't bet enough
                        raise Exception("Bad Bet: Too small")
                if bet > self.chips[player]:
                    raise Exception("Bad Bet: That's more than you have!")

                # Execute the bet
                if bet == 0:                                      # Check
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

                for player in self.players_in_hand:
                    largest_bet = max(largest_bet, self.money_for_pot[player])

                print('larget bet is now', largest_bet)
                if len(players_left_to_act) == 0:
                    break # Break from for loop

            round_not_over = not len(players_left_to_act) == 0

        # put all bets in pot
        for player in self.active_players:
            print('putting', player.name, '\'s money into the pot')
            self.pots[0] += self.money_for_pot[player]
            self.money_for_pot[player] = 0


    def reset_table(self):
        """Resets the table for a new hand"""

        self.pots[0] = 0
        self.folded = set()
        self.money_for_pot = {player: 0 for player in self.active_players}
        self.community_cards = []
        self.players_in_hand = copy(self.active_players)


    def antes(self):
        """Apply the big and little blinds."""

        LB = self.active_players[0]
        BB = self.active_players[1]
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
        for player in self.active_players:
            self.hole_cards[player] = self.deck.draw(2)
            print("  ", player.name, [Card.int_to_str(card) for card in self.hole_cards[player]])
        print()


    def reveal(self, n_cards):
        """Reveals a n_cards from the deck and place them in the common cards."""
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
        for player in best_players:
            self.chips[player] += reward

        print([player.name for player in best_players], 'won', pot_name, 'of', pot, 'chips.')


    def rotate_players(self):
        """Change the list of players so the """
        self.active_players.append(self.active_players.pop(0))




# What is passed to a player on their turn
class GameView:
    """The data that is passed to an agent."""
    def __init__(self, game_state, player):
        self.hole_cards = game_state.hole_cards[player][:]

        self.community_cards = game_state.community_cards[:]
        self.pots = game_state.pots
        # TODO: Security
        self.chips = copy(game_state.chips)
        self.active_players = game_state.active_players
        self.players_in_hand = game_state.players_in_hand
        self.players_folded = list(filter(lambda player: player not in game_state.players_in_hand, game_state.active_players))
        self.money_for_pot = game_state.money_for_pot



if __name__ == '__main__':
    from simon import Simon
    from john import John
    players = [Simon(), Simon(), Simon(), Simon()]
    game = Game(players)

    game.play()
