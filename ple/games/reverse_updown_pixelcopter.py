import math
import sys

#import .base
from .base.pygamewrapper import PyGameWrapper

import pygame
from pygame.constants import K_w, K_s
from .utils.vec2d import vec2d
import numpy as np

class Block(pygame.sprite.Sprite):

    def __init__(self, pos_init, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)

        self.width = int(SCREEN_WIDTH * 0.1)
        self.height = int(SCREEN_HEIGHT * 0.2)
        self.speed = speed

        self.SCREEN_WIDTH = SCREEN_WIDTH
        self.SCREEN_HEIGHT = SCREEN_HEIGHT

        image = pygame.Surface((self.width, self.height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (120, 240, 80),
            (0, 0, self.width, self.height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dt):
        self.pos.x -= self.speed * dt

        self.rect.center = (self.pos.x, self.pos.y)


class HelicopterPlayer(pygame.sprite.Sprite):

    def __init__(self, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        pos_init = (int(SCREEN_WIDTH * 0.35), SCREEN_HEIGHT / 2)
        self.pos = vec2d(pos_init)
        self.speed = speed
        self.climb_speed = speed * -0.09  # -0.0175
        self.fall_speed = speed * 0.35  # 0.0019
        self.momentum = 0

        self.width = SCREEN_WIDTH * 0.05
        self.height = SCREEN_HEIGHT * 0.05

        image = pygame.Surface((self.width, self.height))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        pygame.draw.rect(
            image,
            (255, 255, 255),
            (0, 0, self.width, self.height),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, is_falling, dt):
        self.momentum += (self.fall_speed if is_falling else self.climb_speed) * dt
        self.momentum *= 0.99
        self.pos.y += self.momentum

        self.rect.center = (self.pos.x, self.pos.y)


class Terrain(pygame.sprite.Sprite):

    def __init__(self, pos_init, speed, SCREEN_WIDTH, SCREEN_HEIGHT):
        pygame.sprite.Sprite.__init__(self)

        self.pos = vec2d(pos_init)
        self.speed = speed
        self.width = int(SCREEN_WIDTH * 0.1)

        image = pygame.Surface((self.width, SCREEN_HEIGHT * 1.5))
        image.fill((0, 0, 0, 0))
        image.set_colorkey((0, 0, 0))

        color = (120, 240, 80)

        # top rect
        pygame.draw.rect(
            image,
            color,
            (0, 0, self.width, SCREEN_HEIGHT * 0.5),
            0
        )

        # bot rect
        pygame.draw.rect(
            image,
            color,
            (0, SCREEN_HEIGHT * 1.05, self.width, SCREEN_HEIGHT * 0.5),
            0
        )

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.center = pos_init

    def update(self, dt):
        self.pos.x -= self.speed * dt
        self.rect.center = (self.pos.x, self.pos.y)


class Pixelcopter(PyGameWrapper):
    """
    Parameters
    ----------
    width : int
        Screen width.

    height : int
        Screen height, recommended to be same dimension as width.

    """

    def __init__(self, width=48, height=48):
        super().__init__(width, height, actions={'up': pygame.K_SPACE})
        self.speed = 0.0004 * width
        self.rng = np.random.RandomState(24)  # Initialize the random number generator
        self.player = HelicopterPlayer(self.speed, width, height)
        self.is_falling = False
        pygame.font.init()
        self.font = pygame.font.SysFont('Arial', 24)
        self.init()

    def _handle_player_events(self):
        self.is_falling = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    self.is_falling = True
            elif event.type is pygame.KEYUP:
                if event.key == pygame.K_SPACE:
                    self.is_falling = False

    def getGameState(self):
        """
        Gets a non-visual state representation of the game.

        Returns
        -------

        dict
            * player y position.
            * player velocity.
            * player distance to floor.
            * player distance to ceiling.
            * next block x distance to player.
            * next blocks top y location,
            * next blocks bottom y location.

            See code for structure.

        """

        min_dist = 999
        min_block = None
        for b in self.block_group:  # Groups do not return in order
            dist_to = b.pos.x - self.player.pos.x
            if dist_to > 0 and dist_to < min_dist:
                min_block = b
                min_dist = dist_to

        current_terrain = pygame.sprite.spritecollide(
            self.player, self.terrain_group, False)[0]
        state = {
            "player_y": self.player.pos.y,
            "player_vel": self.player.momentum,
            "player_dist_to_ceil": self.player.pos.y - (current_terrain.pos.y - self.height * 0.25),
            "player_dist_to_floor": (current_terrain.pos.y + self.height * 0.25) - self.player.pos.y,
            "next_gate_dist_to_player": min_dist,
            "next_gate_block_top": min_block.pos.y,
            "next_gate_block_bottom": min_block.pos.y + min_block.height
        }

        return state

    def getScreenDims(self):
        return self.screen_dim

    def getActions(self):
        return self.actions.values()

    def getScore(self):
        return self.score

    def game_over(self):
        return self.lives <= 0.0

    def init(self):
        self.score = 0.0
        self.lives = 1.0

        self.player = HelicopterPlayer(
            self.speed,
            self.width,
            self.height
        )

        self.player_group = pygame.sprite.Group()
        self.player_group.add(self.player)

        self.block_group = pygame.sprite.Group()
        self._add_blocks()

        self.terrain_group = pygame.sprite.Group()
        self._add_terrain(0, self.width * 4)

    def _add_terrain(self, start, end):
        w = int(self.width * 0.1)
        # each block takes up 10 units.
        steps = range(start + int(w / 2), end + int(w / 2), w)
        y_jitter = []

        freq = 4.5 / self.width + self.rng.uniform(-0.01, 0.01)
        for step in steps:
            jitter = (self.height * 0.125) * \
                math.sin(freq * step + self.rng.uniform(0.0, 0.5))
            y_jitter.append(jitter)

        y_pos = [int((self.height / 2.0) + y_jit) for y_jit in y_jitter]

        for i in range(0, len(steps)):
            self.terrain_group.add(Terrain(
                (steps[i], y_pos[i]),
                self.speed,
                self.width,
                self.height
            )
            )

    def _add_blocks(self):
        x_pos = self.rng.randint(self.width, int(self.width * 1.5))
        y_pos = self.rng.randint(
            int(self.height * 0.25),
            int(self.height * 0.75)
        )
        self.block_group.add(
            Block(
                (x_pos, y_pos),
                self.speed,
                self.width,
                self.height
            )
        )

    def reset(self):
        self.init()


    def step(self, dt):

        self.screen.fill((0, 0, 0))
        self._handle_player_events()


        self.player.update(self.is_falling, dt)
        self.block_group.update(dt)
        self.terrain_group.update(dt)

        hits = pygame.sprite.spritecollide(
            self.player, self.block_group, False)
        for creep in hits:
            self.lives -= 1

        hits = pygame.sprite.spritecollide(
            self.player, self.terrain_group, False)
        for t in hits:
            if self.player.pos.y - self.player.height <= t.pos.y - self.height * 0.25:
                self.lives -= 1

            if self.player.pos.y >= t.pos.y + self.height * 0.25:
                self.lives -= 1

        for b in self.block_group:
            if b.pos.x <= self.player.pos.x and len(self.block_group) == 1:
                self.score += 1
                self._add_blocks()

            if b.pos.x <= -b.width:
                b.kill()
        for t in self.terrain_group:
            if t.pos.x <= -t.width:
                t.kill()

        if self.player.pos.y < self.height * 0.125:  # its above
            self.lives -= 1

        if self.player.pos.y > self.height * 0.875:  # its below the lowest possible block
            self.lives -= 1

        if len(self.terrain_group) <= (
                10 + 3):  # 10% per terrain, offset of ~2 with 1 extra
            self._add_terrain(self.width, self.width * 5)

        if self.lives <= 0.0:

            final_score_text = self.font.render(f'Final Score: {self.score}', True, (255, 255, 255))
            text_rect = final_score_text.get_rect(center=(self.width//2, self.height//2))
            self.screen.blit(final_score_text, text_rect)

        self.player_group.draw(self.screen)
        self.block_group.draw(self.screen)
        self.terrain_group.draw(self.screen)
        
        pygame.display.flip()


if __name__ == "__main__":
    import numpy as np

    pygame.init()
    game = Pixelcopter(width=256, height=256)
    game.screen = pygame.display.set_mode(game.getScreenDims(), 0, 32)
    game.clock = pygame.time.Clock()
    game.rng = np.random.RandomState(24)
    game.init()

    while True:
        if game.game_over():
            game.reset()
        dt = game.clock.tick_busy_loop(30)
        game.step(dt)
        pygame.display.update()

