from copy import deepcopy

SIDE = {"U":0, "R":1, "D":2, "L":3, "-U":2, "-R":3, "-D":0, "-L":1}
OFFSET = {"U":(-1,0), "R":(0,1), "D":(1,0), "L":(0,-1)}
CARD_DB = {}
DEBUG = True

_WIDTH = 21
_CARD_FORMAT = "|{{:^{}}}|".format(_WIDTH)

def card_power(name, side, opposite=False):
    index = "URDL".index(side)
    if opposite:
        index = "DLUR".index(side)
    return int(CARD_DB[name][index], 11)

class TTCell:
    def __init__(self):
        self.card_name = "Open"
        self.card_elem = None
        self.card_flip = -1

    def set_card(self, card, player):
        self.card_name = card
        self.card_flip = player

    def combat(self, side, opponent):
        if (self.card_name != "Open" and
            card_power(opponent, side, True) >
            card_power(self.card_name, side)):
            self.card_flip = (self.card_flip + 1) % 2

    def cell_text(self):
        up = right = down = left = " "
        if self.card_name in CARD_DB:
            up, right, down, left = CARD_DB[self.card_name]
        border = _CARD_FORMAT.format("-" * _WIDTH)
        gap = _CARD_FORMAT.format("")
        mid = "|{:<}{{:^{}}}{:>}|".format(left, _WIDTH-2, right)
        return [border, _CARD_FORMAT.format(up), gap,
            mid.format(self.card_name),
            gap, _CARD_FORMAT.format(down), border]

    def __str__(self):
        return '\n'.join(self.cell_text())
        

class TTGrid:
    def __init__(self, turn):
        self.grid = [[TTCell() for x in range(3)] for y in range(3)]
        self.turn = turn
        self.grid_range = range(3)

    def update_turn(self, turn=None):
        if turn is None:
            self.turn = (self.turn + 1) % 2
        else:
            self.turn = turn
        return self.turn

    def play_card(self, row, col, card):
        self.grid[row][col].set_card(card, self.turn)
        for side in "URDL":
            x, y = OFFSET[side]
            x += row
            if x in self.grid_range:
                y += col
                if y in self.grid_range:
                    self.grid[x][y].combat(side, card)

    def __str__(self):
        lines = []
        for grid_row in self.grid:
            row = [card.cell_text() for card in grid_row]
            for x in zip(row[0],row[1],row[2]):
                lines.append(''.join(x))
        return '\n'.join(lines)
            

class TTGame:
    HUMAN, NPC = 0, 1
    
    def __init__(self):
        self.board = None
        self.hand = None
        self.turn = -1

    def setup_game(self):
        self.hand = [
            ["Elastoid","Elastoid","Ifrit","MiniMog","Quistis"],
            ["GIM47N","Ruby Dragon","Iron Giant","Malboro","Shumi"]]
        self.turn = TTGame.NPC
        self.board = TTGrid(self.turn)
        self.advance_turn()

    def solve_game(self, player, ai, turn, same=False, diff=True):
        pass

    def advance_turn(self, depth=2):
        #self.board.play_card(1, 1, "Ruby Dragon")
        print self.board

        play = input("Play Card? ").split()
        card = self.hand[self.turn][int(play[0])]
        space = (int)

    def show_hand(self):
        print "Cards:", ', '.join(self.hand[self.turn])
        
        
    def play_card(self, ai_depth=2):
        card, space, score = self.minimax(self.state, ai_depth)
        self.state_play(self.state, card, space)

    def __str__(self):
        return str(self.board)

def main():
    triad = TTGame()
    global CARD_DB
    with open('card_db.txt', 'r') as f:
        for line in f:
            name, power = line.rstrip().split(':')
            CARD_DB[name] = power.split(',')
    triad.setup_game()
    #test = TTCell()
    #test.set_card("Ruby Dragon", PLAYER)
    #print test

if __name__ == "__main__":
    main()
