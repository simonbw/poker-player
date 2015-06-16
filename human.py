from player import Player
from card import Card
import time
import sys

class Human(Player):

    def __init__(self):
        self.name = input("What's your name?\n > ")
        print()

    def bet(self, game_view):
        """
        Called when asking how much a player would like to bet.
        Returning None folds.
        """
        g = game_view
        hole_cards = " ".join([Card.int_to_pretty_str(card) for card in g.hole_cards])
        community_cards = " ".join([Card.int_to_pretty_str(card) for card in g.community_cards])
        print('\n    Action to you', self.name)
        print('    You have', g.my_chips, 'chips.')
        print('    There are', g.pot_size, 'chips in the pot.')
        print('    Other players chips:')
        opposing_chip_stacks = " -- ".join([str(chips[0]) + ':' + str(chips[1]) for chips in g.chips.items()])
        print('        ', opposing_chip_stacks)

        if community_cards:
            print('    Community cards are:', community_cards)
        print('    Your cards are:', hole_cards)

        if g.my_chips == 0:
            print("    You're all in!")
            return min(g.min_bet, g.my_chips)
        prompt = "    It's {0} to stay in and minimum raise is {1}.\n    What would you like to do?\n     > ".format(g.min_bet if g.min_bet > 0 else 'free', g.min_raise)
        while True:
            n = input(prompt).split(' ')
            print()
            if len(n) == 1:
                action = n[0]
            else:
                action, amount = n
            action = action.lower()

            if action == 'fold':
                return None
            if action == 'check':
                if g.min_bet == 0:
                    return 0
                else:
                    print("    You can't check. You must fold or bet at least", min(g.my_chips, g.min_bet))
            if action == 'call':
                return min(g.min_bet, g.my_chips)
            if action in ('raise', 'bet'):
                if amount == 'all':
                    return g.my_chips
                try:
                    amount = int(amount)
                except:
                    print("    You must bet an integer number of chips.")
                    continue

                if action == 'raise':
                    amount += g.min_bet

                if amount < g.min_bet and amount < g.my_chips:
                    print("    You must bet at least", min(g.my_chips, g.min_bet))
                    continue
                if amount > g.min_bet and amount < (g.min_bet + g.min_raise) and amount < g.my_chips:
                    print("    You must raise by at least", g.min_raise)
                    continue
                if amount > g.my_chips:
                    print("    You don't have that many chips.")
                    continue
                return int(amount)
            if action == 'all':
                return g.my_chips
            if action in ('quit', 'exit'):
                sys.exit()
            print("    I don't understand. Try again.")

    def on_bet(self, player_name, action, amount, game_view):
        """
        Called when another player makes a bet.
        @param player_name - unique name of the player 
        @param action - One of the strings: "check" "call" "fold" "raise"
        @param amount - The amount put in to call or the amount raised by or None (fold).
        @param game_view - A game view with all the data.
        """
        time.sleep(0.2)

    def on_new_round(self, game_view):
        """Called at the beginning of a new round of betting."""
        time.sleep(0.2)
        community_cards = " ".join([Card.int_to_pretty_str(card) for card in game_view.community_cards])
        # print("\nNew Round of Betting")
        # print(community_cards)

    def on_new_hand(self, game_view):
        """Called at the beginning of a new hand."""
        hole_cards = " ".join([Card.int_to_pretty_str(card) for card in game_view.hole_cards])
        # print("\nNew Hand. Your cards are", hole_cards)

    def on_hand_end(self, winner, pot, game_view):
        """Called at the end of a hand."""
        time.sleep(1)
        if winner == self.name:
            print("You won the pot of", pot)
        # else:
        #     print(winner, "won the pot of", pot)

    def on_new_game(self, players):
        """Called at the beginning of a new game."""
        time.sleep(0.2)
        # print("\nLet the game begin!")

    def on_bust(self):
        print("YOU WENT BUST!")
        time.sleep(5)