import pygame
from ple import PLE
from ple.games.monochrome_pixelcopter import Pixelcopter
import sys

# Initialize Pygame and set up the window
pygame.init()
pygame.display.set_caption("Pixelcopter Game")

# Create the game and pass it to the PLE environment
game = Pixelcopter(width=500, height=500)  # Adjusted dimensions for better visibility
p = PLE(game, fps=30, display_screen=True)
p.init()

pygame.init()

# Assuming game.getScreenDims() returns the screen dimensions
screen = pygame.display.set_mode(game.getScreenDims())
font = pygame.font.Font(None, 36)  # Use a default font and a size of 36

# Main game loop
game_over = False
while not game_over:
    while not p.game_over():
        pygame.event.pump()  # Process event queue
        keys = pygame.key.get_pressed()
        action = None

        if keys[pygame.K_SPACE]:  # Using spacebar to go up
            action = game.actions['up']

        reward = p.act(action)
        screen.blit(pygame.surfarray.make_surface(game.getScreenRGB()), (0, 0))
        pygame.display.flip()
        pygame.time.wait(33)

    # Game Over display
    text = font.render('Game Over! Press R to Restart or Q to Quit', True, (255, 0, 0))
    screen.blit(text, (50, 50))  # Position the text at (50, 50) on the screen
    pygame.display.flip()

    # Wait for player decision
    waiting_for_input = True
    while waiting_for_input:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:  # Restart game
                    p.reset_game()  # Reset game to initial state
                    waiting_for_input = False
                elif event.key == pygame.K_q:  # Quit game
                    game_over = True
                    waiting_for_input = False


pygame.quit()
