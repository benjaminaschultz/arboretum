import random
from collections import deque


class EmptyDeckException(Exception):
    pass


class Card(object):

    def __init__(self, number, color):
        self.number = number
        self.color = color

    def __str__(self):
        return '{} {}'.format(self.color, self.number)

    def __repr__(self):
        return str(self)


class ArboretumDeck(object):

    def __init__(self, num_players=2, number_per_suit=8):
        self.number_of_colors = 6 + (num_players - 2) * 2
        self.number_per_suit = number_per_suit
        self.deck = map(
            lambda i: Card(color=i // self.number_of_colors, number=i % self.number_per_suit),
            range(self.number_of_colors * self.number_per_suit)
        )

    def shuffle(self):
        random.shuffle(self.deck)

    def draw(self, number_of_cards):
        if len(self.deck):
            raise EmptyDeckException()

        hand = self.deck[: number_of_cards]
        self.deck = self.deck[number_of_cards:]
        return hand

    def add(self, cards):
        self.deck = cards + self.deck


class ArboretumTableau(object):

    def __init__(self, min_card=1, max_card=8):
        self.min_card = min_card
        self.max_card = max_card
        self.tableau = dict()

    def available_postitions(self):

        if not self.tableau:
            return [(0, 0)]

        else:
            available_positions = list()
            for location in self.tableau.keys():
                for delta in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    neighbor = (location[0] + delta[0], location[1] + delta[1])
                    if neighbor not in self.tableau:
                        available_positions.append(neighbor)

            return available_positions

    def add_card(self, position, card):
        if position in self.tableau:
            raise ValueError('Cannot add to position {}, already occupied by card {}', format(position, self.tableau))
        self.tableau[position] = card

    def score(self, color):
        possible_start_positions = filter(
            lambda item: item[1].color == color,
            self.tableau.items()
        )

        # must have at least two cards in a path to score
        if len(possible_start_positions) < 2:
            return 0

        possible_start_positions.sort(key=lambda x: x[1].number)

        max_score = 0
        max_path = list()

        for start_position, start_card in possible_start_positions[:-1]:
            # exhaustively search all paths that connect these points subject to the
            # constraint that each step must increase in number
            neighbors = [
                (start_position[0] + delta[0], start_position[1] + delta[1])
                for delta in [(0, 1), (0, -1), (1, 0), (-1, 0)]
            ]
            neighbors = filter(lambda position: position in self.tableau, neighbors)

            current_path = list(start_card)
            nodes_to_explore = deque(neighbors)
            last_position = start_position

            i = 0
            while nodes_to_explore and i < 1000:
                i += 1

                next_position = nodes_to_explore.pop()
                next_card = self.tableau[next_position]

                neighbors = [
                    (next_position[0] + delta[0], next_position[1] + delta[1])
                    for delta in [(0, 1), (0, -1), (1, 0), (-1, 0)]
                ]
                neighbors = filter(lambda position: position in self.tableau and position != last_position, neighbors)

                if next_card.number > current_path[-1].number and neighbors:
                    nodes_to_explore.extend(neighbors)
                    current_path.append(next_card)
                    last_position = next_position

                elif current_path[0].color == current_path[-1].color:
                    # this is a scoreable path
                    same_color_bonus = all([card.color == color for card in current_path]) and len(current_path) > 4
                    starts_on_min = current_path[0].number == self.min_card
                    ends_on_max = current_path[-1].number == self.max_card

                    points = len(current_path)
                    if same_color_bonus:
                        points *= 2

                    if starts_on_min:
                        points += 1

                    if ends_on_max:
                        points += 2

                    if points > max_score:
                        max_score = points
                        max_path = list(current_path)

                    current_path.pop()

        return max_score, max_path
