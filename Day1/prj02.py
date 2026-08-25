##########import##########
import pygame
##########basic settings##########
width = 800
height = 600
fps = 60
background = (0, 0, 0)
brick_colors = [
    (244, 114, 182),
    (251, 146, 60),
    (250, 204, 21),
    (74, 222, 128),
    (56, 189, 248)
]
##########initial settings##########
pygame.init()
##########game window settings##########
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("GAME")
clock = pygame.time.Clock()
##########objects##########
class brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.alive = True
    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=3)
##########.##########
def create_bricks():
    bricks = []
    rows = 5
    columns = 9
    brick_width = 72
    brick_height = 24
    gap = 8
    start_x = 44
    start_y = 70
    for row in range(rows):
        for column in range(columns):
            x = start_x + column * (brick_width + gap)
            y = start_y + row * (brick_height + gap)
            color = brick_colors[row]
            bricks.append(brick(x, y, brick_width, brick_height, color))

    return bricks
##########bricks##########
bricks = create_bricks()
##########main code##########
running = True
while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False
    screen.fill(background)
    for brick in bricks:
        brick.draw(screen)
    pygame.display.flip()
##########game over settings##########
pygame.quit()