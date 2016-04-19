from arboretum import ArboretumDeck, ArboretumTableau

deck = ArboretumDeck()
tableau = ArboretumTableau()

hand = deck.draw(7)
hand = sorted(hand, key=lambda x: (x.number, x.color))

while hand:
    card = hand.pop()
    position = tableau.available_positions()[0]
    tableau.add_card(card=card, position=position)

for color in range(10):
    print(color, tableau.score(color))
