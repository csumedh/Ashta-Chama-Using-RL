import gym
from gym import spaces
import numpy as np
import pygame
from helper import diceRoll, move, checkEnemy, possibleMoves, board_overview, safe_places, home_places
from player import Player
from path import getPath

class AshtaChammaEnv(gym.Env):
    def __init__(self):
        super(AshtaChammaEnv, self).__init__()
        pygame.init()
        self.SIZE=(self.width,self.height)=(800,600)
        self.HEIGHT = 9
        self.WIDTH = 9
        self.BOARD_PADDING = 20
        self.board_origin = (self.BOARD_PADDING, self.BOARD_PADDING)
        self.board_height = ((7/8) * self.height) - (self.BOARD_PADDING * 2)	
        self.board_width = self.width - (self.BOARD_PADDING * 2)
        self.cell_size = int(min(self.board_height / self.WIDTH, self.board_width / self.HEIGHT))
        self.WHITE = (255, 255, 255)
        self.GRAY  = (180, 180, 180)
        self.BLACK = (0, 0, 0)
        self.screen=pygame.display.set_mode((self.width,self.height))
        self.home_colors=[self.WHITE, self.WHITE, self.WHITE, self.WHITE]
        self.OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
        self.smallFont = pygame.font.Font(self.OPEN_SANS, 20)
        self.mediumFont = pygame.font.Font(self.OPEN_SANS, 28)
        self.largeFont = pygame.font.Font(self.OPEN_SANS, 40)
        self.colors=[(250, 39, 55), (42, 122, 218), (58, 154, 26), (220, 160, 20)]
        # Define action and observation spaces
        self.action_space = spaces.Discrete(16)  # 4 players * 4 pawns
        self.observation_space = spaces.Dict({
            'board': spaces.Box(low=0, high=4, shape=(9, 9), dtype=np.int32),
            'current_player': spaces.Discrete(4),
            'dice_roll': spaces.Discrete(8),
            'killed': spaces.MultiBinary(4)
        })
        
        # Initialize game state
        self.reset()

    def reset(self):
        # Reset the game state
        self.board = np.zeros((9, 9), dtype=np.int32)
        self.current_player = 0
        self.dice_roll = 0
        self.killed = [False] * 4
        cells = self.drawBoard()
        self.players = [Player(cells, i // 4, i % 4) for i in range(16)]
        
        # Place pawns in starting positions
        for player in self.players:
            self.board[player.Tup[0]][player.Tup[1]] = player.color + 1
        
        return self._get_obs()

    def step(self, action):
        # Execute the action
        pawn = self.players[action]
        if pawn.color != self.current_player:
            return self._get_obs(), -1, False, False, {'error': 'Invalid move'}
        
        new_position = move(self.dice_roll, pawn.Tup, pawn.color, self.killed[pawn.color])
        
        # Update board
        self.board[pawn.Tup[0]][pawn.Tup[1]] = 0
        self.board[new_position[0]][new_position[1]] = pawn.color + 1
        pawn.Tup = new_position
        
        # Check for kills
        enemy = checkEnemy(new_position, pawn.color)
        if enemy:
            self.killed[pawn.color] = True
            enemy.goToStart(None)
            self.board[enemy.Tup[0]][enemy.Tup[1]] = enemy.color + 1
        
        # Check for game end
        done = all(p.Tup == (4, 4) for p in self.players if p.color == self.current_player)
        
        # Calculate reward
        reward = 1 if done else 0
        
        # Move to next player
        self.current_player = (self.current_player + 1) % 4
        self.dice_roll = diceRoll()[0]
        
        return self._get_obs(), reward, done, False, {}

    def _get_obs(self):
        return {
            'board': self.board,
            'current_player': self.current_player,
            'dice_roll': self.dice_roll,
            'killed': self.killed
        }

    def render(self, mode='human'):
        if mode != 'human':
            return

        self.screen.fill(self.BLACK)
        cells = self.drawBoard()
        self.drawEverything()

        # Display the number on the die
        displayBox = pygame.Rect((7 * self.height)//8 + self.BOARD_PADDING, (4 * self.width)//8 + self.BOARD_PADDING, (self.height//3) - self.BOARD_PADDING * 2, 50)
        pygame.draw.rect(self.screen, self.WHITE, displayBox)
        N = self.mediumFont.render(str(self.dice_roll), True, self.BLACK)
        textRect = N.get_rect()
        textRect.center = displayBox.center
        self.screen.blit(N, textRect)

        # Box shows who's turn it is
        turnBox = pygame.Rect((7 * self.height)//8 + self.BOARD_PADDING, (2 * self.width)//8 + self.BOARD_PADDING, (self.height//3) - self.BOARD_PADDING * 2, 50)
        color = self.colors[self.current_player]
        pygame.draw.rect(self.screen, color, turnBox)
        text = "Who's turn"
        text = self.mediumFont.render(text, True, self.BLACK)
        textRect = text.get_rect()
        textRect.center = turnBox.center
        self.screen.blit(text, textRect)

        pygame.display.flip()

    def drawBoard(self):
        cells = []
        h_color = 0
        for i in range(self.HEIGHT):
            row = []
            for j in range(self.WIDTH):
                rect = pygame.Rect(
                    self.board_origin[0] + j * self.cell_size,
                    self.board_origin[1] + i * self.cell_size,
                    self.cell_size, self.cell_size
                )
                if i != 0 and i != self.HEIGHT-1 and j != 0 and j != self.WIDTH-1:
                    if (i, j) in safe_places:
                        pygame.draw.rect(self.screen, (240, 207, 174), rect)
                        pygame.draw.rect(self.screen, self.WHITE, rect, 2)
                        cross = pygame.image.load("assets/icons/cross.png")
                        cross = pygame.transform.scale(cross, (53, 53))
                        self.screen.blit(cross, (self.board_origin[0] + j * self.cell_size, self.board_origin[1] + i * self.cell_size))
                    else:
                        pygame.draw.rect(self.screen, (240, 207, 174), rect)
                        pygame.draw.rect(self.screen, self.WHITE, rect, 2)
                else:
                    if (i, j) in home_places:
                        pygame.draw.rect(self.screen, self.home_colors[h_color], rect)
                        pygame.draw.rect(self.screen, self.WHITE, rect, 2)
                        h_color = (h_color + 1) % 4
                    else:
                        pygame.draw.rect(self.screen, self.BLACK, rect)
                        pygame.draw.rect(self.screen, self.BLACK, rect, 2)
                row.append(rect)
            cells.append(row)
        return cells

    def drawEverything(self):
        cells = self.drawBoard()
        for j in range(4):
            for i in range(4):
                self.drawPawn(self.players[j*4 + i].image, self.players[j*4 + i].Position)

    def drawPawn(self, pawn, position):
        self.screen.blit(pawn, position)