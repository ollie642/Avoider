import pygame
import random

pygame.font.init()

WIN_HEIGHT = 900
WIN_WIDTH = 400

STAT_FONT = pygame.font.SysFont("comicsans", 50)

BG_IMG = pygame.image.load("background.png")
BALL_IMG = pygame.image.load("ball.png")
RECT_IMG = pygame.image.load("rect.png")
PROJ_IMG = pygame.image.load("red_ball.png")

wall_last_deployed = pygame.time.get_ticks()
proj_last_deployed = pygame.time.get_ticks()


# for every obstruction, water level rises
# for every completion, water level drops

class Ball:

    def __init__(self, IMG):
        self.x = 100
        self.y = 200
        self.img = IMG

    def move(self, mouse_x, mouse_y):
        self.x = mouse_x
        self.y = mouse_y

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

    def dead(self, WATER_LEVEL):
        if self.y > WATER_LEVEL:
            return True
        if WATER_LEVEL < 1:
            return True
        return False


class Obstruction:
    def __init__(self):
        self.x = 0
        self.y = 0
        self.collision = False


class Wall_Block(Obstruction):
    VEL = 8

    def __init__(self, isle, shape):
        super().__init__()

        self.shape = shape
        self.y = 0
        if isle == 1:
            self.x = 0
        elif isle == 2:
            self.x = 100
        elif isle == 3:
            self.x = 200
        elif isle == 4:
            self.x = 300

    def move(self):
        self.y += self.VEL

    def draw(self, window):
        window.blit(self.shape, (round(self.x), round(self.y)))

    def collide(self, ball):
        block_mask = pygame.mask.from_surface(self.shape)
        ball_mask = ball.get_mask()

        offset = (round(self.x - ball.x), round(self.y - ball.y))

        overlap = ball_mask.overlap(block_mask, offset)

        if overlap:
            self.collision = True
            return True
        return False

    def complete(self, WATER_LEVEL):
        if self.y >= WATER_LEVEL:
            return True
        return False


class Proj_Block(Obstruction):
    acc_y = 2
    IMG = PROJ_IMG

    def __init__(self):
        super().__init__()
        self.velocity_x = random.randint(1, 5)
        self.velocity_y = 0
        self.spawn()

    def spawn(self):
        side = random.randint(1, 3)
        if side == 1:
            self.y = random.randint(0, 300)
            self.x = -50
            self.acc_x = -1
        elif side == 2:
            self.y = -50
            self.x = random.randint(0, 400)
            if self.x < 200:
                self.acc_x = -1
            elif self.x >= 200:
                self.acc_x = 1
        elif side == 3:
            self.y = random.randint(0, 300)
            self.x = 450
            self.acc_x = 1

    def move(self):
        self.velocity_x += self.acc_x
        self.velocity_y += self.acc_y
        self.x += self.velocity_x
        self.y += self.velocity_y

    def draw(self, window):
        window.blit(self.IMG, (round(self.x), round(self.y)))


class Laser:
    pass


def draw_window(window, wall_blocks, ball, WATER_LEVEL, score, proj_blocks):
    window.blit(BG_IMG, (0, 0))

    for block in wall_blocks:
        block.draw(window)

    for proj in proj_blocks:
        proj.draw(window)

    ball.draw(window)

    pygame.draw.rect(window, (0, 0, 255), (0, WATER_LEVEL, WIN_WIDTH, WIN_HEIGHT - WATER_LEVEL))

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    window.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    pygame.display.update()


def new_wall_block(wall_blocks, shape):
    global wall_last_deployed
    BLOCK_TIME_GAP = 400
    now = pygame.time.get_ticks()
    if now - wall_last_deployed >= BLOCK_TIME_GAP:
        wall_last_deployed = now
        rand_isle1 = random.randint(1, 4)
        rand_isle2 = random.randint(1, 4)
        while rand_isle1 == rand_isle2:
            rand_isle2 = random.randint(1, 4)
        wall_blocks.append(Wall_Block(rand_isle1, shape))
        wall_blocks.append(Wall_Block(rand_isle2, shape))


def new_proj_block(proj_blocks):
    global proj_last_deployed
    BLOCK_TIME_GAP = 750
    now = pygame.time.get_ticks()
    if now - proj_last_deployed >= BLOCK_TIME_GAP:
        proj_last_deployed = now
        proj_blocks.append(Proj_Block())


def main():
    window = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    pygame.display.set_caption("Avoider")
    pygame.mouse.set_visible(0)
    clock = pygame.time.Clock()
    wall_last_deployed = pygame.time.get_ticks()
    WATER_LEVEL = WIN_HEIGHT
    score = 0

    player_ball = Ball(BALL_IMG)
    wall_blocks = [Wall_Block(1, RECT_IMG)]
    proj_blocks = []

    run = True
    while run:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()

        mouse_x, mouse_y = pygame.mouse.get_pos()

        rem = []
        for block in wall_blocks:
            if block.collide(player_ball):
                WATER_LEVEL += -4

            if block.complete(WATER_LEVEL):
                rem.append(block)
                if not block.collision:
                    if WATER_LEVEL < WIN_HEIGHT:
                        WATER_LEVEL += 3
                    score += 1
                elif block.collision:
                    score -= 5

        for block in rem:
            wall_blocks.remove(block)

        for block in wall_blocks:
            block.move()

        for proj in proj_blocks:
            proj.move()

        new_wall_block(wall_blocks, RECT_IMG)
        new_proj_block(proj_blocks)

        player_ball.move(mouse_x, mouse_y)
        if player_ball.dead(WATER_LEVEL):
            run = False
            print("You Lost")

        draw_window(window, wall_blocks, player_ball, WATER_LEVEL, score, proj_blocks)


if __name__ == "__main__":
    main()
