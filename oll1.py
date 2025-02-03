import pygame
import math
import time
pygame.init()

WIDTH, HEIGHT = 1200, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Бильярд")

GREEN = (34, 139, 34)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)

FPS = 60
BALL_RADIUS = 15
HOLE_RADIUS = 20 
TABLE_WIDTH, TABLE_HEIGHT = 1000, 600
TABLE_OFFSET_X, TABLE_OFFSET_Y = (WIDTH - TABLE_WIDTH) // 2, (HEIGHT - TABLE_HEIGHT) // 2

FRICTION = 0.98
BALL_SPEED = 10
WALL_FRICTION = 0.95
COLLISION_FRICTION = 0.95

class Ball:
    def __init__(self, x, y, color, speed_x=0, speed_y=0):
        self.x = x
        self.y = y
        self.color = color
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.in_hole = False
        self.hole_timer = 0

    def move(self):
        if not self.in_hole:
            self.x += self.speed_x
            self.y += self.speed_y
            self.speed_x *= FRICTION
            self.speed_y *= FRICTION

    def draw(self):
        if not self.in_hole:
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), BALL_RADIUS)

    def collide_with_ball(self, other):
        if self.in_hole or other.in_hole:
            return

        dx = self.x - other.x
        dy = self.y - other.y
        distance = math.hypot(dx, dy)

        if distance <= BALL_RADIUS * 2:
            angle = math.atan2(dy, dx)

            speed1 = math.hypot(self.speed_x, self.speed_y)
            speed2 = math.hypot(other.speed_x, other.speed_y)

            direction1 = math.atan2(self.speed_y, self.speed_x)
            direction2 = math.atan2(other.speed_y, other.speed_x)

            new_speed_x1 = speed2 * math.cos(direction2 - angle) * math.cos(angle) + speed1 * math.sin(direction1 - angle) * math.cos(angle + math.pi / 2)
            new_speed_y1 = speed2 * math.cos(direction2 - angle) * math.sin(angle) + speed1 * math.sin(direction1 - angle) * math.sin(angle + math.pi / 2)
            new_speed_x2 = speed1 * math.cos(direction1 - angle) * math.cos(angle) + speed2 * math.sin(direction2 - angle) * math.cos(angle + math.pi / 2)
            new_speed_y2 = speed1 * math.cos(direction1 - angle) * math.sin(angle) + speed2 * math.sin(direction2 - angle) * math.sin(angle + math.pi / 2)

            self.speed_x = new_speed_x1 * COLLISION_FRICTION
            self.speed_y = new_speed_y1 * COLLISION_FRICTION
            other.speed_x = new_speed_x2 * COLLISION_FRICTION
            other.speed_y = new_speed_y2 * COLLISION_FRICTION

            overlap = BALL_RADIUS * 2 - distance
            angle = math.atan2(dy, dx)
            self.x += math.cos(angle) * overlap / 2
            self.y += math.sin(angle) * overlap / 2
            other.x -= math.cos(angle) * overlap / 2
            other.y -= math.sin(angle) * overlap / 2

    def collide_with_walls(self):
        if self.in_hole:
            return

        if self.x - BALL_RADIUS < TABLE_OFFSET_X or self.x + BALL_RADIUS > TABLE_OFFSET_X + TABLE_WIDTH:
            self.speed_x *= -1 * WALL_FRICTION

        if self.y - BALL_RADIUS < TABLE_OFFSET_Y or self.y + BALL_RADIUS > TABLE_OFFSET_Y + TABLE_HEIGHT:
            self.speed_y *= -1 * WALL_FRICTION

    def check_hole_collision(self, holes):
        if self.in_hole:
            return

        for hole in holes:
            distance = math.hypot(self.x - hole[0], self.y - hole[1])
            if distance <= HOLE_RADIUS:
                self.in_hole = True
                self.hole_timer = time.time()
                self.speed_x = 0
                self.speed_y = 0
                break

class Cue:
    def __init__(self):
        self.angle = 0
        self.power = 0
        self.active = False
        self.mouse_pressed = False
        self.start_pos = (0, 0)
        self.end_pos = (0, 0)

    def draw(self, ball):
        if self.active and not ball.in_hole:
            if self.mouse_pressed:
                dx = self.end_pos[0] - ball.x
                dy = self.end_pos[1] - ball.y
                distance = math.hypot(dx, dy)
                angle = math.atan2(dy, dx)

                pygame.draw.line(screen, BLACK, (ball.x, ball.y), (self.end_pos[0], self.end_pos[1]), 5)
а
                pygame.draw.line(screen, WHITE, (ball.x, ball.y),
                                (ball.x - math.cos(angle) * distance * 2, ball.y - math.sin(angle) * distance * 2), 2)


    def draw_reflection(self, ball, angle):

        if ball.x - BALL_RADIUS < TABLE_OFFSET_X or ball.x + BALL_RADIUS > TABLE_OFFSET_X + TABLE_WIDTH:
            reflection_angle = math.pi - angle 
            pygame.draw.line(screen, RED, (ball.x, ball.y),
                            (ball.x + math.cos(reflection_angle) * 200, ball.y + math.sin(reflection_angle) * 200), 2)

        if ball.y - BALL_RADIUS < TABLE_OFFSET_Y or ball.y + BALL_RADIUS > TABLE_OFFSET_Y + TABLE_HEIGHT:
            reflection_angle = -angle  
            pygame.draw.line(screen, RED, (ball.x, ball.y),
                            (ball.x + math.cos(reflection_angle) * 200, ball.y + math.sin(reflection_angle) * 200), 2)

    def strike(self, ball):
        if not ball.in_hole:

            dx = self.end_pos[0] - ball.x
            dy = self.end_pos[1] - ball.y
            distance = math.hypot(dx, dy)
            self.power = min(distance / 50, 10) 

            self.angle = math.atan2(dy, dx)

            ball.speed_x = -math.cos(self.angle) * self.power * BALL_SPEED
            ball.speed_y = -math.sin(self.angle) * self.power * BALL_SPEED
            self.active = False
            self.power = 0


