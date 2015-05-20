import random
from card import Card
from deck import Deck
from evaluator import Evaluator

evaluator = Evaluator()

class Game:
    """"""

    def __init__(self, players):
        """"""

        self.players = players
        print("New Game:", ', '.join([player.name for player in players]), "\n\n")

        self.big_blind = 2
        self.little_blind = 1

        self.chips = {}
        for player in players:
            self.chips[player] = 100

    def play(self):
        """"""

        while True: # game not over
            self.play_hand()

    def play_hand(self):
        """Play 1 hand of the game."""

        print("New Hand")
        print("Betting Order:", ", ".join([player.name for player in self.players]))

        # Reset stuff
        self.pot = 0
        self.folded = set()
        self.money_for_pot = {player: 0 for player in self.players}
        self.community_cards = []

        # TODO: Don't ask for bets when the hand should be over

        # Do the stuff
        self.deck = Deck()
        self.deal()
        self.round_of_betting(True)
        self.reveal(3) # flop
        self.round_of_betting()
        self.reveal(1) # turn
        self.round_of_betting()
        self.reveal(1) # river
        self.round_of_betting()
        self.payout()
        self.rotate_players()
        print()

    def antes(self):
        """"""
        self.money_for_pot

    def deal(self):
        """"""
        print("Dealing")
        self.hole_cards = {}
        for player in self.players:
            self.hole_cards[player] = self.deck.draw(2)
            print("  ", player.name, [Card.int_to_str(card) for card in self.hole_cards[player]])
        print()

    def reveal(self, n_cards):
        """"""
        for i in range(n_cards):
            self.community_cards.append(self.deck.draw())
        print('community_cards:', [Card.int_to_str(card) for card in self.community_cards], "\n")

    def round_of_betting(self, antes=False):
        """"""
        print("New Round Of Betting")

        if antes:
            self.antes()
            largest_bet = self.big_blind
        else:
            largest_bet = 0 # minimum amount required to stay in

        raised = True
        while raised:
            if random.random() < 0.001:
                break
            
            raised = False
            for player in self.players:
                # Skip players who have folded
                if player in self.folded:
                    continue

                amount_to_stay_in = largest_bet - self.money_for_pot[player]
                bet = player.bet(GameView(self, player), amount_to_stay_in)

                if bet is None: # Fold
                    self.folded.add(player)
                    print(player.name, 'folded')
                    continue
                elif bet < amount_to_stay_in:
                    if bet + self.money_for_pot[player] == self.chips[player]: # valid if all in
                        pass # ok
                    else: # didn't bet enough
                        raise Exception("Bad Bet: Too small")
                else: # call / check
                    # TODO: Validity checks
                    if bet > amount_to_stay_in:
                        raised = True
                    self.money_for_pot[player] += bet

                largest_bet = max(largest_bet, bet)
                print(player.name, 'bet', bet, "\n")

        # put all bets in pot
        for player in self.players:
            self.pot += self.money_for_pot[player]
            self.money_for_pot[player] = 0

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
        print(best_player.name, 'won pot of', self.pot)


    def rotate_players(self):
        self.players.insert(0, self.players.pop())



# What is passed to a player on their turn
class GameView:
    """"""
    def __init__(self, game_state, player):
        self.hole_cards = game_state.hole_cards[player][:]

        self.community_cards = game_state.community_cards[:]
        self.pot = game_state.pot
        # TODO: Security
        self.chips = game_state.chips
        self.players = game_state.players
        self.money_for_pot = game_state.money_for_pot

# 
class Player:
    player_count = 0
    def __init__(self):
        Player.player_count += 1
        self.name = 'Player' + str(Player.player_count)

    def bet(self, game_view, minimum):
        return minimum


class Simon(Player):
    agent_count = 0
    def __init__(self):
        Simon.agent_count += 1
        self.name = 'Simon' + str(Simon.agent_count)

    def bet(self, game_view, minimum):
        return minimum + 1



if __name__ == '__main__':
    from simon import Simon
    from john import John
    players = [Simon(), John()]
    game = Game(players)

    game.play_hand()
