# References:
#    HW9_Coding.pdf
# ChatGPT queries:
#    try catch block for index out of bounds error in python

import random


class TeekoPlayer:
    """An object representation for an AI game player for the game Teeko."""

    board = [[" " for j in range(5)] for i in range(5)]
    pieces = ["b", "r"]

    def __init__(self):
        """Initializes a TeekoPlayer object by randomly selecting red or black as its
        piece color.
        """
        self.my_piece = random.choice(self.pieces)
        self.opp = self.pieces[0] if self.my_piece == self.pieces[1] else self.pieces[1]

    def run_challenge_test(self):
        # Set to True if you would like to run gradescope against the challenge AI!
        return True

    def drop_help(self, state):
        """from curr state, get if game is in drop stage"""
        tiles = 0
        drop = True

        for row in state:
            for element in row:
                if element != " ":
                    tiles += 1

        if tiles == 8:  # all tiles placed, no longer in drop stage
            drop = False

        return drop

    def succ(self, state, p):
        """get successor states from current state, based on player and stage"""
        # state = [  # hardcoded state for troubleshooting
        #     ["r", "r", "r", "r", " "],
        #     ["b", "b", "b", "b", " "],
        #     [" ", " ", " ", " ", " "],
        #     [" ", " ", " ", " ", " "],
        #     [" ", " ", " ", " ", " "],
        # ]

        succs = []
        if p == 1:
            player = self.my_piece
        else:
            player = self.opp
        drop = self.drop_help(state)

        if drop:  # curr player can put their piece in any open spot
            for i in range(5):
                for j in range(5):
                    if state[i][j] == " ":
                        next = [x[:] for x in state]
                        next[i][j] = player
                        succs.append(next)
        else:  # curr player moves one of their pieces to adjacent open spot
            for i in range(5):
                for j in range(5):
                    if state[i][j] == player:  # curr player piece found
                        for row in range(max(i - 1, 0), min(i + 2, 5)):
                            for col in range(max(j - 1, 0), min(j + 2, 5)):
                                next = [x[:] for x in state]
                                if next[row][col] == " ":  # open adjacent spot found
                                    next[i][j] = " "  # curr spot emptied
                                    next[row][col] = player  # new spot gets piece
                                    succs.append(next)

        # if not drop:
        #     count = 0  # print out each successor state
        #     for val in succs:
        #         for row in val:
        #             print(row)
        #         if not count % 5:
        #             count += 1
        #         if count % 5:
        #             print("\n")

        return succs

    def heuristic_game_value(self, state, p):
        """if state is terminal, return 1 if ai wins or -1 if user wins
        else, return number of linkages that ai has (how many adjacent
        connections there are, max of 3, divided by 4 to normalize)"""
        terminal = self.game_value(state)  # see if curr state is terminal
        if terminal != 0:
            return terminal

        if p == 1:  # see what piece we're evaluating heuristic on
            piece = self.my_piece
        else:
            piece = self.opp

        link = 0  # num of linkages

        adjacent = [  # directions to check from each piece
            [-1, -1],
            [-1, 0],
            [-1, 1],
            [0, -1],
            [0, 1],
            [-1, 1],
            [1, 0],
            [1, 1],
        ]

        seen = []
        for i in range(5):
            for j in range(5):
                if state[i][j] == piece:  # if piece found
                    for space in adjacent:  # check adjacent spaces for matches
                        ip = i + space[0]
                        jp = j + space[1]
                        # stay in bounds
                        if ip >= 0 and ip <= 4 and jp >= 0 and jp <= 4:
                            # check matches not already seen
                            if state[ip][jp] == piece and [ip, jp] not in seen:
                                link += 1
                                if len(seen) == 0:  # don't double count first one
                                    seen.append([i, j])
                                seen.append([ip, jp])

        return (link * p) / 4  # normalize, make negative if for opp pieces

    def make_move(self, state):
        """Selects a (row, col) space for the next move. You may assume that whenever
        this function is called, it is this player's turn to move.

        Args:
            state (list of lists): should be the current state of the game as saved in
                this TeekoPlayer object. Note that this is NOT assumed to be a copy of
                the game state and should NOT be modified within this method (use
                place_piece() instead). Any modifications (e.g. to generate successors)
                should be done on a deep copy of the state.

                In the "drop phase", the state will contain less than 8 elements which
                are not ' ' (a single space character).

        Return:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

        Note that without drop phase behavior, the AI will just keep placing new markers
            and will eventually take over the board. This is not a valid strategy and
            will earn you no points.
        """
        best = self.best_response_h(state, 2)
        drop_phase = self.drop_help(state)
        move = []

        if not drop_phase:  # must find piece to switch
            for i in range(5):
                for j in range(5):
                    if state[i][j] != best[i][j]:  # mismatch
                        if state[i][j] == " ":  # was it empty, then moved to?
                            dest = (i, j)
                        else:  # otherwise, it had piece before switch
                            orig = (i, j)
            move.insert(0, dest) # where to switch to
            move.insert(1, orig) # where to switch from

        else: # only have to find where to put new piece
            for i in range(5):
                for j in range(5):
                    if state[i][j] != best[i][j]:  # find where piece is put
                        (row, col) = (i, j)
            move.insert(0, (row, col))

        return move

    def best_response_h(self, state, depth):
        a = []

        v = self.heuristic_game_value(state, -1)  # if opponent in win state
        if abs(v) == 1:
            return a

        succ = self.succ(state, 1)
        v = -2
        for sp in succ:
            cur = self.max_value(sp, -1, depth - 1)
            if cur > v:
                v = cur
                a = sp

        return a

    def max_value(self, state, player, depth):
        if depth == 0:
            return self.heuristic_game_value(state, player)  # estimate if at depth

        v = self.heuristic_game_value(state, -1 * player)  # goal check for other player
        if abs(v) == 1:
            return v  # return if terminal state

        succs = self.succ(state, player)

        if player == 1:
            v = -1
            for sp in succs:
                v = max(v, self.max_value(sp, -1 * player, depth - 1))
        else:
            v = 1
            for sp in succs:
                v = min(v, self.max_value(sp, -1 * player, depth - 1))

        return v

    def opponent_move(self, move):
        """Validates the opponent's next move against the internal board representation.
        You don't need to touch this code.

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.
        """
        # validate input
        if len(move) > 1:
            source_row = move[1][0]
            source_col = move[1][1]
            if source_row != None and self.board[source_row][source_col] != self.opp:
                self.print_board()
                print(move)
                raise Exception("You don't have a piece there!")
            if abs(source_row - move[0][0]) > 1 or abs(source_col - move[0][1]) > 1:
                self.print_board()
                print(move)
                raise Exception("Illegal move: Can only move to an adjacent space")
        if self.board[move[0][0]][move[0][1]] != " ":
            raise Exception("Illegal move detected")
        # make move
        self.place_piece(move, self.opp)

    def place_piece(self, move, piece):
        """Modifies the board representation using the specified move and piece

        Args:
            move (list): a list of move tuples such that its format is
                    [(row, col), (source_row, source_col)]
                where the (row, col) tuple is the location to place a piece and the
                optional (source_row, source_col) tuple contains the location of the
                piece the AI plans to relocate (for moves after the drop phase). In
                the drop phase, this list should contain ONLY THE FIRST tuple.

                This argument is assumed to have been validated before this method
                is called.
            piece (str): the piece ('b' or 'r') to place on the board
        """
        if len(move) > 1:
            # print("move", move)
            self.board[move[1][0]][move[1][1]] = " "
        self.board[move[0][0]][move[0][1]] = piece

    def print_board(self):
        """Formatted printing for the board"""
        for row in range(len(self.board)):
            line = str(row) + ": "
            for cell in self.board[row]:
                line += cell + " "
            print(line)
        print("   A B C D E")

    def game_value(self, state):
        """Checks the current board status for a win condition

        Args:
        state (list of lists): either the current state of the game as saved in
            this TeekoPlayer object, or a generated successor state.

        Returns:
            int: 1 if this TeekoPlayer wins, -1 if the opponent wins, 0 if no winner

        """
        # check horizontal wins
        for row in state:
            for i in range(2):
                if row[i] != " " and row[i] == row[i + 1] == row[i + 2] == row[i + 3]:
                    return 1 if row[i] == self.my_piece else -1

        # check vertical wins
        for col in range(5):
            for i in range(2):
                if (
                    state[i][col] != " "
                    and state[i][col]
                    == state[i + 1][col]
                    == state[i + 2][col]
                    == state[i + 3][col]
                ):
                    return 1 if state[i][col] == self.my_piece else -1

        # check \ diagonal wins
        top_left = [[0, 0], [1, 0], [0, 1], [1, 1]]  # starting positions for \
        for idx in top_left:
            i = idx[0]
            j = idx[1]
            if (
                state[i][j] != " "
                and state[i][j]
                == state[i + 1][j + 1]
                == state[i + 2][j + 2]
                == state[i + 3][j + 3]
            ):
                return 1 if state[i][j] == self.my_piece else -1

        # check / diagonal wins
        top_right = [[0, 3], [0, 4], [1, 3], [1, 4]]  # starting positions for /
        for idx in top_right:
            i = idx[0]
            j = idx[1]
            if (
                state[i][j] != " "
                and state[i][j]
                == state[i + 1][j - 1]
                == state[i + 2][j - 2]
                == state[i + 3][j - 3]
            ):
                return 1 if state[i][j] == self.my_piece else -1

        # check box wins
        for i in range(4):
            for j in range(4):
                if (
                    state[i][j] != " "
                    and state[i][j]
                    == state[i][j + 1]
                    == state[i + 1][j]
                    == state[i + 1][j + 1]
                ):
                    return 1 if state[i][j] == self.my_piece else -1

        return 0  # no winner yet