balls = [
    Ball(TABLE_OFFSET_X + 300, TABLE_OFFSET_Y + 300, WHITE)  # Белый шар
]


pyramid_positions = [
    (TABLE_OFFSET_X + 600, TABLE_OFFSET_Y + 300),  
    (TABLE_OFFSET_X + 630, TABLE_OFFSET_Y + 270),  
    (TABLE_OFFSET_X + 630, TABLE_OFFSET_Y + 330),
    (TABLE_OFFSET_X + 660, TABLE_OFFSET_Y + 240), 
    (TABLE_OFFSET_X + 660, TABLE_OFFSET_Y + 300),
    (TABLE_OFFSET_X + 660, TABLE_OFFSET_Y + 360),
    (TABLE_OFFSET_X + 690, TABLE_OFFSET_Y + 210),  
    (TABLE_OFFSET_X + 690, TABLE_OFFSET_Y + 270),
    (TABLE_OFFSET_X + 690, TABLE_OFFSET_Y + 330),
    (TABLE_OFFSET_X + 690, TABLE_OFFSET_Y + 390),
    (TABLE_OFFSET_X + 720, TABLE_OFFSET_Y + 180),  
    (TABLE_OFFSET_X + 720, TABLE_OFFSET_Y + 240),
    (TABLE_OFFSET_X + 720, TABLE_OFFSET_Y + 300),
    (TABLE_OFFSET_X + 720, TABLE_OFFSET_Y + 360),
    (TABLE_OFFSET_X + 720, TABLE_OFFSET_Y + 420)
]

for pos in pyramid_positions:
    balls.append(Ball(pos[0], pos[1], WHITE))  

# Лузы (отверстия)
holes = [
    (TABLE_OFFSET_X, TABLE_OFFSET_Y), 
    (TABLE_OFFSET_X + TABLE_WIDTH, TABLE_OFFSET_Y),
    (TABLE_OFFSET_X, TABLE_OFFSET_Y + TABLE_HEIGHT),  
    (TABLE_OFFSET_X + TABLE_WIDTH, TABLE_OFFSET_Y + TABLE_HEIGHT), 
    (TABLE_OFFSET_X + TABLE_WIDTH // 2, TABLE_OFFSET_Y), 
    (TABLE_OFFSET_X + TABLE_WIDTH // 2, TABLE_OFFSET_Y + TABLE_HEIGHT) 
]

cue = Cue()
selected_ball = balls[0]


player1_score = 0
player2_score = 0
current_player = 1 

clock = pygame.time.Clock()
running = True
while running:
    screen.fill(GREEN)


    pygame.draw.rect(screen, BLACK, (TABLE_OFFSET_X, TABLE_OFFSET_Y, TABLE_WIDTH, TABLE_HEIGHT), 5)


    for hole in holes:
        pygame.draw.circle(screen, BLACK, hole, HOLE_RADIUS)


    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1: 
                cue.mouse_pressed = True
                cue.start_pos = pygame.mouse.get_pos()
            elif event.button == 3: 
              
                mouse_x, mouse_y = event.pos
                for ball in balls:
                    if not ball.in_hole:
                        distance = math.hypot(ball.x - mouse_x, ball.y - mouse_y)
                        if distance <= BALL_RADIUS:
                            selected_ball = ball
                            cue.active = True
                            break
        elif event.type == pygame.MOUSEBUTTONUP:
            if event.button == 1: 
                if cue.mouse_pressed:
                    cue.end_pos = pygame.mouse.get_pos()
                    cue.strike(selected_ball)
                    cue.mouse_pressed = False

              
                    balls_moved = any(
                        math.hypot(ball.speed_x, ball.speed_y) > 0.1 for ball in balls if not ball.in_hole
                    )
                    if not balls_moved:
                
                        current_player = 3 - current_player  

    if cue.mouse_pressed:
        cue.end_pos = pygame.mouse.get_pos()

 
    for ball in balls:
        ball.move()
        ball.collide_with_walls()
        ball.check_hole_collision(holes)
        ball.draw()

 
    current_time = time.time()
    for ball in balls:
        if ball.in_hole and current_time - ball.hole_timer > 1:
            balls.remove(ball)
            if current_player == 1:
                player1_score += 1
            else:
                player2_score += 1


    for i in range(len(balls)):
        for j in range(i + 1, len(balls)):
            balls[i].collide_with_ball(balls[j])

 
    cue.draw(selected_ball)


    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Игрок 1: {player1_score}  Игрок 2: {player2_score}", True, BLACK)
    screen.blit(score_text, (10, 10))

    player_text = font.render(f"Ход: Игрок {current_player}", True, BLACK)
    screen.blit(player_text, (10, 50))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
