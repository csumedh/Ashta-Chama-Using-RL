import random

class StrategicPlayer:
    def __init__(self, player_id, start_positions, color, strategy="random"):
        """
        Initialize a player with a specific strategy.
        :param player_id: Unique ID for the player
        :param start_positions: List of starting positions for the pawns
        :param color: Color for the player pawns
        :param strategy: Strategy type ("aggressive", "defensive", "random")
        """
        self.player_id = player_id
        self.pawns = start_positions  # List of pawn positions
        self.color = color  # Player's color
        self.strategy = strategy  # Player's strategy

    def decide_move(self, possible_moves, board, safe_places):
        """
        Decide the move based on the strategy.
        :param possible_moves: List of possible moves (player_id, pawn_index, new_position, dice_number)
        :param board: Current board state
        :param safe_places: List of safe places on the board
        :return: Chosen move or None if no moves are possible
        """
        if not possible_moves:
            return None

        if self.strategy == "aggressive":
            return self._aggressive_move(possible_moves, board)
        elif self.strategy == "defensive":
            return self._defensive_move(possible_moves, safe_places)
        elif self.strategy == "random":
            return random.choice(possible_moves)

    def _aggressive_move(self, possible_moves, board):
        """
        Choose a move that prioritizes capturing opponent pawns.
        :param possible_moves: List of possible moves
        :param board: Current board state
        :return: Chosen move
        """
        for move in possible_moves:
            _, _, new_position, _ = move
            # Check if new_position has an opponent pawn
            for player in board.players:
                if player.player_id != self.player_id:
                    for pawn_position in player.pawns:
                        if pawn_position == new_position:
                            return move  # Prioritize capturing move
        # If no capturing move, return the first available move
        return possible_moves[0]

    def _defensive_move(self, possible_moves, safe_places):
        """
        Choose a move that keeps pawns in safe places.
        :param possible_moves: List of possible moves
        :param safe_places: List of safe places
        :return: Chosen move
        """
        for move in possible_moves:
            _, _, new_position, _ = move
            if new_position in safe_places:
                return move  # Prioritize moving to a safe place
        # If no safe place move, return the first available move
        return possible_moves[0]

    def update_position(self, pawn_index, new_position):
        """
        Update the position of a specific pawn.
        :param pawn_index: Index of the pawn to update
        :param new_position: New position of the pawn
        """
        self.pawns[pawn_index] = new_position
