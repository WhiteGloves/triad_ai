from copy import deepcopy

PLAYER, AI = 0, 1
SIDE = {"U":0, "R":1, "D":2, "L":3, "-U":2, "-R":3, "-D":0, "-L":1}
OFFSET = {"U":(-1,0), "R":(0,1), "D":(1,0), "L":(0,-1)}
CARD_DB = {}
DEBUG = False

class TTCard:
    def __init__(self, name, elem=None):
        self.name = name
        self.elem = elem

    def get_power(self, side):
        return CARD_DB[self.name][SIDE[side]]

    def __str__(self):
        return "[CARD] %-15s %s" % (self.name, CARD_DB[self.name])

class TTCell:
    def __init__(self):
        self.card_name = "Open"
        self.card_elem = None
        self.card_wall = (0, 0, 0, 0)
        self.card_flip = -1

    def set_card(self, card, player):
        self.card_name = card
        self.card_wall = CARD_DB[card]
        self.card_flip = player

    def flip(self):
        self.card_flip = (self.card_flip + 1) % 2

    def __str__(self):
        pass

class TTGrid:
    def __init__(self):
        self.grid = [[TTCell() for x in range(3)] for y in range(3)]
        self.turn = -1

    def update_turn(self, turn=None):
        if turn is None:
            self.turn = (self.turn + 1) % 2
        else:
            self.turn = turn
        return self.turn

    def set_cell(self, row, col, card):
        self.grid[row][col].set_card(card, self.turn)

    def __str__(self):
        pass
    

class TTState:
    def __init__(self, turn, grid=None, hand=None):
        # grid: 3x3 array, each elem = [hand, card, flip]
        if grid is None:
            self.grid = [[[-1,-1,-1] for x in range(3)] for y in range(3)]
        else:
            self.grid = grid
        if hand is None:
            self.hand = [[True] * 5 for __ in range(2)]
        else:
            self.hand = hand
        self.update_turn(turn)

    def adjacent(self, row, col):
        good_range = range(3)
        adj_list = []
        for i in "URDL":
            x, y = OFFSET[i]
            x, y = row + x, col + y
            if (x in good_range and
                y in good_range and
                self.grid[x][y][2] == self.opponent):
                adj_list.append((i, x, y))
        return adj_list

    def get_score(self):
        score = 0
        for row in self.grid:
            for card in row:
                if card[2] == PLAYER:
                    score += 1
                elif card[2] == AI:
                    score -= 1
        return score

    def get_card(self, x, y):
        return self.grid[x][y]

    def possible(self):
        spaces = []
        for x in range(3):
            for y in range(3):
                if self.grid[x][y][2] < 0:
                    spaces.append((x,y))
        return ([x for x in range(5) if self.hand[self.turn][x]], spaces)

    def flip(self, x, y):
        self.grid[x][y][2] = (self.grid[x][y][2] + 1) % 2

    def play(self, card_index, row, col):
        self.hand[self.turn][card_index] = False
        self.grid[row][col] = [self.turn, card_index, self.turn]
        self.update_turn()

    def update_turn(self, turn=None):
        if turn is None:
            self.turn = (self.turn +1) % 2
        else:
            self.turn = turn
        if self.turn == AI:
            self.opponent = PLAYER
        else:
            self.opponent = AI

    def get_turn(self):
        return self.turn

    def copy_state(self):
        return TTState(self.turn,
            deepcopy(self.grid),
            deepcopy(self.hand))

    def __str__(self):
        result = []
        result.append("Player Hand: %s" % (self.hand[PLAYER]))
        result.append("Computer Hand: %s" % (self.hand[AI]))
        result.append("%s\n%s\n%s" % tuple(self.grid))
        result.append("Turn: %s \t Score: %s" %
                      (self.turn, self.get_score()))
        return '\n'.join(result)
    

class TTGame:
    def __init__(self):
        self.state = None
        self.board = [[None, None, None] for __ in range(3)]
        self.hand = [None, None]
        self.turn = 0

    def solve_game(self, player, ai, turn, same=False, diff=True):
        self.hand[AI] = self.build_hand(ai, "AI")
        self.hand[PLAYER] = self.build_hand(player, "PLAYER")
        self.current_turn(turn)
        print self.state
        self.play_card()
        self.play_card()

    def play_card(self, ai_depth=2):
        print "-----"
        card, space, score = self.minimax(self.state, ai_depth)
        print "Minimax: Card=%s Space =%s Score=%s" % (card, space, score)
        self.state_play(self.state, card, space)
        print self.state

    def current_turn(self, turn=None):
        if turn is not None:
            self.turn = turn
            self.state = TTState(turn)
        return self.turn

    def build_hand(self, cards, owner):
        hand = []
        for name in cards:
            if name in CARD_DB:
                card = TTCard(name, owner)
                hand.append(card)
                print card
            else:
                print "Card:", name, "(Not Found!)"
        return hand

    def minimax(self, node, depth=9, turn=PLAYER):
        # if player turn -> maximize, else -> minimize
        #
        if depth == 0:
            return (None, None, node.get_score())
        if DEBUG:
            print "[MINIMAX]", depth, turn
        best = (None, None, 10)
        cards, spaces = node.possible()
        if turn == AI:
            for card in cards:
                for space in spaces:
                    child = node.copy_state()
                    self.state_play(child, card, space)
                    __, __, score = self.minimax(child, depth-1, PLAYER)
                    if score < best[1]:
                        best = (card, space, score)
        elif turn == PLAYER:
            best = (None, -10)
            for card in cards:
                for space in spaces:
                    child = node.copy_state()
                    self.state_play(child, card, space)
                    __, __, score = self.minimax(child, depth-1, AI)
                    if score > best[1]:
                        best = (card, space, score)
        return best

    def state_play(self, node, hand_index, board_index):
        turn = node.get_turn()
        if DEBUG:
            print "Played: %s %s" % (self.hand[turn][hand_index], board_index)
        x, y = board_index
        node.play(hand_index, x, y)
        adj = node.adjacent(x, y)
        for side, ax, ay in adj:
            cx, cy, __ = node.get_card(ax, ay)
            defense = self.hand[cx][cy].get_power("-"+side)
            cx, cy, __ = node.get_card(x, y)
            offense = self.hand[cx][cy].get_power(side)
            if DEBUG:
                print "Combat: Off %d -vs- %d Def" % (offense, defense)
            if offense > defense:
                node.flip(ax, ay)

    def __str__(self):
        result = []
        #result.append("Player Hand: %s" % (self.hand[PLAYER]))
        #result.append("Computer Hand: %s" % (self.hand[AI]))
        result.append("%s" % self.board)
        #result.append("Turn: %s \t Score: %s" %
        #              (self.turn, self.get_score()))
        return '\n'.join(result)

def main():
    triad = TTGame()
    global CARD_DB
    with open('card_db.txt', 'r') as f:
        for line in f:
            name, power = line.split(':')
            CARD_DB[name] = [int(x,11) for x in power.split(',')]
    my_hand = ["Elastoid","Elastoid","Ifrit","MiniMog","Quistis"]
    ai_hand = ["GIM47N","Ruby Dragon","Iron Giant","Malboro","Shumi"]
    triad.solve_game(my_hand, ai_hand, AI)

if __name__ == "__main__":
    main()
