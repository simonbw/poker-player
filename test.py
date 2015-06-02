from evaluator import Evaluator
from card import Card
evaluator = Evaluator()


hole_cards = list(map(Card.new, ['5c', '6h']))
community_cards = list(map(Card.new, ['4c', '3c', '2c']))
print("hole_cards     ", " ".join(Card.int_to_pretty_str(card) for card in hole_cards))
print("community_cards", " ".join(Card.int_to_pretty_str(card) for card in community_cards))
print("all_cards      ", " ".join(Card.int_to_pretty_str(card) for card in hole_cards + community_cards))

score = evaluator.evaluate(hole_cards, community_cards)
print("score", score)
print("rank", evaluator.class_to_string(evaluator.get_rank_class(score)))