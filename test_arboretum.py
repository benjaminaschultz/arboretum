import random
from arboretum import ArboretumDeck, ArboretumTableau, ArboretumGame

game =  ArboretumGame(4)
for player in game.players:
    player.add_to_hand(game.deck.draw(10))
    for card in player.hand[0:10]:
        positions = player.tableau.available_positions()
        random.shuffle(positions)
        position = positions[0]
        player.tableau.add_card(card=card, position=position)

    player.hand = player.hand[-7:]
        
game.print_state()

