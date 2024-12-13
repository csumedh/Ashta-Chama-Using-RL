import pygame
from board_updated import Board
from feat_StrategicPlayers_updated import StrategicPlayer


# Initialize pygame
pygame.init()

# Set up the game window
screen_width, screen_height = 800, 600  # Dimensions of the game window
screen = pygame.display.set_mode((screen_width, screen_height))  # Create a window with the specified dimensions
pygame.display.set_caption("Strategic Game")  # Set the title of the window

# Initialize the board
game_board = Board()  # Create an instance of the Board class

# Define player start positions and colors
start_positions = [
    [(0, 4), (1, 4)],  # Player 1 starting positions
    [(4, 0), (4, 1)],  # Player 2 starting positions
    [(8, 4), (7, 4)],  # Player 3 starting positions
    [(4, 8), (4, 7)]   # Player 4 starting positions
]

colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]  # Colors for players: Red, Green, Blue, Yellow
strategies = ["defensive", "aggressive", "defensive", "aggressive"]  # Strategies for each player

# Add players to the game
for i in range(len(start_positions)):
    # Create a StrategicPlayer instance for each player
    player = StrategicPlayer(
        player_id=i,  # Unique ID for each player
        start_positions=start_positions[i],  # Initial positions of pawns
        color=colors[i],  # Color assigned to the player
        strategy=strategies[i]  # Strategy assigned to the player
    )
    game_board.add_player(player)  # Add the player to the game board

players = game_board.players  # Reference to all players in the game

# Game loop
running = True  # Flag to keep the game running
clock = pygame.time.Clock()  # Clock object to control the frame rate
current_player_id = 0  # ID of the player whose turn it is

while running:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:  # Check if the user wants to quit
            running = False

    # Clear the screen and render the board
    screen.fill((255, 255, 255))  # Fill the screen with a white background
    game_board.render(screen)  # Draw the board and players on the screen

    # Perform a move for the current player
    current_player = game_board.players[current_player_id]  # Get the current player
    possible_moves = []  # List to store all possible moves for the player
    roll = game_board.diceRoll()  # Simulate rolling a dice

    # Calculate possible moves for each pawn of the current player
    for pawn_index, pawn in enumerate(current_player.pawns):
        if pawn is None:  # Skip pawns that are no longer in play
            continue
        # Use the move function from Board to calculate the new position
        new_position = game_board.move(current_player, pawn_index, roll)
        if new_position != pawn:  # Check if the pawn can move
            # Append the move information as a tuple
            possible_moves.append((current_player_id, current_player.kill, pawn_index, new_position))

    # If there are possible moves, decide and execute the best move
    if possible_moves:
        chosen_move = current_player.decide_move(possible_moves, game_board.players)  # Choose a move based on strategy
        _, _, pawn_index, new_position = chosen_move  # Unpack the chosen move
        print(chosen_move)  # Print the chosen move
        current_player.update_position(pawn_index, new_position)  # Update the pawn's position

    # Check if the current player has won
    win, winner = game_board.check_winner(chosen_move)  # Check for a winning condition
    if win:
        # Announce the winner and their strategy
        print(f"Player {winner.player_id} wins!")
        print(f"Player {winner.player_id} strategy: {winner.strategy}")
        # Display the scores of all players
        print(f"The scores of all players are: {[player.score for player in game_board.players]}")
        running = False  # End the game

    # Cycle to the next player
    current_player_id = (current_player_id + 1) % len(game_board.players)  # Move to the next player's turn

    # Cap the frame rate
    clock.tick(1)  # Limit the loop to 1 frame per second

    # Update the display
    pygame.display.flip()  # Update the screen with the latest changes

# Quit the game
pygame.quit()  # Cleanly exit the game
