import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from board_updated import Board
from feat_StrategicPlayers_updated import StrategicPlayer

class AshtachammaEnv(gym.Env):
    def __init__(self,render_mode=None):
        super(AshtachammaEnv, self).__init__()
        # Initialize Pygame if rendering to a screen
        self.render_mode = render_mode
        if render_mode == "human":
            pygame.init()
            self.screen = None  # Initialize later when rendering
        self.board = Board()
        self.players = []
        self.current_player_index = 0

        start_positions = [
            [(0, 4), (1, 4)],
            [(4, 0), (4, 1)],
            [(8, 4), (7, 4)],
            [(4, 8), (4, 7)]
        ]
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        strategies = ["RL", "random", "aggressive", "defensive"]

        for i in range(len(start_positions)):
            player = StrategicPlayer(player_id=i, start_positions=start_positions[i], color=colors[i],
                                     strategy=strategies[i])
            player.pawns = list(start_positions[i])
            self.players.append(player)

        self.board.players = self.players

        self.action_space = spaces.Discrete(2)
        self.observation_space = spaces.Box(low=0, high=49, shape=(4, 50), dtype=np.int32)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self.board = Board()
        self.players = []
        start_positions = [
            [(0, 4), (1, 4)],
            [(4, 0), (4, 1)],
            [(8, 4), (7, 4)],
            [(4, 8), (4, 7)]
        ]
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        strategies = ["RL", "random", "defensive", "aggressive"]

        for i in range(len(start_positions)):
            player = StrategicPlayer(player_id=i, start_positions=start_positions[i], color=colors[i],
                                     strategy=strategies[i])
            player.pawns = list(start_positions[i])
            self.players.append(player)

        self.board.players = self.players
        self.current_player_index = 0
        return self._get_state(), {}

    def step(self, action):
        print(f"Actions are: {action}")
        current_player = self.players[self.current_player_index]
        roll = self.board.diceRoll()

        reward = 0
        terminated = False
        truncated = False

        if current_player.strategy == "RL":
            pawn_index = action

            # Validate selected pawn
            if pawn_index >= len(current_player.pawns):
                print(f"Invalid pawn index: {pawn_index} for Player {current_player.player_id}")
                self._next_player()
                return self._get_state(), -1 if current_player.strategy == "RL" else 0, False, False, {}

            # Get the pawn's current position
            current_position = current_player.pawns[pawn_index]

            # Move the pawn
            new_position = self.board.move(current_player, pawn_index, roll)

            if new_position == current_position:
                # No move occurred (invalid roll or blocked move)
                self._next_player()
                return self._get_state(), -1, False, False, {}

            # Reward for moving closer to the home position
            old_distance = abs(current_position[0] - 4) + abs(current_position[1] - 4)
            new_distance = abs(new_position[0] - 4) + abs(new_position[1] - 4)
            if new_distance < old_distance:
                reward += 0.5  # Incremental progress reward

            # Update pawn's position
            current_player.pawns[pawn_index] = new_position

            # Check if the pawn reaches home
            if new_position == (4, 4):
                print(f"Player {current_player.player_id}'s pawn {pawn_index} reached home!")
                current_player.pawns[pawn_index] = None  # Remove the pawn
                reward += 5  # Large reward for reaching home

            # Check for safe zone entry
            if new_position in self.board.safe_places:
                reward += 1  # Reward for entering a safe zone

            # Check for risky moves (near opponent pawns)
            for opponent in self.players:
                if opponent != current_player:
                    for opp_pawn in opponent.pawns:
                        if opp_pawn and abs(opp_pawn[0] - new_position[0]) + abs(opp_pawn[1] - new_position[1]) == 1:
                            reward -= 1  # Penalize risky moves

            # Reward for killing an opponent's pawn
            if current_player.kill:
                reward += 1

            # Check for a winner
            if self.board.check_winner((current_player.player_id, False, pawn_index, new_position)):
                reward += 10  # Big reward for winning
                terminated = True
                print(f"Player {current_player.player_id} has won the game!")

        else:
            # Handle non-RL players
            possible_moves = self.get_possible_moves(current_player, roll)
            if not possible_moves:
                print(f"No valid moves for Player {current_player.player_id}. Skipping turn.")
                self._next_player()
                return self._get_state(), 0, terminated, truncated, {}
            chosen_move = current_player.decide_move(possible_moves, self.players)
            _, _, pawn_index, new_position = chosen_move
            current_player.update_position(pawn_index, new_position)
            print(f"Player {current_player.player_id} chose move {chosen_move}")

            # Check for winner
            if self.board.check_winner((current_player.player_id, False, pawn_index, new_position)):
                terminated = True
                print(f"Player {current_player.player_id} has won the game!")

        print(
            f"Player {current_player.player_id} pawn {pawn_index} moved to {new_position}. Reward: {reward}, terminated: {terminated}")

        self._next_player()
        return self._get_state(), reward, terminated, truncated, {}

    def _next_player(self):
        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        while all(pawn is None for pawn in self.players[self.current_player_index].pawns):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def _get_state(self):
        state = np.full((4, 50), 49, dtype=np.int32)  # Set default value as 49 (out of bounds)
        for i, player in enumerate(self.players):
            for j, pawn in enumerate(player.pawns):
                if pawn is not None:
                    state[i][j] = self.board.paths[i].index(pawn)  # Map the pawn position to the path index
        return state

    def get_possible_moves(self, player,roll):
        possible_moves = []
        for pawn_index, pawn in enumerate(player.pawns):
            if pawn is None:
                continue
            new_position = self.board.move(player, pawn_index, roll)
            if new_position != pawn:
                possible_moves.append((player.player_id, player.kill, pawn_index, new_position))
        return possible_moves

    def render(self):
        if self.render_mode == "human":
            if not hasattr(self, "screen") or self.screen is None:
                # Initialize the display for rendering
                screen_width = self.board.board_size * self.board.cell_size + 2 * self.board.padding
                screen_height = self.board.board_size * self.board.cell_size + 2 * self.board.padding
                self.screen = pygame.display.set_mode((screen_width, screen_height))
                pygame.display.set_caption("Ashtachamma RL Environment")

            self.screen.fill((255, 255, 255))  # White background
            self.board.render(self.screen)
            pygame.display.flip()

        elif self.render_mode == "rgb_array":
            # Return an RGB array of the current screen
            screen_width = self.board.board_size * self.board.cell_size + 2 * self.board.padding
            screen_height = self.board.board_size * self.board.cell_size + 2 * self.board.padding
            surface = pygame.Surface((screen_width, screen_height))
            surface.fill((255, 255, 255))
            self.board.render(surface)
            return np.array(pygame.surfarray.array3d(surface))

        elif self.render_mode == "ansi":
            # Return a text representation of the game (for debugging)
            print("Rendering in ANSI mode is not yet implemented.")

        else:
            raise ValueError(f"Unsupported render_mode: {self.render_mode}")

    def close(self):
        if self.render_mode == "human" and hasattr(self, "screen"):
            pygame.quit()
            del self.screen