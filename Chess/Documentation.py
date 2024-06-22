# Difference in 2 classes, why 2? fucntions of each class etc:

# Gamestate Class:
# The Gamestate class is responsible for managing the overall state of the chess game. It represents the board, the positions of the pieces, whose turn it is, and other game-related information. The functions in this class are meant to handle the high-level operations and rules of the game, such as:

# Initializing the board and setting up the game state (__init__)
# Making and undoing moves on the board (makeMove, undoMove)
# Generating and validating legal moves (getValidMoves, getAllPossibleMoves)
# Checking for special conditions like check, checkmate, and stalemate (inCheck, squareUnderAttack)
# Handling special move cases like en passant captures and pawn promotion

# The Gamestate class is essentially the core of the chess engine, responsible for managing the game logic and enforcing the rules of chess.


# Move Class:
# The Move class, on the other hand, is a separate entity that represents a single move in the game of chess. It encapsulates the details of a move, such as:

# The starting and ending squares of the move
# The piece being moved
# Any piece captured during the move
# Whether the move involves special cases like pawn promotion or en passant capture

# The Move class is designed to be a self-contained representation of a move, making it easier to work with moves as independent objects. The functions in this class are focused on:

# Initializing a move object with the necessary details (__init__)
# Comparing moves for equality (__eq__)
# Converting move representations between algebraic notation and coordinate form (getChessNotation, getRankFile)
#
# By separating the concerns of game state management and move representation, the code becomes more organized, modular, and easier to maintain. The Gamestate class can focus on the overall game logic, while the Move class encapsulates the details of individual moves. This separation of responsibilities follows the principles of object-oriented programming and promotes code reusability and extensibility.
# Additionally, having a separate Move class allows for easier implementation of move generation algorithms, move history tracking, and other move-related functionality without cluttering the Gamestate class with too many responsibilities.
# In summary, the Gamestate class is responsible for managing the overall game state and enforcing the rules of chess, while the Move class is a self-contained representation of a single move, making it easier to work with moves as independent objects. This separation of concerns promotes code organization, modularity, and adherence to object-oriented programming principles.






# Q) How the following are checked, verified and made to happen??

# Check:
# The inCheck function determines if the current player's king is in check.
# It calls the squareUnderAttack function with the king's location (either whiteKingLocation or blackKingLocation depending on whose turn it is).
# The squareUnderAttack function generates all possible moves for the opponent using getAllPossibleMoves.
# It then checks if any of the opponent's moves have the king's square as the end square, indicating that the king is under attack.


# Checkmate:
# In the getValidMoves function, after generating all valid moves for the current player, it checks if there are no valid moves left.
# If there are no valid moves and the current player is in check (self.inCheck() == True), it sets the checkMate flag to True.


# Stalemate:
# Similar to checkmate, in the getValidMoves function, if there are no valid moves left but the current player is not in check (self.inCheck() == False), it sets the staleMate flag to True.


# Pawn Promotion:
# In the __init__ method of the Move class, it checks if the move involves a pawn reaching the last rank (row 0 for white pawns or row 7 for black pawns).
# If that's the case, it sets the isPawnPromotion flag to True.
# In the makeMove function of the Gamestate class, it checks if move.isPawnPromotion is True, and if so, it updates the promoted pawn on the board to a queen of the same color.


# En passant:
# The enpassantPossible attribute in the Gamestate class keeps track of the square where an en passant capture is possible (if a pawn has moved two squares forward).
# In the makeMove function, if a pawn moves two squares forward, it updates the enpassantPossible attribute with the square where an en passant capture would be possible on the next move.
# In the __init__ method of the Move class, if the isEnPassantMove flag is set to True, it sets the pieceCaptured attribute to the captured pawn's color and type.
# In the makeMove and undoMove functions, it handles the en passant capture by removing or restoring the captured pawn on the board.