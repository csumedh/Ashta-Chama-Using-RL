import random

class StrategicPlayer:
    def __init__(self, player_id, start_positions, color, strategy="random"):
        self.player_id = player_id
        self.pawns = start_positions  # List of pawn positions
        self.color = color  # Player's color
        self.strategy = strategy  # Player's strategy
        self.kill = None
        self.score = 1

    def decide_move(self, possible_moves, players):
        # Choose the move based on the player's strategy
        if self.strategy == "aggressive":
            print(f"Player {self.player_id} (Aggressive) choosing move...")
            return self._aggressive_move(possible_moves, players)
        elif self.strategy == "defensive":
            print(f"Player {self.player_id} (Defensive) choosing move...")
            return self._defensive_move(possible_moves,players)
        elif self.strategy == "random":
            print(f"Player {self.player_id} (Random) choosing move...")
            return random.choice(possible_moves)

    def _aggressive_move(self, possible_moves, players):
        # Sort possible moves based on capturing opportunity (i.e., moving to an opponent's pawn)
        capture_moves = []
        safe_moves = []

        for move in possible_moves:
            # Check if the move captures an opponent's pawn
            if self.isKill(move):
                capture_moves.append(move)
            else:
                safe_moves.append(move)

        # Prioritize capture moves, if any
        if capture_moves:
            print(f"The player has killed the pawn at  {capture_moves[0][3]}")
            return capture_moves[0]  # Prioritize the first capture move
        elif safe_moves:
            print(f"The player has chosen the safe move at {safe_moves[0][3]}")
            return safe_moves[0]
        else:
            print(f"The player has chosen the best of the possible move, moving to {possible_moves[0][3]}")
            return possible_moves[0]  # Default to any move

    def isKill(self, move):
        _,kill,_,_ = move
        if kill:
            return True
    def is_opponent_pawn(self, position, players):
        # Check if the position has an opponent's pawn
        for player in players:
            if player.player_id != self.player_id:  # Skip own player
                if position in player.pawns:  # Check if the position belongs to an opponent
                    return True
        return False

    def _defensive_move(self, possible_moves,players):
        # For defensive move, prioritize safe moves
        safe_moves = []
        for move in possible_moves:
            if self.is_safe_position(move,players):
                safe_moves.append(move)

        if safe_moves:
            print(f"The player has chosen the safest move possible, moving to {safe_moves[0][3]}")
            return safe_moves[0]
        else:
            print(f"The player has chosen the best of the possible move, moving to {possible_moves[0][3]}")
            return possible_moves[0]  # Default to any move

    def is_safe_position(self, position,players):
        # You can define a safe position based on distance from opponent pawns
        surrounding_positions = self.get_surrounding_positions(position)
        for pos in surrounding_positions:
            if self.is_opponent_pawn(pos,players):
                return False  # If any surrounding position is an opponent's pawn, it's not safe
        return True

    def get_surrounding_positions(self, position):
        # Assuming position is a tuple (x, y)
        _,_,_,(x,y) = position
        surrounding_positions = [
            (x + 1, y),  # move right
            (x - 1, y),  # move left
            (x, y + 1),  # move down
            (x, y - 1)  # move up
        ]
        return surrounding_positions

    def update_position(self, pawn_index, new_position):
        self.pawns[pawn_index] = new_position
