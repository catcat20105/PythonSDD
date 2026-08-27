##########import##########
import pygame
import random
##########basic settings##########
width = 800
height = 600
fps = 60
background = (0, 0, 0)
paddle_color = (245, 245, 255)
ball_color = (255, 255, 255)
obstacle_color = (255, 165, 0)
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
font = pygame.font.Font(None, 32)
game_over_font = pygame.font.Font(None, 72)
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
        missed = False
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
                missed = True
                self.reset(paddle)
        self.rect.center = (round(self.position.x), round(self.position.y))
        return missed
    def draw(self, surface):
        pygame.draw.circle(surface,ball_color, self.rect.center, self.radius)

class Obstacle:
    def __init__(self, x, y):
        self.radius = 18
        self.rect = pygame.Rect(0, 0, self.radius * 2, self.radius * 2)
        self.rect.center = (x, y)
    def draw(self, surface):
        pygame.draw.circle(surface, obstacle_color, self.rect.center, self.radius)
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

def create_obstacles(level):
    obstacles = []
    for _ in range(level - 1):
        x = random.randint(50, width - 50)
        y = random.randint(270, height - 100)
        obstacles.append(Obstacle(x, y))
    return obstacles

def bounce_from_rect(ball, target_rect):
    overlaps = {
        "left": ball.rect.right - target_rect.left,
        "right": target_rect.right - ball.rect.left,
        "top": ball.rect.bottom - target_rect.top,
        "bottom": target_rect.bottom - ball.rect.top
    }
    collision_side = min(overlaps, key=overlaps.get)
    if collision_side in ("left", "right"):
        ball.velocity.x *= -1
    else:
        ball.velocity.y *= -1
def handle_collisions(ball, paddle, bricks, obstacles):
    if ball.velocity.y > 0 and ball.rect.colliderect(paddle.rect):
        ball.rect.bottom = paddle.rect.top
        ball.position.y = ball.rect.centery
        ball.velocity.y = -abs(ball.velocity.y)
        offset = (ball.rect.centerx - paddle.rect.centerx) / (paddle.rect.width / 2)
        ball.velocity.x = 6 * offset
    for brick in bricks:
        if brick.alive and ball.rect.colliderect(brick.rect):
            brick.alive = False
            bounce_from_rect(ball, brick.rect)
            break
    for obstacle in obstacles:
        if ball.rect.colliderect(obstacle.rect):
            bounce_from_rect(ball, obstacle.rect)
            break
##########bricks##########
bricks = create_bricks()
##########paddle##########
paddle = Paddle()
##########ball##########
ball = Ball(paddle)
##########main code##########
lives = 4587237521477864976498
level = 1
obstacles = create_obstacles(level)
level_message_frames = 0
game_over = False
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
                if game_over:
                    lives = 3
                    level = 1
                    bricks = create_bricks()
                    obstacles = create_obstacles(level)
                    level_message_frames = 0
                    paddle = Paddle()
                    ball = Ball(paddle)
                    game_over = False
                    ball.launch()
                else:
                    ball.launch()
    if not game_over:
        if level_message_frames > 0:
            level_message_frames -= 1
            if level_message_frames == 0:
                ball.launch()
        else:
            keys = pygame.key.get_pressed()
            paddle.update(keys)
            if ball.update(paddle):
                lives -= 1
                if lives == 0:
                    game_over = True
            handle_collisions(ball, paddle, bricks, obstacles)
            # Go to the next level when no bricks are alive.
            if lives > 0 and not any(brick.alive for brick in bricks):
                level += 1
                bricks = create_bricks()
                obstacles = create_obstacles(level)
                ball.reset(paddle)
                level_message_frames = fps * 3
    screen.fill(background)
    if level_message_frames == 0 or game_over:
        for Brick in bricks:
            Brick.draw(screen)
        for obstacle in obstacles:
            obstacle.draw(screen)
        paddle.draw(screen)
        ball.draw(screen)
    lives_text = font.render(f"Lives: {lives}", True, ball_color)
    screen.blit(lives_text, (10, 10))
    level_text = font.render(f"Level: {level}", True, ball_color)
    screen.blit(level_text, (10, 40))
    obstacle_text = font.render(f"Obstacles: {len(obstacles)}", True, obstacle_color)
    screen.blit(obstacle_text, (10, 70))
    if level_message_frames > 0 and not game_over:
        level_text = game_over_font.render(f"LEVEL {level}", True, ball_color)
        level_rect = level_text.get_rect(center=(width // 2, height // 2))
        screen.blit(level_text, level_rect)
    if game_over:
        game_over_text = game_over_font.render("GAME OVER", True, ball_color)
        game_over_rect = game_over_text.get_rect(center=(width // 2, height // 2 - 20))
        screen.blit(game_over_text, game_over_rect)
        replay_text = font.render("Press SPACE to replay", True, ball_color)
        replay_rect = replay_text.get_rect(center=(width // 2, height // 2 + 40))
        screen.blit(replay_text, replay_rect)
    pygame.display.flip()
##########game over settings##########
pygame.quit()