import random


class StrategicPlayer:
    def __init__(self, player_id, start_positions, color, strategy="random"):
        """
        Initialize the StrategicPlayer object.

        Args:
        - player_id: Unique identifier for the player.
        - start_positions: List of starting positions for the player's pawns.
        - color: The player's color.
        - strategy: The player's strategy ("random", "aggressive", "defensive", or "RL").
        """
        self.player_id = player_id
        self.pawns = start_positions  # List storing the positions of the player's pawns
        self.color = color  # Player's color
        self.strategy = strategy  # Strategy used to decide moves
        self.kill = None  # Tracks if the player captured an opponent's pawn (for aggressive strategy)
        self.score = 0  # Player's score, can be incremented based on game rules

    def decide_move(self, possible_moves, players):
        """
        Decide the player's move based on the chosen strategy.

        Args:
        - possible_moves: A list of all possible moves for the player.
        - players: A list of all players in the game.

        Returns:
        - A chosen move from possible_moves.
        """
        if self.strategy == "aggressive":
            print(f"Player {self.player_id} (Aggressive) choosing move...")
            return self._aggressive_move(possible_moves, players)
        elif self.strategy == "defensive":
            print(f"Player {self.player_id} (Defensive) choosing move...")
            return self._defensive_move(possible_moves, players)
        elif self.strategy == "random":
            print(f"Player {self.player_id} (Random) choosing move...")
            return random.choice(possible_moves)  # Pick a random move
        elif self.strategy == "RL":
            # Placeholder for RL-based decision-making
            print(f"Player {self.player_id} (RL): Move to be decided externally.")
            return None  # RL logic is handled externally
        else:
            print(f"Player {self.player_id}: Unknown strategy, choosing random move.")
            return random.choice(possible_moves)

    def _aggressive_move(self, possible_moves, players):
        """
        Implement aggressive strategy: prioritize capturing opponent pawns.

        Args:
        - possible_moves: A list of possible moves.
        - players: A list of all players in the game.

        Returns:
        - The chosen move based on aggressive strategy.
        """
        capture_moves = []  # Moves that can capture opponent pawns
        safe_moves = []  # Moves that don't result in capture

        for move in possible_moves:
            if self.isKill(move):  # Check if the move captures an opponent's pawn
                capture_moves.append(move)
            else:
                safe_moves.append(move)

        if capture_moves:  # If there are capture moves, prioritize them
            if capture_moves[0][3] == (4, 4):  # Check if move leads to a "winning" position
                print("Pawn at win place, will be removed now!")
                return capture_moves[0]
            else:
                print(f"The player has killed the pawn at {capture_moves[0][3]}")
                return capture_moves[0]
        elif safe_moves:  # Choose a safe move if no capture moves
            if safe_moves[0][3] == (4, 4):
                print("Pawn at win place, will be removed now!")
                return safe_moves[0]
            else:
                print(f"The player has chosen the safe move at {safe_moves[0][3]}")
                return safe_moves[0]
        else:
            print(f"The player has chosen the best of the possible moves, moving to {possible_moves[0][3]}")
            return possible_moves[0]  # Default to the first move

    def isKill(self, move):
        """
        Check if a move results in capturing an opponent's pawn.

        Args:
        - move: A move tuple.

        Returns:
        - True if the move captures an opponent's pawn, False otherwise.
        """
        _, kill, _, _ = move
        return bool(kill)  # Return True if the move kills an opponent's pawn

    def is_opponent_pawn(self, position, players):
        """
        Check if a given position has an opponent's pawn.

        Args:
        - position: The position to check.
        - players: A list of all players in the game.

        Returns:
        - True if the position contains an opponent's pawn, False otherwise.
        """
        for player in players:
            if player.player_id != self.player_id:  # Ignore the player's own pawns
                if position in player.pawns:
                    return True  # Position belongs to an opponent
        return False

    def _defensive_move(self, possible_moves, players):
        """
        Implement defensive strategy: prioritize avoiding dangerous positions.

        Args:
        - possible_moves: A list of possible moves.
        - players: A list of all players in the game.

        Returns:
        - The chosen move based on defensive strategy.
        """
        safe_moves = []

        for move in possible_moves:
            if move[3] == (4, 4):  # Check if move leads to a "winning" position
                print("Pawn at win place, will be removed now!")
                return move
            elif self.is_safe_position(move, players):  # Check if move is safe
                safe_moves.append(move)

        if safe_moves:  # Choose a safe move if available
            print(f"The player has chosen the safest move possible, moving to {safe_moves[0][3]}")
            return safe_moves[0]
        else:
            print(f"The player has chosen the best of the possible moves, moving to {possible_moves[0][3]}")
            return possible_moves[0]  # Default to the first move

    def is_safe_position(self, position, players):
        """
        Determine if a position is safe (not surrounded by opponents).

        Args:
        - position: The position to evaluate.
        - players: A list of all players in the game.

        Returns:
        - True if the position is safe, False otherwise.
        """
        surrounding_positions = self.get_surrounding_positions(position)
        for pos in surrounding_positions:
            if self.is_opponent_pawn(pos, players):
                return False  # Not safe if any surrounding position is an opponent's pawn
        return True

    def get_surrounding_positions(self, position):
        """
        Get all positions surrounding the given position.

        Args:
        - position: The current position as a tuple (x, y).

        Returns:
        - A list of surrounding positions.
        """
        _, _, _, (x, y) = position
        return [
            (x + 1, y),  # Right
            (x - 1, y),  # Left
            (x, y + 1),  # Down
            (x, y - 1)  # Up
        ]

    def update_position(self, pawn_index, new_position):
        """
        Update the position of a pawn.

        Args:
        - pawn_index: The index of the pawn to update.
        - new_position: The new position of the pawn.
        """
        self.pawns[pawn_index] = new_position  # Update the pawn's position
