import random
from player import Player
from evaluator import Evaluator
from card import Card
from deck import Deck
from itertools import combinations

evaluator = Evaluator()

WORST_SCORE = 7462


class Simon(Player):
    def bet(self, game_view):
        score = 0

        opponent_score = self.estimate_opponent_score(game_view)
        my_win_chance = self.my_win_chance(game_view, opponent_score)


        # print("Estimated opponent score:", opponent_score, "My estimated win chance:", my_win_chance)

        # TODO: Detect bluffing
        # TODO: Bluff

        if my_win_chance > 0.5:
            target_bet = game_view.minimum_bet + game_view.minimum_raise * 4 * my_win_chance * my_win_chance
            return min(target_bet, game_view.chips[self.name])
        else:
            # Don' fold if we don't have to
            if game_view.minimum_bet == 0:
                return 0
            return None

    def estimate_opponent_score(self, game_view):
        """Return my best guess of the best hand of all my opponents."""
        score = WORST_SCORE
        for i in range(len(game_view.players_in_hand) - 1):
            score = min(score, random.randint(WORST_SCORE / 2, WORST_SCORE))
        return score

    def my_win_chance(self, game_view, opponent_score):
        """Return the chance I have of beating the score."""
        if len(game_view.community_cards) == 0: # before flop
            return self.my_win_chance_before_flop(game_view.hole_cards, opponent_score) # after flop
        elif len(game_view.community_cards) == 3:
            return self.my_win_chance_after_flop(game_view.hole_cards, game_view.community_cards, opponent_score)
        elif len(game_view.community_cards) == 4: # after turn
            return self.my_win_chance_after_river(game_view.hole_cards, game_view.community_cards, opponent_score)
        else: # after river
            return evaluator.evaluate(game_view.community_cards, game_view.hole_cards)

    def my_win_chance_before_flop(self, hole_cards, opponent_score):
        """Return how good a set of hole cards are with no other information."""
        # too hard to go through and evaluate all possibilities, but we can have a pretty good guess
        score = 0
        card_ranks = [Card.get_rank_int(card) for card in hole_cards]
        if card_ranks[0] == card_ranks[1]:
            score += 0.1 * (card_ranks[0] / 13.0) ** 2
        else:
            score += 0.1 * (card_ranks[0] / 13.0) ** 2
            score += 0.1 * (card_ranks[1] / 13.0) ** 2
        return 0.5 + 0.5 * evaluator.get_five_card_rank_percentage(opponent_score)

    def my_win_chance_after_flop(self, hole_cards, community_cards, opponent_score):
        """Return how good a set of hole cards are with given the flop."""
        wins = 0
        deck = self.get_remaining_deck(hole_cards + community_cards)
        for cards in combinations(deck, 2):
            score = evaluator.evaluate(hole_cards, community_cards + list(cards))
            if score < opponent_score:
                wins += 1
            elif score == opponent_score:
                wins += 0.5
        return wins / len(deck)

    def my_win_chance_after_river(self, hole_cards, community_cards, opponent_score):
        """Return how good a set of hole cards are with given the flop and river."""
        wins = 0
        deck = self.get_remaining_deck(hole_cards + community_cards)
        for card in deck:
            score = evaluator.evaluate(hole_cards, community_cards + [card])
            if score < opponent_score:
                wins += 1
            elif score == opponent_score:
                wins += 0.5
        return wins / len(deck)

    def my_win_chance_after_turn(self, hole_cards, community_cards, opponent_score):
        """Return how good a set of hole cards are with given the flop and river."""
        score = evaluator.evaluate(game_view.community_cards, game_view.hole_cards)
        return int(score > opponent_score)

    def get_remaining_deck(self, known_cards):
        """Returns array of all cards remaining in the deck."""
        known_cards = set(known_cards)
        deck = Deck.GetFullDeck()
        deck = filter(lambda card: card not in known_cards, deck)
        return list(deck)


