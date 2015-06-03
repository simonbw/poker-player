from evaluator import Evaluator
from card import Card
from util import Util
evaluator = Evaluator()
util = Util()
average_range= set()
for set_ in Util.PAIRS.values():
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

hole_cards = list(map(Card.new, ['Ah', 'Jd']))
community_cards = list(map(Card.new, ['2c', 'Qh', '9d']))
print("hole_cards     ", " ".join(Card.int_to_pretty_str(card) for card in hole_cards))
print("community_cards", " ".join(Card.int_to_pretty_str(card) for card in community_cards))
print("all_cards      ", " ".join(Card.int_to_pretty_str(card) for card in hole_cards + community_cards))

score = evaluator.evaluate(hole_cards, community_cards)
print("score", score)
print("rank", evaluator.class_to_string(evaluator.get_rank_class(score)))

print(util.my_equity(tuple(hole_cards), tuple(community_cards), average_range))