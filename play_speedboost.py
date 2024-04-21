import pygame
from ple import PLE
from ple.games.speed_boost import Pixelcopter

# Initialize Pygame and set up the window
pygame.init()
pygame.display.set_caption("Pixelcopter Game")

# Create the game and pass it to the PLE environment
game = Pixelcopter(width=500, height=500)  # Adjusted dimensions for better visibility
p = PLE(game, fps=30, display_screen=True)
p.init()

# Create a display surface
screen = pygame.display.set_mode(game.getScreenDims())

# Main game loop
while not p.game_over():
    pygame.event.pump()  # Process event queue

    keys = pygame.key.get_pressed()
    action = None

    if keys[pygame.K_SPACE]:  # Using spacebar to go up
        action = game.actions['up']

    # Perform action in the game environment and get the reward
    reward = p.act(action)

    # Render the game state
    screen.blit(pygame.surfarray.make_surface(game.getScreenRGB()), (0, 0))
    pygame.display.flip()

    # Delay to control the game speed
    pygame.time.wait(33)  # Approx. 30 frames per second

pygame.quit()
