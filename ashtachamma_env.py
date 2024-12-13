import gymnasium as gym
from gymnasium import spaces
import numpy as np
import pygame
from board_updated import Board
from feat_StrategicPlayers_updated import StrategicPlayer

class AshtachammaEnv(gym.Env):
    """
    Custom Gymnasium Environment for the game Ashtachamma.
    This environment allows reinforcement learning agents to interact with the game.
    """

    def __init__(self, render_mode=None):
        """
        Initialize the Ashtachamma environment.

        Parameters:
        - render_mode (str): The rendering mode. 'human' for visual rendering, or None for no rendering.
        """
        super(AshtachammaEnv, self).__init__()

        # Rendering setup
        self.render_mode = render_mode
        if render_mode == "human":
            pygame.init()  # Initialize pygame if rendering to a screen
            self.screen = None  # Screen will be initialized later when rendering starts

        # Initialize the game board
        self.board = Board()
        self.players = []  # List to hold players
        self.current_player_index = 0  # Index of the current player

        # Define starting positions, colors, and strategies for players
        start_positions = [
            [(0, 4), (1, 4)],
            [(4, 0), (4, 1)],
            [(8, 4), (7, 4)],
            [(4, 8), (4, 7)]
        ]
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Red, Green, Blue, Yellow
        strategies = ["RL", "random", "aggressive", "defensive"]  # RL, random, and heuristic strategies

        # Initialize players with their attributes
        for i in range(len(start_positions)):
            player = StrategicPlayer(player_id=i, start_positions=start_positions[i], color=colors[i],
                                     strategy=strategies[i])
            player.pawns = list(start_positions[i])  # Set initial pawn positions
            self.players.append(player)

        self.board.players = self.players  # Add players to the board

        # Define action and observation spaces for RL
        self.action_space = spaces.Discrete(2)  # RL agents can select one of two actions
        self.observation_space = spaces.Box(low=0, high=49, shape=(4, 50), dtype=np.int32)

    def reset(self, seed=None, options=None):
        """
        Reset the environment to its initial state.

        Parameters:
        - seed (int): Optional random seed.
        - options (dict): Additional reset options.

        Returns:
        - state (np.ndarray): The initial observation/state.
        - info (dict): Additional reset information.
        """
        super().reset(seed=seed)

        # Reinitialize the board and players
        self.board = Board()
        self.players = []

        # Reset starting positions, colors, and strategies
        start_positions = [
            [(0, 4), (1, 4)],
            [(4, 0), (4, 1)],
            [(8, 4), (7, 4)],
            [(4, 8), (4, 7)]
        ]
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        strategies = ["RL", "random", "defensive", "aggressive"]

        # Reinitialize players
        for i in range(len(start_positions)):
            player = StrategicPlayer(player_id=i, start_positions=start_positions[i], color=colors[i],
                                     strategy=strategies[i])
            player.pawns = list(start_positions[i])
            self.players.append(player)

        self.board.players = self.players
        self.current_player_index = 0

        return self._get_state(), {}

    def step(self, action):
        """
        Perform a step in the environment for the current player based on the action.

        Parameters:
        - action (int): The action selected by the agent.

        Returns:
        - state (np.ndarray): The updated observation/state.
        - reward (float): The reward for the action.
        - terminated (bool): Whether the episode is terminated.
        - truncated (bool): Whether the episode is truncated.
        - info (dict): Additional information.
        """
        current_player = self.players[self.current_player_index]  # Get the current player
        roll = self.board.diceRoll()  # Roll the dice

        reward = 0  # Initialize reward
        terminated = False
        truncated = False

        # Handle RL player's action
        if current_player.strategy == "RL":
            pawn_index = action  # Action corresponds to the pawn index

            # Validate pawn index
            if pawn_index is not None and pawn_index >= len(current_player.pawns):
                print(f"Invalid pawn index: {pawn_index} for Player {current_player.player_id}")
                self._next_player()
                return self._get_state(), -1, False, False, {}

            # Handle None pawns
            if current_player.pawns[pawn_index] is None:
                for i in range(len(current_player.pawns)):
                    if current_player.pawns[i] is not None:
                        pawn_index = i
                        break

            # Get the current pawn's position and move it
            current_position = current_player.pawns[pawn_index]
            new_position = self.board.move(current_player, pawn_index, roll)

            if new_position == current_position:
                # No valid move
                self._next_player()
                return self._get_state(), -0.1, False, False, {}

            # Update pawn's position and calculate rewards
            current_player.pawns[pawn_index] = new_position
            old_distance = abs(current_position[0] - 4) + abs(current_position[1] - 4)
            new_distance = abs(new_position[0] - 4) + abs(new_position[1] - 4)

            if new_distance < old_distance:
                reward += 1.5  # Progress reward

            if new_position == (4, 4):
                print(f"Player {current_player.player_id}'s pawn {pawn_index} reached home!")
                current_player.pawns[pawn_index] = None
                reward += 5  # Home reward
                current_player.score += 1

            if new_position in self.board.safe_places:
                reward += 1  # Safe zone reward

            for opponent in self.players:
                if opponent != current_player:
                    for opp_pawn in opponent.pawns:
                        if opp_pawn and abs(opp_pawn[0] - new_position[0]) + abs(opp_pawn[1] - new_position[1]) == 6:
                            reward -= 0.8  # Risk penalty

            if current_player.kill:
                reward += 2  # Kill reward

        else:
            # Handle non-RL players using strategies
            possible_moves = self.get_possible_moves(current_player, roll)
            if not possible_moves:
                self._next_player()
                return self._get_state(), 0, False, False, {}

            chosen_move = current_player.decide_move(possible_moves, self.players)
            _, _, pawn_index, new_position = chosen_move
            current_player.update_position(pawn_index, new_position)

        # Check for winning conditions
        win, winner = self.board.check_winner((current_player.player_id, False, pawn_index, new_position))
        if win:
            if current_player.strategy == "RL":
                reward += 10  # Winning reward for RL agent
            terminated = True

        self._next_player()
        return self._get_state(), reward, terminated, truncated, {}

    def _next_player(self):
        """
        Advance to the next player, skipping players with no active pawns.
        """
        if any(player.score == 2 for player in self.players):
            return

        self.current_player_index = (self.current_player_index + 1) % len(self.players)
        while all(pawn is None for pawn in self.players[self.current_player_index].pawns):
            self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def _get_state(self):
        """
        Generate the current state as an observation for RL.
        """
        state = np.full((4, 50), 49, dtype=np.int32)
        for i, player in enumerate(self.players):
            for j, pawn in enumerate(player.pawns):
                if pawn is not None:
                    state[i][j] = self.board.paths[i].index(pawn)
        return state

    def get_possible_moves(self, player, roll):
        """
        Get all valid moves for the given player and dice roll.
        """
        possible_moves = []
        for pawn_index, pawn in enumerate(player.pawns):
            if pawn is None:
                continue
            new_position = self.board.move(player, pawn_index, roll)
            if new_position != pawn:
                possible_moves.append((player.player_id, player.kill, pawn_index, new_position))
        return possible_moves

    def render(self):
        """
        Render the game based on the selected render mode.
        """
        if self.render_mode == "human":
            if not hasattr(self, "screen") or self.screen is None:
                screen_width = self.board.board_size * self.board.cell_size + 2 * self.board.padding
                screen_height = self.board.board_size * self.board.cell_size + 2 * self.board.padding
                self.screen = pygame.display.set_mode((screen_width, screen_height))
                pygame.display.set_caption("Ashtachamma RL Environment")

            self.screen.fill((255, 255, 255))
            self.board.render(self.screen)
            pygame.display.flip()

        elif self.render_mode == "rgb_array":
            screen_width = self.board.board_size * self.board.cell_size + 2 * self.board.padding
            screen_height = self.board.board_size * self.board.cell_size + 2 * self.board.padding
            surface = pygame.Surface((screen_width, screen_height))
            surface.fill((255, 255, 255))
            self.board.render(surface)
            return np.array(pygame.surfarray.array3d(surface))

        elif self.render_mode == "ansi":
            print("Rendering in ANSI mode is not yet implemented.")

        else:
            raise ValueError(f"Unsupported render_mode: {self.render_mode}")

    def close(self):
        """
        Clean up resources when the environment is closed.
        """
        if self.render_mode == "human" and hasattr(self, "screen"):
            pygame.quit()
            del self.screen
