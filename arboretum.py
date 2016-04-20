import random
from collections import deque
from colorama import Back, Fore


class EmptyDeckException(Exception):
    pass


class Card(object):
    BG_COLORS = [
        Back.GREEN,
        Back.BLUE,
        Back.RED,
        Back.WHITE,
        Back.YELLOW,
        Back.MAGENTA,
        Back.CYAN,
        Back.LIGHTBLACK_EX,
        Back.LIGHTRED_EX,
        Back.LIGHTBLUE_EX
    ]

    def __init__(self, number, color):
        self.number = number
        self.color = color

    def __str__(self):
        return '{}{}{}'.format(
            self.BG_COLORS[self.color] + Fore.BLACK,
            self.number,
            Back.RESET + Fore.RESET
        )

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

    def __len__(self):
        return len(self.deck)

    def pop(self):
        return self.draw(1)

    def draw(self, number_of_cards):
        if len(self.deck) == 0:
            raise EmptyDeckException()

        hand = self.deck[: number_of_cards]
        self.deck = self.deck[number_of_cards:]
        return hand


class ArboretumTableau(object):

    def __init__(self, min_card=1, max_card=8):
        self.min_card = min_card
        self.max_card = max_card
        self.tableau = dict()

    def available_positions(self):
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

            current_path = [start_card]
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

                elif len(current_path) > 1 and current_path[0].color == current_path[-1].color:
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

    def __str__(self):
        coords = self.tableau.keys()
        if not coords:
            return ''

        xs = map(lambda x: x[0], coords)
        ys = map(lambda x: x[1], coords)

        min_x = min(xs)
        max_x = max(xs)

        min_y = min(ys)
        max_y = max(ys)

        dim_x = max_x - min_x + 0
        dim_y = max_y - min_y + 1

        tableau_string = ''
        for ix in range(dim_x):
            for iy in range(dim_y):
                tableau_string += str(self.tableau.get((ix + min_x, iy + min_y)) or ' ')
            tableau_string += '\n'

        return tableau_string


class ArboretumTurn(object):

    def __init__(
        draws,
        card_to_play,
        card_to_discard
        )


class ArboretumPlayer(object):

    def __init__(self, hand, discard_pile=None):
        self.hand = hand
        self.discard_pile = deque([]) if discard_pile is None else deque(discard_pile)
        self.tableau = ArboretumTableau()

    def add_to_hand(self, cards):
        self.hand.extend(cards)

    @property
    def top_discard(self):
        if self.discard_pile:
            return self.discard_pile[-1]
        else:
            None

    def print_state(self):
        self.hand.sort(key = lambda x: (x.color, x.number))
        print 'Hand: {}'.format('{}'.format(''.join(map(str, self.hand))))
        print 'Discard {:s}'.format(self.top_discard or 'X')
        print 'Tableau:\n{:s}'.format(self.tableau)


class ArboretumGame(object):

    def __init__(self, num_players):
        self.deck = ArboretumDeck(num_players=num_players)
        self.deck.shuffle()

        hands  = [self.deck.draw(7) for i in range(num_players)]
        discard_piles = [None] + [self.deck.draw(1) for i in range(num_players - 1)]

        self.players = [ArboretumPlayer(hand=hand, discard_pile=discard_pile)
            for hand, discard_pile in zip(hands, discard_piles)]

        self.current_player_number = 0

    def get_moves(self):
        draw_options = list()
        draw_decks = list()
        first_draw_options = None


    def print_state(self):
        for i, player in enumerate(self.players):
            print('Player {}'.format(i))
            player.print_state()
            print(30 * '-')
