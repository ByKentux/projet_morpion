class Grid:
    EMPTY = 0
    J1 = 1
    J2 = 2
    NB_CELLS = 9
    SYMBOLS = [' ', 'O', 'X']

    def __init__(self):
        self.cells = [self.EMPTY] * self.NB_CELLS

    def play(self, player, cell):
        assert 0 <= cell < self.NB_CELLS
        assert self.cells[cell] == self.EMPTY
        self.cells[cell] = player

    def display_string(self):
        result = "-------------\n"
        for i in range(3):
            result += f"| {self.SYMBOLS[self.cells[i * 3]]} | {self.SYMBOLS[self.cells[i * 3 + 1]]} | {self.SYMBOLS[self.cells[i * 3 + 2]]} |\n"
            result += "-------------\n"
        return result

    def game_over(self):
        for y in range(3):
            if self.cells[y * 3] == self.cells[y * 3 + 1] == self.cells[y * 3 + 2] != self.EMPTY:
                return self.cells[y * 3]
        for x in range(3):
            if self.cells[x] == self.cells[3 + x] == self.cells[6 + x] != self.EMPTY:
                return self.cells[x]
        if self.cells[0] == self.cells[4] == self.cells[8] != self.EMPTY:
            return self.cells[0]
        if self.cells[2] == self.cells[4] == self.cells[6] != self.EMPTY:
            return self.cells[2]
        if self.EMPTY not in self.cells:
            return 0
        return -1