# import pygame
import random

class Board:
    def __init__(self):
        self.board_size = 9  # 9x9 board
        self.safe_places = [(1, 4), (2, 2), (2, 6), (4, 1), (4, 4), (4, 7), (6, 2), (6, 6), (7, 4)]
        self.home_places = [(0, 4), (4, 0), (8, 4), (4, 8)]
        # self.board_state = [[None for _ in range(self.board_size)] for _ in range(self.board_size)]
        self.players = []  # List of Player objects
        self.current_player_index = 0
        self.cell_size = 60
        self.padding = 20
        self.paths = [[(0,4), (1,4), (1,3), (1,2), (1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7), (6,7), (5,7), (4,7), (3,7), (2,7), (1,7), (1,6), (1,5), 
          (2,6), (3,6), (4,6), (5,6), (6,6), (6,5), (6,4), (6,3), (6,2), (5,2), (4,2), (3,2), (2,2), (2,3), (2,4), (2,5),  (3,5), (4,5), (5,5), (5,4), (5,3), (4,3), (3,3),(3,4), (4,4)],
		
		 [(4,0), (4,1), (5,1), (6,1), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7), (6,7), (5,7), (4,7), (3,7), (2,7), (1,7), (1,6), (1,5), (1,4), (1,3), (1,2), (1,1), (2,1), (3,1), 
		  (2,2), (2,3), (2,4), (2,5), (2,6), (3,6), (4,6), (5,6), (6,6), (6,5), (6,4), (6,3), (6,2), (5,2), (4,2), (3,2), (3,3),(3,4), (3,5), (4,5), (5,5), (5,4), (5,3), (4,3), (4,4)],

		 [(8,4), (7,4), (7,5), (7,6), (7,7), (6,7), (5,7), (4,7), (3,7), (2,7), (1,7), (1,6), (1,5), (1,4), (1,3), (1,2), (1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (7,1), (7,2), (7,3), 
          (6,2), (5,2), (4,2), (3,2), (2,2), (2,3), (2,4), (2,5), (2,6), (3,6), (4,6), (5,6), (6,6), (6,5), (6,4), (6,3), (5,3), (4,3),(3,3),(3,4), (3,5), (4,5), (5,5), (5,4), (4,4)],
			
		 [(4,8), (4,7), (3,7), (2,7), (1,7), (1,6), (1,5), (1,4), (1,3), (1,2), (1,1), (2,1), (3,1), (4,1), (5,1), (6,1), (7,1), (7,2), (7,3), (7,4), (7,5), (7,6), (7,7), (6,7), (5,7),
          (6,6), (6,5), (6,4), (6,3), (6,2), (5,2), (4,2), (3,2), (2,2), (2,3), (2,4), (2,5), (2,6), (3,6), (4,6), (5,6), (5,5), (5,4), (5,3), (4,3), (3,3),(3,4), (3,5), (4,5), (4,4)] 
		]
        # pygame.init()
        # self.screen = pygame.display.set_mode((self.board_size * self.cell_size + 2 * self.padding,
                                            #    self.board_size * self.cell_size + 2 * self.padding))
        # pygame.display.set_caption("Ashta Chamma")

    def add_player(self, player):
        """
        Add a player to the game.
        :param player: Player object
        """
        self.players.append(player)

    def diceRoll(self):
        """
        Simulate a dice roll with weighted probabilities.
        Possible outcomes are 1, 2, 3, 4, and 8.
        :return: The number rolled on the dice.
        """
        possibleNumbers = [1, 2, 3, 4, 8]
        number = random.choices(population=possibleNumbers, k=1)[0]
        return number
    def _next_player(self):
        """
        Switch to the next player's turn.
        """
        self.current_player_index = (self.current_player_index + 1) % len(self.players)

    def move(self, player_id):
        """
        Perform a move for the given player using the dice roll.
        Handles movement based on the player's strategy and updates the board state.
        :param player_id: The ID of the player whose turn it is.
        :return: List of possible moves.
        """
        dice_number = self.diceRoll()
        player = self.players[player_id]
        possible_path = self.paths[player_id]
        possible_moves = []

        # Generate possible moves based on dice roll
        for pawn_index, pawn_position in enumerate(player.pawns):
            if pawn_position is None:
                continue  # Skip if the pawn is inactive
            # print(pawn_position)
            current_position = possible_path.index(pawn_position)
            new_position_index = current_position + dice_number

            if new_position_index < len(possible_path):
                new_position = possible_path[new_position_index]

                # Check if the new position is occupied by a pawn of the same player
                if new_position in player.pawns:
                    continue  # Skip this move as the position is occupied by the player's own pawn

                # Check if the move results in a kill
                kill = self._check_kill(player_id, new_position)

                # Add the move to possible moves
                possible_moves.append((player_id, pawn_index, new_position, dice_number, kill))

        return possible_moves



    def _check_kill(self, player_id, position):
        """
        Check if the move captures an opponent's pawn.
        :param player_id: The ID of the player making the move.
        :param position: The target position of the move.
        :return: Information about the captured pawn, if any.
        """
        if position in self.safe_places:
            return None  # No kills possible in safe places

        for opponent in self.players:
            if opponent.player_id != player_id:
                for pawn_index, pawn_position in enumerate(opponent.pawns):
                    if pawn_position == position:
                        return (player_id, opponent.player_id, pawn_index)
        return None

            
    def kill_check(self, best_move):
        """
        Check if the move captures an opponent's pawn.
        :param best_move: The move being considered.
        :return: Information about the captured pawn, if any.
        """
        player_id = best_move[0]
        pawn_id = best_move[1]
        position = best_move[2]
        kill = []
        if position not in self.safe_places:
            for player in self.players:
                if player.player_id != player_id:
                    for pawn_index, pawn in enumerate(player.pawns):
                        if position == pawn:
                            kill.append((player_id, player.player_id, pawn_index))
                     

    def update(self, best_move, kill):
        """
        Update the board state with the new pawn position and handle captures.
        :param best_move: The move to update the board with.
        :param kill: Information about the captured pawn, if any.
        """
        self.players[best_move[0]].pawns[best_move[1]] = best_move[2]
        if kill != None and len(kill) != 0:
            self.players[kill[1]].pawns[kill[2]] = self.paths[kill[1]][0]
    
    def get_winner(self):
        """
        Determine if there's a winner.
        A winner is identified when all pawns of a player reach the goal state.
        :return: Player ID of the winner or None if no winner yet.
        """
        for player in self.players:
            # Check if all pawns of the player are in the goal position
            if all(pawn == self.paths[player.player_id][-1] for pawn in player.pawns):
                return player.player_id
        return None
    
    def is_game_over(self):
        """
        Check if the game is over.
        A game is over if any player has all their pawns in the goal position.
        :return: True if the game is over, False otherwise.
        """
        for player in self.players:
            # Check if all pawns of a player are in the last position of their path
            if all(pawn == self.paths[player.player_id][-1] for pawn in player.pawns):
                return True
        return False
    
    def reset(self):
        """
        Reset the board to its initial state.
        All pawns are returned to their respective starting positions in their paths,
        and the game state is cleared.
        """
        for player in self.players:
            player.pawns = [
                self.paths[player.player_id][0]  # Set each pawn to the starting position of the player's path
                for _ in range(len(player.pawns))
            ]
        self.current_player_index = 0
    def get_state(self):
        """
        Generate the current state of the board as a 2D array.
        :return: A 2D list (9x9) representing the board state.
        """
        state = [[0 for _ in range(self.board_size)] for _ in range(self.board_size)]

        for player in self.players:
            for pawn in player.pawns:
                if pawn:  # Check if the pawn has a valid position
                    x, y = pawn
                    state[x][y] = player.player_id + 1  # Use player ID + 1 to distinguish players

        return state
        
    # def render(self):
    #     """
    #     Render the board and the current positions of all pawns.
    #     """
    #     self.screen.fill((0, 0, 0))  # Fill the background with black

    #     # Draw the board
    #     for i in range(self.board_size):
    #         for j in range(self.board_size):
    #             rect = pygame.Rect(
    #                 self.padding + j * self.cell_size,
    #                 self.padding + i * self.cell_size,
    #                 self.cell_size,
    #                 self.cell_size
    #             )

    #             # Check if the cell is a safe place
    #             if (i, j) in self.safe_places:
    #                 pygame.draw.rect(self.screen, (240, 207, 174), rect)
    #                 cross = pygame.image.load("assets/icons/cross.png")
    #                 cross = pygame.transform.scale(cross, (53, 53))
    #             # Check if the cell is a home place
    #             elif (i, j) in self.home_places:
    #                 home_color_index = self.home_places.index((i, j))
    #                 home_colors = [(255, 255, 255), (200, 200, 200), (180, 180, 180), (220, 220, 220)]
    #                 pygame.draw.rect(self.screen, home_colors[home_color_index], rect)
    #             else:
    #                 pygame.draw.rect(self.screen, (240, 207, 174), rect)

    #             pygame.draw.rect(self.screen, (255, 255, 255), rect, 2)  # Border

    #     # Draw pawns
    #     for player in self.players:
    #         for pawn_position in player.pawns:
    #             x, y = pawn_position
    #             center_x = self.padding + y * self.cell_size + self.cell_size // 2
    #             center_y = self.padding + x * self.cell_size + self.cell_size // 2
    #             pygame.draw.circle(self.screen, player.color, (center_x, center_y), self.cell_size // 3)

    #     pygame.display.flip()
