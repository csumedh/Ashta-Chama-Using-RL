import random
class StrategicPlayer:
    def __init__(self, player_id, start_positions, color, strategy="random"):
        self.player_id = player_id
        self.pawns = start_positions  # List of pawn positions
        self.color = color  # Player's color
        self.strategy = strategy  # Player's strategy

    def decide_move(self, possible_moves, board, safe_places):
        if not possible_moves:
            return None

        if self.strategy == "aggressive":
            print(f"Player {self.player_id} (Aggressive) choosing move...")
            return self._aggressive_move(possible_moves, board)
        elif self.strategy == "defensive":
            print(f"Player {self.player_id} (Defensive) choosing move...")
            return self._defensive_move(possible_moves, safe_places)
        elif self.strategy == "random":
            print(f"Player {self.player_id} (Random) choosing move...")
            return random.choice(possible_moves)

    def _aggressive_move(self, possible_moves, board):
        """Prioritize capturing opponent pawns."""
        for move in possible_moves:
            _, _, new_position, _ = move
            # Check if new_position has an opponent pawn to capture
            for player in board.players:
                if player.player_id != self.player_id:
                    for i, pawn_position in enumerate(player.pawns):
                        if pawn_position == new_position:
                            # If a pawn is found, capture it
                            print(f"Player {self.player_id} (Aggressive) capturing pawn at {new_position}")
                            return move  # Return this move to capture the opponent's pawn
        # If no capturing move, return the first available move
        return possible_moves[0]

    def _defensive_move(self, possible_moves, safe_places):
        """Prioritize safe places."""
        for move in possible_moves:
            _, _, new_position, _ = move
            if new_position in safe_places:
                return move  # Return move to a safe place
        # If no safe place move, return the first available move
        return possible_moves[0]

    def update_position(self, pawn_index, new_position):
        self.pawns[pawn_index] = new_position