# This file is responsible for storing all the information about the
# current state of the game. It will also be responsible for the valid moves at the
# current state. It will also keep a move log.

class GameState():
    def __init__(self):
        # 8x8 board, each element has 2 characters,
        # the 1st small one tell abt colour and 2nd capital letter for type of piece,
        # "--" means blank spaces
        self.board = [
            ["bR", "bN", "bB", "bQ", "bK", "bB", "bN", "bR"],
            ["bp", "bp", "bp", "bp", "bp", "bp", "bp", "bp"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["--", "--", "--", "--", "--", "--", "--", "--"],
            ["wp", "wp", "wp", "wp", "wp", "wp", "wp", "wp"],
            ["wR", "wN", "wB", "wQ", "wK", "wB", "wN", "wR"]
        ]
        self.moveFunctions = {'p': self.getPawnMoves, 'R': self.getRookMoves, 'N': self.getKnightMoves, 'B': self.getBishopMoves, 'K': self.getKingMoves, 'Q': self.getQueenMoves}
        self.whiteToMove = True
        self.moveLog = []
        self.whiteKingLocation = (7, 4)
        self.blackKingLocation = (0, 4)
        self.checkMate = False
        self.staleMate = False
        self.enpassantPossible = () # coordinates for the square where en passant capture is possible
        self.currentCastlingRight = CastleRights(True, True, True, True)
        self.castleRightsLog = [CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                             self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)]




    # Takes a move as a parameter and executes it (would not work for castling, pawn-promotion, and en-passant)
    def makeMove(self, move):
        self.board[move.startRow][move.startCol] = "--"
        self.board[move.endRow][move.endCol] = move.pieceMoved
        self.moveLog.append(move)  # log the move so we can undo or display the history of moves
        if move.pieceMoved == "wK":
            self.whiteKingLocation = (move.endRow, move.endCol)
        elif move.pieceMoved == "bK":
            self.blackKingLocation = (move.endRow, move.endCol)
        self.whiteToMove = not self.whiteToMove  # swap players

        # pawn promotion
        # if move.isPawnPromotion:
        #     self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"

        if move.isPawnPromotion:
            self.board[move.endRow][move.endCol] = move.pieceMoved[0] + "Q"
        # enpassant move
        if move.isEnpassantMove:
            self.board[move.startRow][move.endCol] = "--"

        # update enpassantPossible variable
        if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
            self.enpassantPossible = ((move.startRow + move.endRow)//2, move.startCol)
        else:
            self.enpassantPossible = ()

        # castle move
        if move.isCastleMove:
            if move.endCol - move.startCol == 2:  # kingside castle
                self.board[move.endRow][move.endCol-1] = self.board[move.endRow][move.endCol+1]  # copies the rook
                self.board[move.endRow][move.endCol+1] = '--'  # erase old rock
            else:  # queen side castle
                self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-2]  # copies the rook
                self.board[move.endRow][move.endCol-2] = '--'

        # update castling rights
        self.updateCastleRights(move)
        self.castleRightsLog.append(CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks, self.currentCastlingRight.wqs, self.currentCastlingRight.bqs))


    # Undo the last move

    def undoMove(self):
        if len(self.moveLog) != 0:  # Make sure that there is a move to undo
            move = self.moveLog.pop()
            self.board[move.startRow][move.startCol] = move.pieceMoved
            self.board[move.endRow][move.endCol] = move.pieceCaptured
            self.whiteToMove = not self.whiteToMove
            if move.pieceMoved == "wK":
                self.whiteKingLocation = (move.startRow, move.startCol)
            elif move.pieceMoved == "bK":
                self.blackKingLocation = (move.startRow, move.startCol)
            # undo the enpassant move
            if move.isEnpassantMove:
                self.board[move.endRow][move.endCol] = '--'
                self.board[move.startRow][move.endCol] = move.pieceCaptured
                self.enpassantPossible = (move.endRow, move.endCol)
            # undo a 2 square pawn advance
            if move.pieceMoved[1] == 'p' and abs(move.startRow - move.endRow) == 2:
                self.enpassantPossible = ()
            # undo castling rights
            self.castleRightsLog.pop()  # get rid of the new castle rights of the move we are undoing
            self.currentCastlingRight = self.castleRightsLog[-1] # set the current castle rights to the last one in the list
            # undo castle move
            if move.isCastleMove:
                if move.endCol - move.startCol == 2:
                    self.board[move.endRow][move.endCol+1] = self.board[move.endRow][move.endCol-1]
                    self.board[move.endRow][move.endCol-1] = '--'
                else:
                    self.board[move.endRow][move.endCol - 2] = self.board[move.endRow][move.endCol + 1]
                    self.board[move.endRow][move.endCol + 1] = '--'

            self.checkMate = False
            self.staleMate = False

    # All moves considering checks

    def getValidMoves(self):
        tempEnpassantPossible = self.enpassantPossible
        tempCastlingRights = CastleRights(self.currentCastlingRight.wks, self.currentCastlingRight.bks,
                                          self.currentCastlingRight.wqs, self.currentCastlingRight.bqs)
        #1) generate all possible moves
        moves = self.getAllPossibleMoves()
        if self.whiteToMove:
            self.getCastleMoves(self.whiteKingLocation[0], self.whiteKingLocation[1], moves)
        else:
            self.getCastleMoves(self.blackKingLocation[0], self.blackKingLocation[1], moves)
        #2) for each move, make the move
        for i in range(len(moves) - 1 , -1, -1): # when removing from a list, go backwards through that list
            self.makeMove(moves[i])
            #3) generate all opponent's moves
            #4) for each of your opponent's moves, see if they attack your king
            self.whiteToMove = not self.whiteToMove
            if self.inCheck():
                moves.remove(moves[i])  #5) if they do attack your king, not a valid move
            self.whiteToMove = not self.whiteToMove
            self.undoMove()
        if len(moves) == 0:
            if self.inCheck():
                self.checkMate = True
            else:
                self.staleMate = True
        else:
            self.checkMate = False
            self.staleMate = False



        self.enpassantPossible = tempEnpassantPossible
        self.currentCastlingRight = tempCastlingRights

        return moves



    # Determine if the current player is in check

    def inCheck(self):
        if self.whiteToMove:
            return self.squareUnderAttack(self.whiteKingLocation[0], self.whiteKingLocation[1])
        else:
            return self.squareUnderAttack(self.blackKingLocation[0], self.blackKingLocation[1])




    # Determine if the enemy can attack the square r, c
    def squareUnderAttack(self, r, c):
        self.whiteToMove = not self.whiteToMove # switch to opponent's move
        oppMoves = self.getAllPossibleMoves()
        for move in oppMoves:
            if move.endRow == r and move.endCol == c: # square is under attack
                self.whiteToMove = not self.whiteToMove  # switch turns back
                return True
        self.whiteToMove = not self.whiteToMove  # switch turns back
        return False


    # All moves w/o considering checks

    def getAllPossibleMoves(self):
        moves = []
        for r in range(len(self.board)):
            for c in range(len(self.board[r])):
                turn = self.board[r][c][0]
                if (turn == 'w' and self.whiteToMove) or (turn == 'b' and not self.whiteToMove):
                    piece = self.board[r][c][1]
                    # if piece == 'p':
                    #     self.getPawnMoves(r, c, moves)
                    self.moveFunctions[piece](r, c, moves)  # calls the appropriate move function based on piece type
        return moves

    # Update the castle rights given the move

    def updateCastleRights(self, move):

        if move.pieceCaptured == "wR":
            if move.endRow == 7:
                if move.endCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.endCol == 7:  # right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceCaptured == "bR":
            if move.endRow == 0:
                if move.endCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.endCol == 7:  # right rook
                    self.currentCastlingRight.bks = False

        if move.pieceMoved == 'wK':
            self.currentCastlingRight.wks = False
            self.currentCastlingRight.wqs = False
        elif move.pieceMoved == 'bK':
            self.currentCastlingRight.bks = False
            self.currentCastlingRight.bqs = False
        elif move.pieceMoved == 'wR':
            if move.startRow == 7:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.wqs = False
                elif move.startCol == 7:  #right rook
                    self.currentCastlingRight.wks = False
        elif move.pieceMoved == 'bR':
            if move.startRow == 0:
                if move.startCol == 0:  # left rook
                    self.currentCastlingRight.bqs = False
                elif move.startCol == 7:  #right rook
                    self.currentCastlingRight.bks = False







    # Get all the pawn moves for the pawn located at row, col and add these moves to the list
    def getPawnMoves(self, r, c, moves):
        if self.whiteToMove:
            if self.board[r-1][c] == "--": # 1 block ahead is empty
                moves.append(Move((r,c),(r-1,c), self.board))
                if r == 6 and self.board[r-2][c] == "--":  # 2 blocks ahead is empty
                    moves.append(Move((r, c), (r - 2, c), self.board))
            if c-1 >= 0:
                if self.board[r-1][c-1][0] == "b":  # Enemy piece to capture
                    moves.append(Move((r, c), (r-1, c-1), self.board))
                elif (r-1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c - 1), self.board, isEnPassantMove=True))
            if c+1 <= 7:
                if self.board[r-1][c+1][0] == "b":  # Enemy piece to capture
                    moves.append(Move((r, c), (r-1, c+1), self.board))
                elif (r-1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r - 1, c + 1), self.board, isEnPassantMove=True))

        else:
            if self.board[r+1][c] == "--": # 1 block ahead is empty
                moves.append(Move((r,c),(r+1,c), self.board))
                if r == 1 and self.board[r+2][c] == "--":  # 2 blocks ahead is empty
                    moves.append(Move((r, c), (r + 2, c), self.board))
            if c-1 >= 0:
                if self.board[r+1][c-1][0] == "w":  # Enemy piece to capture
                    moves.append(Move((r, c), (r+1, c-1), self.board))
                elif (r+1, c-1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c - 1), self.board, isEnPassantMove=True))
            if c+1 <= 7:
                if self.board[r+1][c+1][0] == "w":  # Enemy piece to capture
                    moves.append(Move((r, c), (r+1, c+1), self.board))
                elif (r+1, c+1) == self.enpassantPossible:
                    moves.append(Move((r, c), (r + 1, c + 1), self.board, isEnPassantMove=True))

    # Get all the Rook moves for the rook located at row, col and add these moves tot he list
    def getRookMoves(self, r, c, moves):
        directions = ((-1,0),(0,-1),(1,0),(0,1))  #up, left, down, right
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--": # empty space valid
                        moves.append(Move((r, c),(endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break # friendly piece invalid
                else:  # off board
                    break

    def getKnightMoves(self, r, c, moves):
        knightMoves = ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for m in knightMoves:
            endRow = r + m[0]
            endCol = c + m[1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor: # either empty or enemy
                    moves.append(Move((r, c), (endRow, endCol), self.board))
    def getBishopMoves(self, r, c, moves):
        directions = ((-1, -1), (-1, 1), (1, -1), (1, 1))  # all 4 diagonals
        enemyColor = "b" if self.whiteToMove else "w"
        for d in directions:
            for i in range(1, 8):
                endRow = r + d[0] * i
                endCol = c + d[1] * i
                if 0 <= endRow < 8 and 0 <= endCol < 8:
                    endPiece = self.board[endRow][endCol]
                    if endPiece == "--":  # empty space valid
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                    elif endPiece[0] == enemyColor:
                        moves.append(Move((r, c), (endRow, endCol), self.board))
                        break
                    else:
                        break  # friendly piece invalid
                else:  # off board
                    break

    def getQueenMoves(self, r, c, moves):
        self.getRookMoves(r, c, moves)
        self.getBishopMoves(r, c, moves)

    def getKingMoves(self, r, c, moves):
        kingMoves = ((-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1))
        allyColor = "w" if self.whiteToMove else "b"
        for i in range(8):
            endRow = r + kingMoves[i][0]
            endCol = c + kingMoves[i][1]
            if 0 <= endRow < 8 and 0 <= endCol < 8:
                endPiece = self.board[endRow][endCol]
                if endPiece[0] != allyColor:
                   moves.append(Move((r, c), (endRow, endCol), self.board))


    # Generate all valid castle moves for the king at (r,c)

    def getCastleMoves(self, r, c, moves):
        if self.squareUnderAttack(r,c):
            return
        if (self.whiteToMove and self.currentCastlingRight.wks) or (not self.whiteToMove and self.currentCastlingRight.bks):
            self.getKingsideCastleMoves(r, c, moves)
        if (self.whiteToMove and self.currentCastlingRight.wqs) or (not self.whiteToMove and self.currentCastlingRight.bqs):
            self.getQueensideCastleMoves(r, c, moves)

    def getKingsideCastleMoves(self,r,c,moves):
        if self.board[r][c+1] == '--' and self.board[r][c+2] == '--':
            if not self.squareUnderAttack(r, c+1) and not self.squareUnderAttack(r, c+2):
                moves.append(Move((r,c), (r, c+2), self.board, isCastleMove=True))
    def getQueensideCastleMoves(self, r, c, moves):
        if self.board[r][c-1] == '--' and self.board[r][c-2] == '--' and self.board[r][c-3] == '--':
            if not self.squareUnderAttack(r, c-1) and not self.squareUnderAttack(r, c-2):
                moves.append(Move((r,c), (r, c-2), self.board, isCastleMove=True))


class CastleRights():
    def __init__(self, wks, bks, wqs, bqs):
        self.wks = wks
        self.bks = bks
        self.wqs = wqs
        self.bqs = bqs




class Move():
    # maps keys to values
    # key : value
    rankToRows = {"1":7, "2":6, "3":5, "4":4,
                  "5":3, "6":2, "7":1, "8":0}
    rowsToRanks = {v: k for k, v in rankToRows.items()}
    filesToCols = {"a":0, "b":1, "c":2, "d":3,
                   "e":4, "f":5, "g":6, "h":7}
    colsToFiles = {v: k for k, v in filesToCols.items()}

    def __init__(self, startSq, endSq, board, isEnPassantMove = False, isCastleMove=False):
        self.startRow = startSq[0]
        self.startCol = startSq[1]
        self.endRow = endSq[0]
        self.endCol = endSq[1]
        self.pieceMoved = board[self.startRow][self.startCol]
        self.pieceCaptured = board[self.endRow][self.endCol]

        # pawn promotion
        self.isPawnPromotion = False
        if (self.pieceMoved == 'wp' and self.endRow == 0) or (self.pieceMoved == 'bp' and self.endRow == 7) :
            self.isPawnPromotion = True

        # enpassant
        # self.isEnpassantMove = False
        # if self.pieceMoved[1] == 'p' and (self.endRow, self.endCol) == enpassantPossible:
        #     self.isEnpassantMove = True
        self.isEnpassantMove = isEnPassantMove
        if self.isEnpassantMove:
            self.pieceCaptured = 'wp' if self.pieceMoved == 'bp' else 'bp '

       # castling
        self.isCastleMove = isCastleMove



        self.moveID = self.startRow * 1000 + self.startCol * 100 + self.endRow * 10 + self.endCol



    # Overriding the equals method

    def __eq__(self, other):
        if isinstance(other, Move):
            return self.moveID == other.moveID
        return False



    def getChessNotation(self):
        return self.getRankFile(self.startRow, self.startCol) + self.getRankFile(self.endRow, self.endCol)


    def getRankFile(self, r, c):
        return self.colsToFiles[c] + self.rowsToRanks[r]