############################################################################
#
# THE FOLLOWING CODE IS FOR SAMPLE GAMEPLAY ONLY
#
############################################################################
def main():
    print("Hello, this is Samaritan")
    ai = TeekoPlayer()
    piece_count = 0
    turn = 0

    # drop phase
    while piece_count < 8 and ai.game_value(ai.board) == 0:
        # get the player or AI's move
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(
                ai.my_piece
                + " moved at "
                + chr(move[0][1] + ord("A"))
                + str(move[0][0])
            )
        else:
            move_made = False
            ai.print_board()
            print(ai.opp + "'s turn")
            while not move_made:
                player_move = input("Move (e.g. B3): ")
                while player_move[0] not in "ABCDE" or player_move[1] not in "01234":
                    player_move = input("Move (e.g. B3): ")
                try:
                    ai.opponent_move(
                        [(int(player_move[1]), ord(player_move[0]) - ord("A"))]
                    )
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        piece_count += 1
        turn += 1
        turn %= 2

    # move phase - can't have a winner until all 8 pieces are on the board
    while ai.game_value(ai.board) == 0:
        if ai.my_piece == ai.pieces[turn]:
            ai.print_board()
            move = ai.make_move(ai.board)
            ai.place_piece(move, ai.my_piece)
            print(
                ai.my_piece
                + " moved from "
                + chr(move[1][1] + ord("A"))
                + str(move[1][0])
            )
            print("  to " + chr(move[0][1] + ord("A")) + str(move[0][0]))
        else:
            move_made = False
            ai.print_board()
            print(ai.opp + "'s turn")
            while not move_made:
                move_from = input("Move from (e.g. B3): ")
                while move_from[0] not in "ABCDE" or move_from[1] not in "01234":
                    move_from = input("Move from (e.g. B3): ")
                move_to = input("Move to (e.g. B3): ")
                while move_to[0] not in "ABCDE" or move_to[1] not in "01234":
                    move_to = input("Move to (e.g. B3): ")
                try:
                    ai.opponent_move(
                        [
                            (int(move_to[1]), ord(move_to[0]) - ord("A")),
                            (int(move_from[1]), ord(move_from[0]) - ord("A")),
                        ]
                    )
                    move_made = True
                except Exception as e:
                    print(e)

        # update the game variables
        turn += 1
        turn %= 2

    ai.print_board()
    if ai.game_value(ai.board) == 1:
        print("AI wins! Game over.")
    else:
        print("You win! Game over.")


if __name__ == "__main__":
    main()
