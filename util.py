from evaluator import Evaluator
from card import Card
from deck import Deck
from itertools import combinations

evaluator = Evaluator()

class Util():
    # In order of 2 - A, s-c-h-d
    FULL_DECK = set()
    # In order of 2:deck, 3: deck-2, 4: deck-2,3
    # d-c-s-h
    ALL_HOLE_CARDS = []
    # Tuples
    # key = pair rank eg 'A': {H|H is a tuple of 2 cards with rank = 'A'}
    PAIRS = {}
    # Key = higherRank + lowerRank eg. 'AK'
    SUITED = {}
    UNSUITED = {}
    SUITED_CONNECTORS = {}

    ROUND_NAMES = { 
        0: 'Preflop',
        3: 'Postflop',
        4: 'Turn',
        5: 'River'
    }
    

    def __init__(self):
        self._initiate_opening_hands()


    def my_equity(self, hole_cards, community_cards, opponent_range):
        """
        Return the percent of times hole_cards beats opponent_range.
        @param hole_cards - tuple of 2 cards as ints defined by card.py
        @param community_cards - 
        @param opponent_range - set of tuples that represent hole cards
        """
        community_cards = tuple(community_cards)
        if len(community_cards) == 0:
            return self.win_chance_preflop(hole_cards, opponent_range)
        elif len(community_cards) == 3:
            return self.win_chance_postflop(hole_cards, community_cards, opponent_range)
        elif len(community_cards) == 4:
            return self.win_chance_after_turn(hole_cards, community_cards, opponent_range)
        else:
            return self.win_chance_after_river(hole_cards, community_cards, opponent_range)

    def win_chance_preflop(self, my_hole_cards, opponent_hole_cards):
        """Return how good a set of hole cards are with no other information."""
        # too hard to go through and evaluate all possibilities, but we can have a pretty good guess
        # TODO: Use opening hand equity tables! woohoo
        return 0

    def win_chance_postflop(self, hole_cards, community_cards, opponent_range):
        """
        Return how good a set of hole cards are with given the flop.
        @param hole_cards - tuple of 2 cards as ints defined by card.py
        @param community_cards -
        @param opponent_range - set of tuples
        Assumes opponent_range cards are all equally likely
        """
        wins = 0
        possible_events = 0
        for opposing_hand in opponent_range:
            if (opposing_hand[0] in community_cards + hole_cards or
                opposing_hand[1] in community_cards + hole_cards):
                continue
            deck = self.get_remaining_deck(hole_cards + community_cards + opposing_hand)
            for cards in combinations(deck, 2):
                possible_events += 1
                my_score = evaluator.evaluate(hole_cards, community_cards + cards)
                opposing_score = evaluator.evaluate(opposing_hand, community_cards + cards)
                if my_score < opposing_score:
                    wins += 1
                elif my_score == opposing_score:
                    wins += 0.5
        possible_events = max(possible_events, 1)
        return wins / possible_events

    def win_chance_after_turn(self, hole_cards, community_cards, opponent_range):
        """Return how good a set of hole cards are with given the flop and river."""
        wins = 0
        possible_events = 0
        for opposing_hand in opponent_range:
            if (opposing_hand[0] in community_cards + hole_cards or
                opposing_hand[1] in community_cards + hole_cards):
                continue
            deck = self.get_remaining_deck(hole_cards + community_cards + opposing_hand)
            for cards in deck:
                possible_events += 1
                my_score = evaluator.evaluate(hole_cards, community_cards + (cards,))
                opposing_score = evaluator.evaluate(opposing_hand, community_cards + (cards,))
                if my_score < opposing_score:
                    wins += 1
                elif my_score == opposing_score:
                    wins += 0.5
        possible_events = max(possible_events, 1)
        return wins / possible_events

    def win_chance_after_river(self, hole_cards, community_cards, opponent_range):
        """Return how good a set of hole cards are with given the flop and river."""
        possible_events = 0
        wins = 0
        for opposing_hand in opponent_range:
            if (opposing_hand[0] in community_cards + hole_cards or
                opposing_hand[1] in community_cards + hole_cards):
                continue
            possible_events += 1
            my_score = evaluator.evaluate(hole_cards, community_cards)
            opposing_score = evaluator.evaluate(opposing_hand, community_cards)
            if my_score < opposing_score:
                wins += 1
            elif my_score == opposing_score:
                wins += 0.5
        possible_events = max(possible_events, 1)
        return wins / possible_events

    def get_remaining_deck(self, known_cards):
        """Returns array of all cards remaining in the deck."""
        known_cards = set(known_cards)
        deck = Util.FULL_DECK
        return deck - known_cards

    def _initiate_opening_hands(self):
        for rank in Card.STR_RANKS:
            for suit,val in Card.CHAR_SUIT_TO_INT_SUIT.items():
                Util.FULL_DECK.add(Card.new(rank + suit))
        for combo in combinations(Util.FULL_DECK, 2):
            Util.ALL_HOLE_CARDS.append(combo)
            cards = Card.int_to_str(combo[0]) + Card.int_to_str(combo[1])
            c1_rank, c1_suit, c2_rank, c2_suit = cards
            # Check for pairs
            if c1_rank == c2_rank:
                for rank in Card.STR_RANKS:
                    if c1_rank == rank:
                        if rank not in Util.PAIRS:
                            Util.PAIRS[rank] = set()
                        Util.PAIRS[rank].add(combo)
            else:
                for rank_pair in combinations(Card.STR_RANKS[::-1], 2):
                    ranks = rank_pair[0] + rank_pair[1]
                    if rank_pair == (c2_rank, c1_rank) or rank_pair == (c1_rank, c2_rank):
                        if c1_suit == c2_suit:  # Suited!
                            if ranks not in Util.SUITED:
                                Util.SUITED[ranks] = set()
                            Util.SUITED[ranks].add(combo)
                            if Card.STR_RANKS.index(rank_pair[0]) == 1 + Card.STR_RANKS.index(rank_pair[1]):
                                if ranks not in Util.SUITED_CONNECTORS:
                                    Util.SUITED_CONNECTORS[ranks] = set()
                                Util.SUITED_CONNECTORS[ranks].add(combo)
                            #print(ranks, Card.int_to_str(combo[0]), Card.int_to_str(combo[1]))
                        else:
                            if ranks not in Util.UNSUITED:
                                Util.UNSUITED[ranks] = set()
                            Util.UNSUITED[ranks].add(combo)
                            #print(ranks, Card.int_to_str(combo[0]), Card.int_to_str(combo[1]))