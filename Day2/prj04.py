##########import##########
import pygame
##########basic settings##########
width = 800
height = 600
fps = 60
background = (0, 0, 0)
paddle_color = (245, 245, 255)
ball_color = (255, 255, 255)
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
class Brick:
    def __init__(self, x, y, width, height, color):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.alive = True
    def draw(self, surface):
        if self.alive:
            pygame.draw.rect(surface, self.color, self.rect, border_radius=3)

class Paddle:
    def __init__(self):
        self.rect = pygame.Rect(0, 0, 120, 16)
        self.rect.midbottom = (width // 2, height - 34)
        self.speed = 8
    def update(self, keys):
        direction = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction += 1
        self.rect.x += direction * self.speed
        self.rect.x = max(0, min(self.rect.x, width - self.rect.width))
    def draw(self, surface):
        pygame.draw.rect(surface, paddle_color, self.rect, border_radius=8)

class Ball:
    def __init__(self, paddle):
        self.radius = 9
        self.position = pygame.Vector2(0, 0)
        self.velocity = pygame.Vector2(5, -5)
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.launched = False
        self.reset(paddle)
    def reset(self, paddle):
        self.launched = False
        self.position.update(paddle.rect.centerx, paddle.rect.top - self.radius)
        self. velocity.update(5, -5)
        self.rect.center = (round(self.position.x), round(self.position.y))
    def launch(self):
        self.launched = True
    def update(self, paddle):
        if not self.launched:
            self.position.update(
                paddle.rect.centerx,
                paddle.rect.top - self.radius
            )
        else:
            self.position += self.velocity
            if self.position.x - self.radius <= 0:
                self.position.x = self.radius
                self.velocity.x *= -1
            elif self.position.x + self.radius >= width:
                self.position.x = width - self.radius
                self.velocity.x *= -1
            if self.position.y - self.radius <= 0:
                self.position.y = self.radius
                self.velocity.y *= -1
            if self.position.y - self.radius > height:
                self.reset(paddle)
        self.rect.center = (round(self.position.x), round(self.position.y))
    def draw(self, surface):
        pygame.draw.circle(surface,ball_color, self.rect.center, self.radius)
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
            bricks.append(Brick(x, y, brick_width, brick_height, color))

    return bricks
##########bricks##########
bricks = create_bricks()
##########paddle##########
paddle = Paddle()
##########ball##########
ball = Ball(paddle)
##########main code##########
running = True
while running:
    clock.tick(fps)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_SPACE:
                ball.launch()
    keys = pygame.key.get_pressed()
    paddle.update(keys)
    ball.update(paddle)
    screen.fill(background)
    for Brick in bricks:
        Brick.draw(screen)
    paddle.draw(screen)
    ball.draw(screen)
    pygame.display.flip()
##########game over settings##########
pygame.quit()