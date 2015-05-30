class Event():
	# Event Types:
	NEW_GAME = 0
	NEW_HAND = 1
	NEW_ROUND_OF_BETTING = 2
	PLAYER_ACTION = 3
	END_ROUND_OF_BETTING = 4
	END_HAND = 5

	# Action Types:
	CHECK = 0
	FOLD = 1
	RAISE = 2
	CALL = 3

	"""
	Class that handles game events

	"""

	def __init__(self, event_type, data):
		if event_type is NEW_GAME:
			pass
		elif event_type is NEW_HAND:
			self.hole_cards = data.hole_cards
		elif event_type is NEW_ROUND_OF_BETTING:
			pass
		elif event_type is PLAYER_ACTION:
			self.player = data.player_name
			self.action_type = data.action_type
			self.bet = data.bet
		elif event_type is END_ROUND_OF_BETTING:
			pass
		elif event_type is END_HAND:
			pass