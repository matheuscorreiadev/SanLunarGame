import math
import random
import sys
from pathlib import Path

import pygame


BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"

WIDTH = 960
HEIGHT = 540
FPS = 60

BG = (9, 17, 31)
PANEL = (17, 28, 43)
WHITE = (246, 247, 251)
CYAN = (96, 239, 255)
YELLOW = (255, 209, 102)
PINK = (255, 143, 171)
GROUND = (38, 48, 61)


class SanLunarGame:
    def __init__(self, smoke_test=False):
        pygame.init()
        pygame.display.set_caption("San Lunar: Cristais da Mare")
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        self.clock = pygame.time.Clock()
        self.smoke_test = smoke_test
        self.running = True
        self.state = "menu"
        self.message = ""

        self.font_title = pygame.font.SysFont("segoeui", 56, bold=True)
        self.font_big = pygame.font.SysFont("segoeui", 34, bold=True)
        self.font_mid = pygame.font.SysFont("segoeui", 22, bold=True)
        self.font = pygame.font.SysFont("segoeui", 18)
        self.font_small = pygame.font.SysFont("segoeui", 15, bold=True)

        random.seed(18)
        self.stars = [
            (random.randrange(WIDTH), random.randrange(18, HEIGHT - 125), random.choice((1, 1, 2)))
            for _ in range(130)
        ]
        self.reset_game()

    def reset_game(self):
        self.player = pygame.Vector2(92, HEIGHT - 105)
        self.player_radius = 18
        self.hp = 3
        self.oxygen = 48.0
        self.collected = 0
        self.required_crystals = 6
        self.base_rect = pygame.Rect(805, HEIGHT - 130, 116, 72)
        self.crystals = [
            {"pos": pygame.Vector2(218, 398), "taken": False, "bob": 0.3},
            {"pos": pygame.Vector2(345, 302), "taken": False, "bob": 1.7},
            {"pos": pygame.Vector2(476, 418), "taken": False, "bob": 2.8},
            {"pos": pygame.Vector2(590, 246), "taken": False, "bob": 4.2},
            {"pos": pygame.Vector2(706, 377), "taken": False, "bob": 5.1},
            {"pos": pygame.Vector2(824, 184), "taken": False, "bob": 6.0},
        ]
        self.meteors = []
        for index in range(7):
            self.meteors.append(
                {
                    "pos": pygame.Vector2(170 + index * 112, -45 - index * 58),
                    "radius": random.randint(15, 25),
                    "speed": random.uniform(110, 175),
                    "drift": random.uniform(-38, 38),
                    "hit_cooldown": 0.0,
                }
            )

    def run(self):
        while self.running:
            dt = self.clock.tick(FPS) / 1000
            self.handle_events()
            if self.state == "playing":
                self.update(dt)
            self.draw()
            pygame.display.flip()
            if self.smoke_test:
                self.running = False
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if self.state == "menu" and event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    self.reset_game()
                    self.state = "playing"
                elif self.state in ("victory", "defeat") and event.key == pygame.K_r:
                    self.reset_game()
                    self.state = "playing"
                elif event.key == pygame.K_ESCAPE:
                    self.state = "menu"

    def update(self, dt):
        keys = pygame.key.get_pressed()
        direction = pygame.Vector2(0, 0)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            direction.x -= 1
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            direction.x += 1
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            direction.y -= 1
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            direction.y += 1

        if direction.length_squared() > 0:
            direction = direction.normalize()

        boost = 1.55 if keys[pygame.K_SPACE] else 1.0
        self.player += direction * 238 * boost * dt
        self.player.x = max(26, min(WIDTH - 26, self.player.x))
        self.player.y = max(78, min(HEIGHT - 44, self.player.y))

        self.oxygen -= dt
        if self.oxygen <= 0:
            self.end_game("defeat", "Derrota: o oxigenio acabou.")
            return

        self.update_meteors(dt)
        self.collect_crystals()
        self.check_victory()

    def update_meteors(self, dt):
        for meteor in self.meteors:
            meteor["pos"].y += meteor["speed"] * dt
            meteor["pos"].x += meteor["drift"] * dt
            meteor["hit_cooldown"] = max(0, meteor["hit_cooldown"] - dt)

            if meteor["pos"].x < 35 or meteor["pos"].x > WIDTH - 35:
                meteor["drift"] *= -1

            if meteor["pos"].y > HEIGHT + 45:
                self.respawn_meteor(meteor)

            distance = self.player.distance_to(meteor["pos"])
            if distance < self.player_radius + meteor["radius"] and meteor["hit_cooldown"] <= 0:
                self.hp -= 1
                meteor["hit_cooldown"] = 0.6
                self.respawn_meteor(meteor)
                if self.hp <= 0:
                    self.end_game("defeat", "Derrota: os meteoros destruiram o traje.")
                    return

    def respawn_meteor(self, meteor):
        meteor["pos"].x = random.uniform(78, WIDTH - 78)
        meteor["pos"].y = random.uniform(-180, -36)
        meteor["speed"] = random.uniform(110, 180)
        meteor["drift"] = random.uniform(-40, 40)

    def collect_crystals(self):
        for crystal in self.crystals:
            if crystal["taken"]:
                continue
            if self.player.distance_to(crystal["pos"]) < self.player_radius + 18:
                crystal["taken"] = True
                self.collected += 1

    def check_victory(self):
        if self.collected >= self.required_crystals and self.base_rect.collidepoint(self.player):
            self.end_game("victory", "Vitoria: cristais salvos no modulo lunar!")

    def end_game(self, state, message):
        self.state = state
        self.message = message

    def draw(self):
        self.draw_background()
        if self.state == "menu":
            self.draw_menu()
        else:
            self.draw_world()
            self.draw_hud()
            if self.state in ("victory", "defeat"):
                self.draw_end_overlay()

    def draw_background(self):
        self.screen.fill(BG)
        for x, y, size in self.stars:
            color = random.choice(((255, 255, 255), (168, 216, 255), (255, 209, 102), (155, 246, 255)))
            pygame.draw.circle(self.screen, color, (x, y), size)

        pygame.draw.circle(self.screen, (215, 232, 235), (720, 124), 70)
        pygame.draw.circle(self.screen, (169, 190, 199), (696, 96), 14)
        pygame.draw.circle(self.screen, (184, 203, 208), (748, 148), 15)
        pygame.draw.circle(self.screen, (167, 187, 197), (675, 165), 10)

    def draw_menu(self):
        self.draw_moon_floor()
        self.draw_base((775, 357))
        self.draw_player((162, 378), boost=False, scale=1.18)

        self.center_text("SAN LUNAR", self.font_title, (WIDTH // 2, 82), (246, 241, 213))
        self.center_text("Cristais da Mare", self.font_big, (WIDTH // 2, 138), CYAN)
        self.center_text(
            "Colete 6 cristais lunares e volte ao modulo antes que o oxigenio acabe.",
            self.font,
            (WIDTH // 2, 203),
            (217, 232, 255),
        )

        controls = [
            "Setas ou WASD - mover o explorador",
            "Space - propulsor rapido",
            "Enter - iniciar",
            "Esc - voltar ao menu",
            "R - reiniciar apos vencer/perder",
        ]
        for index, line in enumerate(controls):
            self.center_text(line, self.font, (WIDTH // 2, 270 + index * 30), WHITE)

        self.center_text("Pressione ENTER para jogar", self.font_mid, (WIDTH // 2, 462), YELLOW)

    def draw_world(self):
        self.draw_moon_floor()
        self.draw_base(self.base_rect.center)

        now = pygame.time.get_ticks() / 1000
        for crystal in self.crystals:
            if not crystal["taken"]:
                self.draw_crystal(crystal, now)

        for meteor in self.meteors:
            self.draw_meteor(meteor)

        keys = pygame.key.get_pressed()
        self.draw_player(self.player, boost=keys[pygame.K_SPACE])

    def draw_moon_floor(self):
        points = [
            (0, 444),
            (145, 420),
            (290, 452),
            (468, 430),
            (648, 462),
            (820, 426),
            (WIDTH, 448),
            (WIDTH, HEIGHT),
            (0, HEIGHT),
        ]
        pygame.draw.polygon(self.screen, GROUND, points)
        pygame.draw.lines(self.screen, (98, 112, 128), False, points[:7], 3)
        for x, y, rx, ry in [(86, 486, 25, 8), (288, 474, 16, 6), (542, 498, 32, 10), (734, 462, 20, 7), (880, 498, 28, 9)]:
            pygame.draw.ellipse(self.screen, (28, 37, 48), pygame.Rect(x - rx, y - ry, rx * 2, ry * 2))
            pygame.draw.ellipse(self.screen, (57, 71, 87), pygame.Rect(x - rx, y - ry, rx * 2, ry * 2), 2)

    def draw_base(self, center):
        x, y = center
        body = pygame.Rect(0, 0, 116, 64)
        body.center = (x, y)
        pygame.draw.rect(self.screen, (215, 228, 235), body, border_radius=7)
        pygame.draw.rect(self.screen, WHITE, body, 2, border_radius=7)
        top = pygame.Rect(0, 0, 72, 24)
        top.midbottom = body.midtop
        pygame.draw.rect(self.screen, (153, 186, 208), top, border_radius=5)
        pygame.draw.rect(self.screen, WHITE, top, 2, border_radius=5)
        pygame.draw.circle(self.screen, (12, 34, 53), body.center, 24)
        pygame.draw.circle(self.screen, CYAN, body.center, 24, 3)
        pygame.draw.line(self.screen, (215, 228, 235), body.bottomleft, (body.left - 22, body.bottom + 26), 5)
        pygame.draw.line(self.screen, (215, 228, 235), body.bottomright, (body.right + 22, body.bottom + 26), 5)
        self.center_text("MODULO", self.font_small, (x, y + 74), (234, 247, 255))

    def draw_crystal(self, crystal, now):
        pos = crystal["pos"]
        y = pos.y + math.sin(now * 4 + crystal["bob"]) * 5
        points = [(pos.x, y - 22), (pos.x + 16, y), (pos.x, y + 22), (pos.x - 16, y)]
        pygame.draw.polygon(self.screen, CYAN, points)
        pygame.draw.polygon(self.screen, WHITE, points, 2)
        pygame.draw.line(self.screen, (185, 251, 255), (pos.x, y - 18), (pos.x, y + 18), 2)

    def draw_meteor(self, meteor):
        pos = meteor["pos"]
        radius = meteor["radius"]
        pygame.draw.line(self.screen, (255, 123, 84), (pos.x - radius * 2, pos.y - radius * 2), (pos.x - 8, pos.y - 8), 6)
        pygame.draw.circle(self.screen, (140, 75, 50), pos, radius)
        pygame.draw.circle(self.screen, (255, 200, 87), pos, radius, 2)
        pygame.draw.circle(self.screen, (95, 51, 40), (int(pos.x - radius * 0.2), int(pos.y)), max(4, radius // 3))

    def draw_player(self, pos, boost=False, scale=1.0):
        x, y = int(pos[0]), int(pos[1])
        r = int(self.player_radius * scale)
        pygame.draw.circle(self.screen, WHITE, (x, y), r)
        pygame.draw.circle(self.screen, CYAN, (x, y), r, 3)
        visor = pygame.Rect(0, 0, int(r * 1.0), int(r * 0.55))
        visor.center = (x, y - int(r * 0.1))
        pygame.draw.ellipse(self.screen, (16, 38, 56), visor)
        pygame.draw.ellipse(self.screen, (184, 247, 255), visor, 2)
        pygame.draw.line(self.screen, WHITE, (x - r - 7, y + 3), (x - r - 22, y + 18), 5)
        pygame.draw.line(self.screen, WHITE, (x + r + 7, y + 3), (x + r + 22, y + 18), 5)
        pygame.draw.line(self.screen, WHITE, (x - 8, y + r - 2), (x - 18, y + r + 20), 5)
        pygame.draw.line(self.screen, WHITE, (x + 8, y + r - 2), (x + 18, y + r + 20), 5)
        if boost:
            pygame.draw.polygon(self.screen, YELLOW, [(x - 9, y + r + 16), (x + 9, y + r + 16), (x, y + r + 44)])

    def draw_hud(self):
        pygame.draw.rect(self.screen, PANEL, pygame.Rect(0, 0, WIDTH, 58))
        self.left_text(f"Cristais: {self.collected}/{self.required_crystals}", self.font_small, (28, 29), CYAN)
        self.left_text(f"Oxigenio: {max(0, int(self.oxygen))}s", self.font_small, (205, 29), (246, 241, 213))
        self.left_text(f"Vida: {self.hp}", self.font_small, (374, 29), PINK)
        hint = "Volte ao modulo!" if self.collected >= self.required_crystals else "Colete todos os cristais"
        self.left_text(hint, self.font_small, (670, 29), WHITE)

    def draw_end_overlay(self):
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        color = (10, 82, 63, 185) if self.state == "victory" else (90, 22, 36, 185)
        overlay.fill(color)
        self.screen.blit(overlay, (0, 0))

        box = pygame.Rect(230, 160, 500, 198)
        pygame.draw.rect(self.screen, (16, 24, 39), box, border_radius=8)
        pygame.draw.rect(self.screen, WHITE, box, 3, border_radius=8)
        title = "VITORIA" if self.state == "victory" else "DERROTA"
        self.center_text(title, self.font_big, (WIDTH // 2, 218), YELLOW)
        self.center_text(self.message, self.font, (WIDTH // 2, 272), WHITE)
        self.center_text("R - jogar novamente    Esc - menu", self.font, (WIDTH // 2, 320), CYAN)

    def center_text(self, text, font, center, color):
        surface = font.render(text, True, color)
        rect = surface.get_rect(center=center)
        self.screen.blit(surface, rect)

    def left_text(self, text, font, midleft, color):
        surface = font.render(text, True, color)
        rect = surface.get_rect(midleft=midleft)
        self.screen.blit(surface, rect)


if __name__ == "__main__":
    smoke = "--smoke-test" in sys.argv
    SanLunarGame(smoke_test=smoke).run()
