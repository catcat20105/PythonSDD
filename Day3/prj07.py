from __future__ import annotations

from enum import Enum, auto
from pathlib import Path
import colorsys
import json
import os
import random

import pygame


ASSET_DIR = Path(__file__).with_name('assets')


def default_high_score_path() -> Path:
    local_app_data = os.environ.get('LOCALAPPDATA')
    if local_app_data:
        base_path = Path(local_app_data)
    else:
        base_path = Path.home() / '.local' / 'share'
    return base_path / 'ChromeDinoStompRunner' / 'high_score.json'


# Window and frame settings
SCREEN_WIDTH = 960
SCREEN_HEIGHT = 360
FPS = 60
MAX_DT = 0.05

# World settings
GROUND_Y = 290
GROUND_LINE_WIDTH = 3
INITIAL_SCROLL_SPEED = 300.0
MAX_SCROLL_SPEED = 520.0
SPEED_INCREMENT = 35.0
DIFFICULTY_INTERVAL = 5.0
SCORE_PER_SECOND = 10.0

# Dinosaur physics
DINOSAUR_X = 120
DINOSAUR_WIDTH = 44
DINOSAUR_HEIGHT = 48
JUMP_VELOCITY = -780.0
GRAVITY = 1900.0

# Cactus patterns and limits
CACTUS_VARIANTS = (
    (18, 42),
    (24, 56),
    (30, 48),
)
CACTUS_PATTERNS = (
    (0,),
    (0, 1),
    (0, 0, 1),
)
CACTUS_PATTERN_GAP = 8
CACTUS_CLUSTER_GAP = 32
CACTUS_SPAWN_OFFSET = 120
CACTUS_SPAWN_GAP = 180
CACTUS_BOUNCE_SPEED = 125.0
CACTUS_SECOND_BOUNCE_SPEED = 155.0
MIN_ACTIVE_CACTI = 8
MAX_ACTIVE_CACTI = 12

# Flying enemy and attack settings
FLYING_ENEMY_WIDTH = 46
FLYING_ENEMY_HEIGHT = 26
ENEMY_STOMP_MARGIN = 10
FLYING_ENEMY_LEVELS = (190, 145, 210)
MAX_ACTIVE_ENEMIES = 2
ENEMY_SPAWN_INTERVAL = 3.4
PUNCH_WIDTH = 90
PUNCH_HEIGHT = 42
PUNCH_OFFSET = 2
PUNCH_DURATION = 0.12
PUNCH_COOLDOWN = 5.0
CACTUS_SWEEP_SECONDS = 5.0
ENEMY_STUN_SECONDS = 0.5

# Ability settings
HELPER_SECONDS = 5.0
HELPER_COOLDOWN = 30.0
RAINBOW_SECONDS = 15.0
RAINBOW_COOLDOWN = 60.0
RAINBOW_HUE_SPEED = 0.7
DIG_EXIT_DISTANCE = SCREEN_HEIGHT - (GROUND_Y - DINOSAUR_HEIGHT)
DIG_SPEED = 260.0
DIG_TAP_DISTANCE = 18.0
DIG_SECONDS_TO_INVERT = DIG_EXIT_DISTANCE / DIG_SPEED
DIG_TAP_AMOUNT = DIG_TAP_DISTANCE / DIG_EXIT_DISTANCE

# Easter egg settings
GROUND_COMBO_HOLD_SECONDS = 0.10
GROUND_COMBO_COOLDOWN = 15.0
COMBO_TARGET_COUNT = 3  # Maximum targets per grounded combo.
COMBO_REACH = 320

# Score values
STOMP_BONUS = 50
PUNCH_BONUS = 100
COMBO_BONUS = 150
REVIVE_COST = 500
DEATH_SCREEN_DELAY = 0.5

# Colors
SKY_COLOR = (247, 250, 252)
BLACK = (0, 0, 0)
GROUND_COLOR = (55, 62, 70)
DINO_COLOR = (0, 0, 0)
DINO_STUNNED_COLOR = (0, 0, 0)
CACTUS_COLOR = (42, 126, 72)
CACTUS_DARK_COLOR = (28, 91, 52)
ENEMY_COLOR = (121, 74, 157)
ENEMY_WING_COLOR = (157, 98, 189)
PUNCH_COLOR = (232, 156, 44)
TEXT_COLOR = (42, 47, 52)
MUTED_TEXT_COLOR = (95, 103, 111)
BONUS_COLOR = (190, 106, 31)
DANGER_COLOR = (184, 56, 56)
WHITE = (255, 255, 255)


def hsv_color(hue: float, saturation: float = 1.0, value: float = 1.0) -> tuple[int, int, int]:
    red, green, blue = colorsys.hsv_to_rgb(
        hue % 1.0,
        max(0.0, min(1.0, saturation)),
        max(0.0, min(1.0, value)),
    )
    return (
        round(red * 255),
        round(green * 255),
        round(blue * 255),
    )


def invert_color(color: tuple[int, int, int]) -> tuple[int, int, int]:
    return tuple(255 - channel for channel in color)


class GameState(Enum):
    READY = auto()
    RUNNING = auto()
    GAME_OVER = auto()


class Dinosaur:
    def __init__(
        self,
        x: int = DINOSAUR_X,
        ground_y: int = GROUND_Y,
        width: int = DINOSAUR_WIDTH,
        height: int = DINOSAUR_HEIGHT,
    ):
        self.start_x = x
        self.ground_y = ground_y
        self.width = width
        self.height = height
        self.rect = pygame.Rect(x, ground_y - height, width, height)
        self.position_y = float(self.rect.top)
        self.velocity_y = 0.0
        self.is_grounded = True
        self.previous_bottom = float(self.rect.bottom)
        self.previous_velocity_y = 0.0

    @property
    def current_bottom(self) -> float:
        return self.position_y + self.height

    def reset(self) -> None:
        self.position_y = float(self.ground_y - self.height)
        self.rect.topleft = (self.start_x, round(self.position_y))
        self.velocity_y = 0.0
        self.is_grounded = True
        self.previous_bottom = self.current_bottom
        self.previous_velocity_y = 0.0

    def jump(self) -> bool:
        if not self.is_grounded:
            return False
        self.velocity_y = JUMP_VELOCITY
        self.is_grounded = False
        return True

    def update(self, dt: float) -> None:
        self.previous_bottom = self.current_bottom
        self.previous_velocity_y = self.velocity_y

        if self.is_grounded:
            self.position_y = float(self.ground_y - self.height)
            self.rect.top = round(self.position_y)
            return

        self.velocity_y += GRAVITY * dt
        self.position_y += self.velocity_y * dt

        if self.current_bottom >= self.ground_y:
            self.position_y = float(self.ground_y - self.height)
            self.velocity_y = 0.0
            self.is_grounded = True

        self.rect.top = round(self.position_y)

    def land_after_stomp(self, cactus_top: int) -> None:
        self.position_y = float(cactus_top - self.height)
        self.rect.top = round(self.position_y)
        self.velocity_y = max(self.velocity_y, 90.0)
        self.is_grounded = False

    def draw(
        self,
        surface: pygame.Surface,
        stunned: bool = False,
        sprite: pygame.Surface | None = None,
        inverted: bool = False,
        visual_offset: int = 0,
    ) -> None:
        display_rect = self.rect.move(0, int(visual_offset))
        if sprite is not None:
            surface.blit(sprite, display_rect)
            return

        if inverted:
            color = WHITE
            eye_color = BLACK
        else:
            color = DINO_STUNNED_COLOR if stunned else DINO_COLOR
            eye_color = WHITE

        left = display_rect.left
        top = display_rect.top

        body = pygame.Rect(left + 6, top + 15, 27, 26)
        head = pygame.Rect(left + 24, top + 4, 17, 19)
        neck = pygame.Rect(left + 22, top + 11, 12, 15)
        tail = [
            (left + 8, top + 20),
            (left - 3, top + 28),
            (left + 8, top + 30),
        ]
        pygame.draw.rect(surface, color, body)
        pygame.draw.rect(surface, color, neck)
        pygame.draw.rect(surface, color, head)
        pygame.draw.polygon(surface, color, tail)

        leg_y = top + 39
        pygame.draw.rect(surface, color, pygame.Rect(left + 10, leg_y, 7, 9))
        pygame.draw.rect(surface, color, pygame.Rect(left + 27, leg_y, 7, 9))
        pygame.draw.rect(surface, color, pygame.Rect(left + 8, top + 46, 12, 3))
        pygame.draw.rect(surface, color, pygame.Rect(left + 25, top + 46, 12, 3))

        eye = pygame.Rect(left + 35, top + 8, 3, 3)
        pygame.draw.rect(surface, eye_color, eye)


class Cactus:
    def __init__(self, x: float, variant_index: int = 0):
        self.variant_index = variant_index % len(CACTUS_VARIANTS)
        width, height = CACTUS_VARIANTS[self.variant_index]
        self.position_x = float(x)
        self.rect = pygame.Rect(round(self.position_x), GROUND_Y - height, width, height)

    def move_by(self, distance: float) -> None:
        self.position_x += distance
        self.rect.x = round(self.position_x)

    def draw(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int] | None = None,
        dark_color: tuple[int, int, int] | None = None,
    ) -> None:
        main_color = CACTUS_COLOR if color is None else color
        shadow_color = CACTUS_DARK_COLOR if dark_color is None else dark_color
        pygame.draw.rect(surface, main_color, self.rect)

        arm_width = max(4, self.rect.width // 4)
        arm_height = max(9, self.rect.height // 4)
        arm_y = self.rect.top + self.rect.height // 2
        left_arm = pygame.Rect(
            self.rect.left - arm_width + 2,
            arm_y,
            arm_width,
            arm_height,
        )
        right_arm = pygame.Rect(
            self.rect.right - 2,
            arm_y - arm_height // 2,
            arm_width,
            arm_height,
        )
        pygame.draw.rect(surface, shadow_color, left_arm)
        pygame.draw.rect(surface, shadow_color, right_arm)
        pygame.draw.rect(
            surface,
            shadow_color,
            pygame.Rect(
                self.rect.left + self.rect.width // 3,
                self.rect.top + 5,
                max(3, self.rect.width // 6),
                max(8, self.rect.height - 10),
            ),
        )


class CactusCluster:
    """Cacti that share direction so a small group stays together."""

    def __init__(
        self,
        x: float,
        variant_indices: tuple[int, ...] = (0,),
        gap: int = CACTUS_PATTERN_GAP,
        direction: int = -1,
    ):
        if not variant_indices:
            raise ValueError("A cactus cluster must contain at least one cactus.")

        self.cacti: list[Cactus] = []
        self.gap = gap
        self.direction = -1 if direction < 0 else 1
        self.has_bounced = False
        self.bounce_count = 0

        next_x = float(x)
        for variant_index in variant_indices:
            cactus = Cactus(next_x, variant_index)
            self.cacti.append(cactus)
            next_x += cactus.rect.width + gap

    @property
    def is_active(self) -> bool:
        return bool(self.cacti)

    @property
    def left(self) -> int:
        return min(cactus.rect.left for cactus in self.cacti)

    @property
    def right(self) -> int:
        return max(cactus.rect.right for cactus in self.cacti)

    def update(self, dt: float, scroll_speed: float) -> None:
        if not self.cacti:
            return

        if self.bounce_count == 0 and not self.has_bounced:
            speed = scroll_speed
        elif self.bounce_count <= 1:
            speed = CACTUS_BOUNCE_SPEED
        else:
            speed = CACTUS_SECOND_BOUNCE_SPEED
        distance = self.direction * speed * dt
        for cactus in self.cacti:
            cactus.move_by(distance)

        if self.direction < 0 and self.left <= 0:
            self._move_by(-self.left)
            self.direction = 1
            self.has_bounced = True
            self.bounce_count += 1
        elif self.direction > 0 and self.right >= SCREEN_WIDTH:
            self._move_by(SCREEN_WIDTH - self.right)
            self.direction = -1
            self.has_bounced = True
            self.bounce_count += 1

    def _move_by(self, distance: float) -> None:
        for cactus in self.cacti:
            cactus.move_by(distance)

    def remove(self, cactus: Cactus) -> bool:
        if cactus not in self.cacti:
            return False
        self.cacti.remove(cactus)
        return True

    def draw(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int] | None = None,
        dark_color: tuple[int, int, int] | None = None,
    ) -> None:
        for cactus in self.cacti:
            cactus.draw(surface, color, dark_color)


class FlyingEnemy:
    def __init__(
        self,
        x: float,
        y: int,
        height_index: int = 0,
    ):
        self.position_x = float(x)
        self.flight_y = y
        self.height_index = height_index
        self.rect = pygame.Rect(
            round(self.position_x),
            y,
            FLYING_ENEMY_WIDTH,
            FLYING_ENEMY_HEIGHT,
        )
        self.contact_handled = False
        self.is_sweeper = False
        self.is_ridden = False
        self.is_helper = False

    def update(self, dt: float, scroll_speed: float) -> None:
        if not self.is_ridden and not self.is_helper:
            self.position_x -= scroll_speed * dt
            self.rect.x = round(self.position_x)
        if self.is_sweeper or self.is_helper:
            self.rect.top = GROUND_Y - FLYING_ENEMY_HEIGHT

    def activate_cactus_sweep(
        self,
        rider_rect: pygame.Rect | None = None,
    ) -> None:
        self.is_sweeper = True
        self.is_ridden = True
        self.contact_handled = True
        self.rect.top = GROUND_Y - FLYING_ENEMY_HEIGHT
        if rider_rect is not None:
            self.rect.centerx = rider_rect.centerx
            self.position_x = float(self.rect.left)

    def activate_helper(self, anchor_rect: pygame.Rect) -> None:
        self.is_helper = True
        self.contact_handled = True
        self.rect.top = GROUND_Y - FLYING_ENEMY_HEIGHT
        self.rect.centerx = anchor_rect.centerx
        self.position_x = float(self.rect.left)

    def release_rider(self) -> None:
        self.is_sweeper = False
        self.is_ridden = False
        self.rect.top = self.flight_y

    def release_helper(self) -> None:
        self.is_helper = False
        self.rect.top = self.flight_y

    def is_off_screen(self) -> bool:
        return self.rect.right <= 0

    def draw(
        self,
        surface: pygame.Surface,
        body_color: tuple[int, int, int] | None = None,
        wing_color: tuple[int, int, int] | None = None,
        eye_color: tuple[int, int, int] | None = None,
    ) -> None:
        body_main = ENEMY_COLOR if body_color is None else body_color
        wing_main = ENEMY_WING_COLOR if wing_color is None else wing_color
        eye_main = WHITE if eye_color is None else eye_color
        left = self.rect.left
        top = self.rect.top
        body = pygame.Rect(left + 9, top + 8, 28, 12)
        left_wing = [
            (left + 15, top + 11),
            (left + 1, top + 1),
            (left + 7, top + 17),
        ]
        right_wing = [
            (left + 31, top + 11),
            (left + 45, top + 1),
            (left + 39, top + 17),
        ]
        pygame.draw.polygon(surface, wing_main, left_wing)
        pygame.draw.polygon(surface, wing_main, right_wing)
        pygame.draw.ellipse(surface, body_main, body)
        pygame.draw.polygon(
            surface,
            body_main,
            [(left + 36, top + 9), (left + 46, top + 13), (left + 36, top + 16)],
        )
        pygame.draw.rect(surface, eye_main, pygame.Rect(left + 31, top + 10, 3, 3))


class PunchHitbox:
    """The short-lived forward area created by one airborne E press."""

    def __init__(self, dinosaur_rect: pygame.Rect):
        self.rect = pygame.Rect(
            dinosaur_rect.right + PUNCH_OFFSET,
            dinosaur_rect.centery - PUNCH_HEIGHT // 2,
            PUNCH_WIDTH,
            PUNCH_HEIGHT,
        )
        self.remaining_seconds = PUNCH_DURATION
        self.has_hit = False

    @property
    def is_active(self) -> bool:
        return self.remaining_seconds > 0

    def update(self, dinosaur_rect: pygame.Rect, dt: float) -> None:
        self.remaining_seconds -= dt
        self.rect.left = dinosaur_rect.right + PUNCH_OFFSET
        self.rect.centery = dinosaur_rect.centery

    def draw(
        self,
        surface: pygame.Surface,
        color: tuple[int, int, int] | None = None,
    ) -> None:
        if not self.is_active:
            return
        punch_color = PUNCH_COLOR if color is None else color
        pygame.draw.rect(surface, punch_color, self.rect, width=2)
        fist = pygame.Rect(self.rect.left + 7, self.rect.centery - 5, 12, 10)
        pygame.draw.rect(surface, punch_color, fist)


class GameSession:
    """Owns one complete run and all transient gameplay state."""

    def __init__(
        self,
        seed: int | None = None,
        high_score_path: str | Path | None = None,
        persist_high_score: bool = True,
    ):
        self.dinosaur = Dinosaur()
        self.spawning_enabled = True
        self.world_speed_override: float | None = None
        self.random_seed = seed
        self.rng = random.Random(seed)
        self.persist_high_score = persist_high_score
        self.high_score_path = (
            Path(high_score_path)
            if high_score_path is not None
            else default_high_score_path()
        )
        self.high_score = self._load_high_score()
        self.reset()

    @property
    def cacti(self) -> list[Cactus]:
        return [
            cactus
            for cluster in self.cactus_clusters
            for cactus in cluster.cacti
        ]

    @property
    def score(self) -> int:
        return self.survival_score + self.bonus_score

    @property
    def is_stunned(self) -> bool:
        return self.stun_remaining > 0

    def reset(self) -> None:
        self.state = GameState.READY
        self.dinosaur.reset()
        self.world_speed_override = None
        self.cactus_clusters: list[CactusCluster] = []
        self.flying_enemies: list[FlyingEnemy] = []
        self.punch_hitbox: PunchHitbox | None = None
        self.riding_enemy: FlyingEnemy | None = None
        self.helper_enemy: FlyingEnemy | None = None

        self.elapsed_seconds = 0.0
        self.survival_score = 0
        self.bonus_score = 0
        self.scroll_speed = INITIAL_SCROLL_SPEED
        self.death_overlay_delay_remaining = 0.0

        self.stun_remaining = 0.0
        self.cactus_sweep_remaining = 0.0
        self.helper_remaining = 0.0
        self.helper_cooldown = 0.0
        self.rainbow_remaining = 0.0
        self.rainbow_cooldown = 0.0
        self.rainbow_elapsed = 0.0
        self.dig_progress = 0.0
        self.dig_target_inverted = False
        self.is_digging = False
        self.is_inverted = False
        self.just_entered_inverted = False
        self.punch_cooldown = 0.0
        self.combo_cooldown = 0.0
        self.combo_hold_elapsed = 0.0
        self.combo_attempt_pending = False
        self.e_is_held = False
        self.w_is_held = False
        self.r_is_held = False
        self.d_is_held = False
        self.dig_toggle_blocked = False

        self.rng = random.Random(self.random_seed)
        self.next_enemy_height_index = 0
        self.enemy_spawn_elapsed = 0.0

        self.last_notification = ""
        self.notification_seconds = 0.0
        self.notification_color = BONUS_COLOR

        self._stage_initial_cacti()

    def start(self) -> bool:
        if self.state != GameState.READY:
            return False
        self.state = GameState.RUNNING
        return True

    def restart(
        self,
        auto_jump: bool = False,
        carried_score: int = 0,
    ) -> None:
        self.reset()
        self.bonus_score = max(0, int(carried_score))
        self.start()
        if auto_jump:
            self.dinosaur.jump()

    def request_jump(self) -> bool:
        if self.state == GameState.READY:
            self.start()
        if (
            self.state != GameState.RUNNING
            or self.is_stunned
            or self.is_digging
        ):
            return False
        if self.riding_enemy is not None:
            return self._jump_from_ride()
        return self.dinosaur.jump()

    def request_punch(self) -> bool:
        if (
            self.state != GameState.RUNNING
            or self.is_stunned
            or self.dinosaur.is_grounded
            or self.punch_cooldown > 0
        ):
            return False

        self.punch_hitbox = PunchHitbox(self.dinosaur.rect)
        self.punch_cooldown = PUNCH_COOLDOWN
        return True

    def request_rainbow(self) -> bool:
        if (
            self.state != GameState.RUNNING
            or self.rainbow_cooldown > 0
        ):
            return False

        self.rainbow_remaining = RAINBOW_SECONDS
        self.rainbow_cooldown = RAINBOW_COOLDOWN
        self.rainbow_elapsed = 0.0
        self._notify('RAINBOW', BONUS_COLOR)
        return True

    def request_helper(self) -> bool:
        if (
            self.state != GameState.RUNNING
            or self.helper_cooldown > 0
            or self.helper_enemy is not None
        ):
            return False

        anchor = self.dinosaur.rect.move(80, 0)
        helper = FlyingEnemy(
            anchor.centerx,
            FLYING_ENEMY_LEVELS[0],
            0,
        )
        helper.activate_helper(anchor)
        self.flying_enemies.append(helper)
        self.helper_enemy = helper
        self.helper_remaining = HELPER_SECONDS
        self.helper_cooldown = HELPER_COOLDOWN
        self._notify('HELPER PTERODACTYL', BONUS_COLOR)
        return True

    def request_dig(self) -> bool:
        if (
            self.state != GameState.RUNNING
            or self.riding_enemy is not None
            or not self.dinosaur.is_grounded
            or self.dig_toggle_blocked
        ):
            return False

        self.is_digging = True
        self.dig_target_inverted = not self.is_inverted
        self.dig_toggle_blocked = True
        self.dinosaur.is_grounded = False
        self.dinosaur.velocity_y = 0.0
        self._advance_dig(DIG_TAP_DISTANCE)
        return True

    def handle_key_down(self, key: int) -> bool:
        if key in (pygame.K_SPACE, pygame.K_UP):
            if self.state == GameState.GAME_OVER:
                can_revive = self.score >= REVIVE_COST
                carried_score = (
                    self.score - REVIVE_COST
                    if can_revive
                    else 0
                )
                self.restart(
                    auto_jump=True,
                    carried_score=carried_score,
                )
                if can_revive:
                    self._notify('REVIVE -500', BONUS_COLOR)
                return True
            return self.request_jump()

        if key == pygame.K_r:
            if self.state == GameState.GAME_OVER:
                self.restart(auto_jump=False)
                return True
            if self.state != GameState.RUNNING or self.r_is_held:
                return False
            self.r_is_held = True
            return self.request_helper()

        if key == pygame.K_w:
            if self.state != GameState.RUNNING or self.w_is_held:
                return False
            self.w_is_held = True
            return self.request_rainbow()

        if key == pygame.K_d:
            if self.state != GameState.RUNNING or self.d_is_held:
                return False
            self.d_is_held = True
            return self.request_dig()

        if key != pygame.K_e or self.state != GameState.RUNNING:
            return False

        if self.e_is_held:
            return False

        self.e_is_held = True
        if self.is_stunned:
            return False

        if self.dinosaur.is_grounded:
            if self.combo_cooldown <= 0:
                self.combo_attempt_pending = True
                self.combo_hold_elapsed = 0.0
            return False

        return self.request_punch()

    def handle_key_up(self, key: int) -> None:
        if key == pygame.K_e:
            self.e_is_held = False
            self.combo_attempt_pending = False
            self.combo_hold_elapsed = 0.0
        elif key == pygame.K_w:
            self.w_is_held = False
        elif key == pygame.K_r:
            self.r_is_held = False
        elif key == pygame.K_d:
            self.d_is_held = False
            self.dig_toggle_blocked = False

    def find_combo_targets(self) -> list[Cactus]:
        front_edge = self.dinosaur.rect.right
        reach_edge = front_edge + COMBO_REACH
        candidates = sorted(
            (
                cactus
                for cactus in self.cacti
                if cactus.rect.left >= front_edge
                and cactus.rect.left <= reach_edge
            ),
            key=lambda cactus: cactus.rect.left,
        )
        return candidates[:COMBO_TARGET_COUNT]

    def update(self, dt: float) -> None:
        dt = max(0.0, min(float(dt), MAX_DT))

        if self.state == GameState.GAME_OVER:
            if self.death_overlay_delay_remaining - dt <= 1e-9:
                self.death_overlay_delay_remaining = 0.0
            else:
                self.death_overlay_delay_remaining -= dt
            return

        if self.state != GameState.RUNNING:
            return

        self._update_timers(dt)
        if self.helper_enemy is not None and self.helper_remaining <= 0:
            self._end_helper()
        if self.riding_enemy is not None and self.cactus_sweep_remaining <= 0:
            self._end_cactus_ride()
        self._update_dig(dt)

        self.elapsed_seconds += dt
        self.survival_score = int(self.elapsed_seconds * SCORE_PER_SECOND)
        difficulty_steps = int(self.elapsed_seconds // DIFFICULTY_INTERVAL)
        calculated_speed = min(
            INITIAL_SCROLL_SPEED + difficulty_steps * SPEED_INCREMENT,
            MAX_SCROLL_SPEED,
        )
        if self.world_speed_override is None:
            self.scroll_speed = calculated_speed
        else:
            self.scroll_speed = self.world_speed_override

        if self.is_digging:
            self.dinosaur.previous_bottom = self.dinosaur.current_bottom
            self.dinosaur.previous_velocity_y = 0.0
        else:
            self.dinosaur.update(dt)
        for cluster in self.cactus_clusters:
            cluster.update(dt, self.scroll_speed)
        for enemy in self.flying_enemies:
            enemy.update(dt, self.scroll_speed)
        self._sync_dinosaur_to_cactus_ride()

        if self.punch_hitbox is not None:
            self.punch_hitbox.update(self.dinosaur.rect, dt)
            if not self.punch_hitbox.is_active:
                self.punch_hitbox = None

        self._update_ground_combo(dt)
        self._resolve_punch_hits()
        self._resolve_stomps()
        self._resolve_enemy_stomps()
        self._resolve_riding_cactus_contacts()
        self._resolve_helper_contacts()
        self._resolve_enemy_contacts()
        self._resolve_fatal_cactus_collision()
        self._record_high_score()

        if self.state != GameState.RUNNING:
            self.just_entered_inverted = False
            return

        self.flying_enemies = [
            enemy
            for enemy in self.flying_enemies
            if not enemy.is_off_screen()
        ]
        self._update_spawning(dt)
        self._replenish_cacti()
        self._record_high_score()
        self.just_entered_inverted = False

    def _load_high_score(self) -> int:
        if not self.persist_high_score:
            return 0
        try:
            payload = json.loads(
                self.high_score_path.read_text(encoding='utf-8')
            )
            return max(0, int(payload.get('high_score', 0)))
        except (OSError, TypeError, ValueError, AttributeError):
            return 0

    def _save_high_score(self) -> None:
        if not self.persist_high_score:
            return
        try:
            self.high_score_path.parent.mkdir(parents=True, exist_ok=True)
            temporary_path = self.high_score_path.with_suffix(
                self.high_score_path.suffix + '.tmp'
            )
            temporary_path.write_text(
                json.dumps({'high_score': self.high_score}),
                encoding='utf-8',
            )
            temporary_path.replace(self.high_score_path)
        except OSError:
            pass

    def _record_high_score(self) -> None:
        if self.score <= self.high_score:
            return
        self.high_score = self.score
        self._save_high_score()

    def _update_timers(self, dt: float) -> None:
        if self.rainbow_remaining > 0:
            self.rainbow_elapsed += dt
        self.stun_remaining = max(0.0, self.stun_remaining - dt)
        self.cactus_sweep_remaining = max(
            0.0, self.cactus_sweep_remaining - dt
        )
        self.helper_remaining = max(0.0, self.helper_remaining - dt)
        self.helper_cooldown = max(0.0, self.helper_cooldown - dt)
        self.rainbow_remaining = max(0.0, self.rainbow_remaining - dt)
        self.rainbow_cooldown = max(0.0, self.rainbow_cooldown - dt)
        self.punch_cooldown = max(0.0, self.punch_cooldown - dt)
        self.combo_cooldown = max(0.0, self.combo_cooldown - dt)
        self.notification_seconds = max(0.0, self.notification_seconds - dt)

    def _complete_dig(self) -> None:
        target_inverted = self.dig_target_inverted
        self.is_digging = False
        self.is_inverted = target_inverted
        self.dig_progress = 1.0 if target_inverted else 0.0
        self.dinosaur.reset()
        # Protect the reset-to-ground transition from collision for one frame.
        self.just_entered_inverted = True
        self._notify(
            'INVERTED UNIVERSE' if target_inverted else 'NORMAL UNIVERSE',
            BONUS_COLOR,
        )

    def _enter_inverted(self) -> None:
        if self.is_inverted:
            return
        self.dig_target_inverted = True
        self._complete_dig()

    def _advance_dig(self, distance: float) -> None:
        if not self.is_digging:
            return

        dinosaur = self.dinosaur
        dinosaur.previous_bottom = dinosaur.current_bottom
        dinosaur.previous_velocity_y = 0.0
        dinosaur.position_y += max(0.0, distance)
        dinosaur.rect.top = round(dinosaur.position_y)
        dinosaur.is_grounded = False
        start_top = dinosaur.ground_y - dinosaur.height
        self.dig_progress = min(
            1.0,
            max(0.0, (dinosaur.position_y - start_top) / DIG_EXIT_DISTANCE),
        )
        if dinosaur.rect.top >= SCREEN_HEIGHT:
            self._complete_dig()

    def _update_dig(self, dt: float) -> None:
        if not self.d_is_held or not self.is_digging:
            return
        self._advance_dig(DIG_SPEED * dt)

    def _update_ground_combo(self, dt: float) -> None:
        if not self.combo_attempt_pending:
            return

        if (
            not self.e_is_held
            or not self.dinosaur.is_grounded
            or self.is_stunned
            or self.combo_cooldown > 0
        ):
            self.combo_attempt_pending = False
            self.combo_hold_elapsed = 0.0
            return

        self.combo_hold_elapsed += dt
        if self.combo_hold_elapsed < GROUND_COMBO_HOLD_SECONDS:
            return

        self.combo_attempt_pending = False
        self.combo_hold_elapsed = 0.0
        self.combo_cooldown = GROUND_COMBO_COOLDOWN

        targets = self.find_combo_targets()
        if not targets:
            self._notify('COMBO MISSED', DANGER_COLOR)
            return

        for cactus in targets:
            self._remove_cactus(cactus)
        self.bonus_score += STOMP_BONUS * len(targets)
        self._notify(f'COMBO x{len(targets)}', BONUS_COLOR)

    def _resolve_helper_contacts(self) -> None:
        helper = self.helper_enemy
        if helper is None or helper not in self.flying_enemies:
            return

        for cactus in list(self.cacti):
            if helper.rect.colliderect(cactus.rect):
                self._remove_cactus(cactus)

        for enemy in list(self.flying_enemies):
            if (
                enemy is helper
                or enemy is self.riding_enemy
                or enemy.is_helper
            ):
                continue
            if helper.rect.colliderect(enemy.rect):
                self.flying_enemies.remove(enemy)

    def _resolve_punch_hits(self) -> None:
        if self.punch_hitbox is None or self.punch_hitbox.has_hit:
            return

        for enemy in list(self.flying_enemies):
            if enemy is self.riding_enemy or enemy.is_helper:
                continue
            if self.punch_hitbox.rect.colliderect(enemy.rect):
                self.flying_enemies.remove(enemy)
                self.punch_hitbox.has_hit = True
                self.punch_hitbox = None
                self.bonus_score += PUNCH_BONUS
                self._notify("+100 PUNCH", BONUS_COLOR)
                return

    def _resolve_stomps(self) -> None:
        if self.is_digging:
            return

        dinosaur = self.dinosaur

        for cactus in sorted(self.cacti, key=lambda item: item.rect.left):
            horizontal_overlap = (
                dinosaur.rect.right > cactus.rect.left
                and dinosaur.rect.left < cactus.rect.right
            )
            crossed_top = (
                dinosaur.previous_bottom <= cactus.rect.top
                and dinosaur.current_bottom >= cactus.rect.top
            )
            bottom_side_touch = abs(
                dinosaur.current_bottom - cactus.rect.top
            ) <= 1.0
            if not horizontal_overlap or not (crossed_top or bottom_side_touch):
                continue

            self._remove_cactus(cactus)
            dinosaur.land_after_stomp(cactus.rect.top)
            self.bonus_score += STOMP_BONUS
            self._notify('+50 STOMP', BONUS_COLOR)
            return

    def _resolve_enemy_stomps(self) -> None:
        if self.riding_enemy is not None or self.is_digging:
            return

        dinosaur = self.dinosaur
        for enemy in self.flying_enemies:
            if enemy.is_sweeper or enemy.is_helper:
                continue
            horizontal_overlap = (
                dinosaur.rect.right > enemy.rect.left - ENEMY_STOMP_MARGIN
                and dinosaur.rect.left < enemy.rect.right + ENEMY_STOMP_MARGIN
            )
            crossed_top = (
                dinosaur.previous_bottom <= enemy.rect.top
                and dinosaur.current_bottom >= enemy.rect.top
            )
            bottom_side_touch = abs(
                dinosaur.current_bottom - enemy.rect.top
            ) <= 1.0
            if not horizontal_overlap or not (crossed_top or bottom_side_touch):
                continue

            enemy.activate_cactus_sweep(dinosaur.rect)
            self.riding_enemy = enemy
            self.cactus_sweep_remaining = CACTUS_SWEEP_SECONDS
            self._sync_dinosaur_to_cactus_ride()
            self._notify('RIDING PTERODACTYL', BONUS_COLOR)
            return

    def _sync_dinosaur_to_cactus_ride(self) -> None:
        enemy = self.riding_enemy
        if enemy is None or enemy not in self.flying_enemies:
            return

        dinosaur = self.dinosaur
        dinosaur.rect.centerx = enemy.rect.centerx
        dinosaur.position_y = float(enemy.rect.top - dinosaur.height)
        dinosaur.rect.top = round(dinosaur.position_y)
        dinosaur.velocity_y = 0.0
        dinosaur.is_grounded = False
        dinosaur.previous_bottom = dinosaur.current_bottom
        dinosaur.previous_velocity_y = 0.0

    def _jump_from_ride(self) -> bool:
        enemy = self.riding_enemy
        if enemy is None:
            return self.dinosaur.jump()

        self.riding_enemy = None
        self.cactus_sweep_remaining = 0.0
        if enemy in self.flying_enemies:
            self.flying_enemies.remove(enemy)
        enemy.release_rider()

        dinosaur = self.dinosaur
        dinosaur.is_grounded = True
        dinosaur.velocity_y = 0.0
        dinosaur.previous_bottom = dinosaur.current_bottom
        dinosaur.previous_velocity_y = 0.0
        return dinosaur.jump()

    def _end_cactus_ride(self) -> None:
        enemy = self.riding_enemy
        self.riding_enemy = None
        if enemy is not None:
            enemy.release_rider()

        dinosaur = self.dinosaur
        dinosaur.rect.left = dinosaur.start_x
        dinosaur.position_y = float(dinosaur.rect.top)
        dinosaur.velocity_y = 90.0
        dinosaur.is_grounded = False
        dinosaur.previous_bottom = dinosaur.current_bottom
        dinosaur.previous_velocity_y = dinosaur.velocity_y

    def _end_helper(self) -> None:
        helper = self.helper_enemy
        self.helper_enemy = None
        if helper is None:
            return
        if helper in self.flying_enemies:
            self.flying_enemies.remove(helper)
        helper.release_helper()

    def _resolve_riding_cactus_contacts(self) -> None:
        enemy = self.riding_enemy
        if enemy is None or enemy not in self.flying_enemies:
            return

        for cactus in list(self.cacti):
            if enemy.rect.colliderect(cactus.rect):
                self._remove_cactus(cactus)

    def _resolve_enemy_contacts(self) -> None:
        if self.is_digging or not self.dinosaur.is_grounded:
            return

        for enemy in self.flying_enemies:
            if enemy.contact_handled or enemy.is_helper:
                continue
            if self.dinosaur.rect.colliderect(enemy.rect):
                enemy.contact_handled = True
                self.stun_remaining = max(
                    self.stun_remaining,
                    ENEMY_STUN_SECONDS,
                )
                self._notify('STUNNED', DANGER_COLOR)

    def _resolve_fatal_cactus_collision(self) -> None:
        if (
            self.riding_enemy is not None
            or self.is_digging
            or self.just_entered_inverted
        ):
            return
        for cactus in self.cacti:
            if self.dinosaur.rect.colliderect(cactus.rect):
                self.state = GameState.GAME_OVER
                self.death_overlay_delay_remaining = DEATH_SCREEN_DELAY
                self._notify('GAME OVER', DANGER_COLOR)
                return
    def _remove_cactus(self, cactus: Cactus) -> bool:
        for cluster in list(self.cactus_clusters):
            if cluster.remove(cactus):
                if not cluster.is_active:
                    self.cactus_clusters.remove(cluster)
                return True
        return False

    def _choose_cactus_pattern(self, max_count: int | None = None) -> tuple[int, ...]:
        available_templates = tuple(
            pattern
            for pattern in CACTUS_PATTERNS
            if max_count is None or len(pattern) <= max_count
        )
        if not available_templates:
            return ()

        template = self.rng.choice(available_templates)
        return tuple(
            self.rng.randrange(len(CACTUS_VARIANTS))
            for _ in template
        )

    def _stage_initial_cacti(self) -> None:
        spawn_x = SCREEN_WIDTH + self.rng.randint(
            CACTUS_SPAWN_OFFSET,
            CACTUS_SPAWN_OFFSET + 180,
        )
        for _ in range(3):
            pattern = self._choose_cactus_pattern()
            cluster = CactusCluster(
                spawn_x,
                pattern,
                gap=self.rng.randint(CACTUS_PATTERN_GAP, CACTUS_CLUSTER_GAP),
            )
            self.cactus_clusters.append(cluster)
            spawn_x = cluster.right + self.rng.randint(
                CACTUS_SPAWN_GAP,
                CACTUS_SPAWN_GAP + 240,
            )

    def _update_spawning(self, dt: float) -> None:
        if not self.spawning_enabled:
            return

        self.enemy_spawn_elapsed += dt
        if (
            self.enemy_spawn_elapsed < ENEMY_SPAWN_INTERVAL
            or len(self.flying_enemies) >= MAX_ACTIVE_ENEMIES
        ):
            return

        height_index = self.next_enemy_height_index % len(FLYING_ENEMY_LEVELS)
        enemy = FlyingEnemy(
            SCREEN_WIDTH + 60,
            FLYING_ENEMY_LEVELS[height_index],
            height_index,
        )
        self.flying_enemies.append(enemy)
        self.next_enemy_height_index += 1
        self.enemy_spawn_elapsed = 0.0

    def _replenish_cacti(self) -> None:
        if not self.spawning_enabled:
            return

        while MIN_ACTIVE_CACTI > len(self.cacti):
            remaining_capacity = MAX_ACTIVE_CACTI - len(self.cacti)
            pattern = self._choose_cactus_pattern(remaining_capacity)
            if not pattern:
                return

            rightmost = max(
                (cactus.rect.right for cactus in self.cacti),
                default=SCREEN_WIDTH,
            )
            random_offset = self.rng.randint(
                CACTUS_SPAWN_OFFSET,
                CACTUS_SPAWN_OFFSET + 180,
            )
            random_gap = self.rng.randint(
                CACTUS_SPAWN_GAP,
                CACTUS_SPAWN_GAP + 240,
            )
            spawn_x = max(
                SCREEN_WIDTH + random_offset,
                rightmost + random_gap,
            )
            self.cactus_clusters.append(
                CactusCluster(
                    spawn_x,
                    pattern,
                    gap=self.rng.randint(CACTUS_PATTERN_GAP, CACTUS_CLUSTER_GAP),
                )
            )

    def _notify(self, message: str, color: tuple[int, int, int]) -> None:
        self.last_notification = message
        self.notification_color = color
        self.notification_seconds = 1.0

    @property
    def rainbow_hue(self) -> float:
        return (self.rainbow_elapsed * RAINBOW_HUE_SPEED) % 1.0

    def get_background_color(self) -> tuple[int, int, int]:
        if self.is_inverted:
            return BLACK
        if self.rainbow_remaining > 0:
            return hsv_color(self.rainbow_hue)
        return SKY_COLOR

    def get_ground_color(self) -> tuple[int, int, int]:
        return WHITE if self.is_inverted else BLACK

    def get_floor_color(self) -> tuple[int, int, int]:
        if self.is_inverted or self.rainbow_remaining > 0:
            return WHITE
        return self.get_background_color()

    def get_cactus_colors(
        self,
    ) -> tuple[tuple[int, int, int], tuple[int, int, int]]:
        if self.is_inverted and self.rainbow_remaining > 0:
            hue = self.rainbow_hue
            return (
                hsv_color(hue, 0.8, 0.95),
                hsv_color(hue + 0.08, 0.8, 0.65),
            )
        if self.is_inverted:
            return (
                invert_color(CACTUS_COLOR),
                invert_color(CACTUS_DARK_COLOR),
            )
        return CACTUS_COLOR, CACTUS_DARK_COLOR

    def get_enemy_colors(
        self,
    ) -> tuple[
        tuple[int, int, int],
        tuple[int, int, int],
        tuple[int, int, int],
    ]:
        if self.is_inverted and self.rainbow_remaining > 0:
            hue = self.rainbow_hue
            return (
                hsv_color(hue + 0.55, 0.75, 0.95),
                hsv_color(hue + 0.63, 0.8, 0.75),
                BLACK,
            )
        if self.is_inverted:
            return (
                invert_color(ENEMY_COLOR),
                invert_color(ENEMY_WING_COLOR),
                BLACK,
            )
        return ENEMY_COLOR, ENEMY_WING_COLOR, WHITE

    def get_punch_color(self) -> tuple[int, int, int]:
        if self.is_inverted:
            return invert_color(PUNCH_COLOR)
        return PUNCH_COLOR

    def draw(
        self,
        surface: pygame.Surface,
        font: pygame.font.Font | None = None,
        large_font: pygame.font.Font | None = None,
        sprites: dict[str, pygame.Surface] | None = None,
        medium_font: pygame.font.Font | None = None,
    ) -> None:
        if self.state == GameState.READY:
            surface.fill(SKY_COLOR)
            if font is None or large_font is None:
                return

            title = large_font.render('DINO GAME', True, TEXT_COLOR)
            title_rect = title.get_rect(
                center=(SCREEN_WIDTH // 2, 125)
            )
            surface.blit(title, title_rect)
            prompt = font.render(
                'PRESS SPACE KEY TO START',
                True,
                MUTED_TEXT_COLOR,
            )
            prompt_rect = prompt.get_rect(
                center=(SCREEN_WIDTH // 2, 180)
            )
            surface.blit(prompt, prompt_rect)
            return

        if (
            self.state == GameState.GAME_OVER
            and self.death_overlay_delay_remaining <= 0
        ):
            surface.fill(SKY_COLOR)
            if font is None or large_font is None:
                return

            medium = medium_font or font
            question = medium.render(
                'ARE YOU TRYING TO EAT THE CACTUS?',
                True,
                TEXT_COLOR,
            )
            question_rect = question.get_rect(
                center=(SCREEN_WIDTH // 2, 105)
            )
            surface.blit(question, question_rect)

            lose = large_font.render('YOU LOSE', True, DANGER_COLOR)
            lose_rect = lose.get_rect(
                center=(SCREEN_WIDTH // 2, 165)
            )
            surface.blit(lose, lose_rect)

            prompt = font.render(
                'PRESS SPACE TO RESTART',
                True,
                MUTED_TEXT_COLOR,
            )
            prompt_rect = prompt.get_rect(
                center=(SCREEN_WIDTH // 2, 220)
            )
            surface.blit(prompt, prompt_rect)
            return

        background_color = self.get_background_color()
        floor_color = self.get_floor_color()
        surface.fill(background_color)
        pygame.draw.rect(
            surface,
            floor_color,
            pygame.Rect(
                0,
                GROUND_Y,
                SCREEN_WIDTH,
                SCREEN_HEIGHT - GROUND_Y,
            ),
        )
        pygame.draw.line(
            surface,
            self.get_ground_color(),
            (0, GROUND_Y),
            (SCREEN_WIDTH, GROUND_Y),
            GROUND_LINE_WIDTH,
        )

        cactus_color, cactus_dark_color = self.get_cactus_colors()
        enemy_color, enemy_wing_color, enemy_eye_color = self.get_enemy_colors()
        for cluster in self.cactus_clusters:
            cluster.draw(surface, cactus_color, cactus_dark_color)
        for enemy in self.flying_enemies:
            enemy.draw(
                surface,
                enemy_color,
                enemy_wing_color,
                enemy_eye_color,
            )
        if self.punch_hitbox is not None:
            self.punch_hitbox.draw(surface, self.get_punch_color())

        dino_sprite = None
        if sprites is not None:
            sprite_key = 'dino_inverted' if self.is_inverted else 'dino'
            dino_sprite = sprites.get(sprite_key)
        self.dinosaur.draw(
            surface,
            stunned=self.is_stunned,
            sprite=dino_sprite,
            inverted=self.is_inverted,
        )

        if font is None or large_font is None:
            return

        text_color = WHITE if self.is_inverted else TEXT_COLOR
        muted_color = (
            (180, 180, 180)
            if self.is_inverted
            else MUTED_TEXT_COLOR
        )
        score_text = font.render(f'SCORE {self.score:05d}', True, text_color)
        surface.blit(score_text, (SCREEN_WIDTH - score_text.get_width() - 18, 16))
        best_text = font.render(f'BEST {self.high_score:05d}', True, BONUS_COLOR)
        surface.blit(best_text, (SCREEN_WIDTH - best_text.get_width() - 18, 40))

        speed_text = font.render(
            f'SPEED {int(self.scroll_speed)}',
            True,
            muted_color,
        )
        surface.blit(speed_text, (18, 16))

        status_y = 44
        if self.is_stunned:
            stunned_text = font.render('STUNNED', True, DANGER_COLOR)
            surface.blit(stunned_text, (18, status_y))
            status_y += 24

        if self.helper_remaining > 0:
            helper_text = font.render(
                f'HELPER {self.helper_remaining:.1f}s',
                True,
                BONUS_COLOR,
            )
            surface.blit(helper_text, (18, status_y))
            status_y += 24

        if self.cactus_sweep_remaining > 0:
            ride_text = font.render(
                f'RIDE {self.cactus_sweep_remaining:.1f}s',
                True,
                BONUS_COLOR,
            )
            surface.blit(ride_text, (18, status_y))
            status_y += 24

        if self.is_inverted:
            universe_text = font.render(
                'INVERTED UNIVERSE',
                True,
                WHITE,
            )
            surface.blit(universe_text, (18, status_y))
        elif self.dig_progress > 0:
            dig_text = font.render(
                f'DIG {int(self.dig_progress * 100)}%',
                True,
                muted_color,
            )
            surface.blit(dig_text, (18, status_y))

        if (
            self.notification_seconds > 0
            and self.last_notification
            and not (
                self.state == GameState.GAME_OVER
                and self.death_overlay_delay_remaining > 0
            )
        ):
            notification = font.render(
                self.last_notification,
                True,
                self.notification_color,
            )
            notification_rect = notification.get_rect(
                center=(
                    self.dinosaur.rect.centerx + 42,
                    self.dinosaur.rect.top - 14,
                )
            )
            surface.blit(notification, notification_rect)


def load_sprite(filename: str, size: tuple[int, int]) -> pygame.Surface | None:
    # Trim transparent padding before nearest-neighbor scaling.
    path = ASSET_DIR / filename
    if not path.is_file():
        return None

    try:
        sprite = pygame.image.load(str(path)).convert_alpha()
    except (OSError, pygame.error):
        return None

    bounds = sprite.get_bounding_rect(min_alpha=1)
    if bounds.width <= 0 or bounds.height <= 0:
        return None

    sprite = sprite.subsurface(bounds).copy()
    return pygame.transform.scale(sprite, size)


def invert_surface(sprite: pygame.Surface) -> pygame.Surface:
    inverted = pygame.Surface(sprite.get_size(), pygame.SRCALPHA)
    for x in range(sprite.get_width()):
        for y in range(sprite.get_height()):
            red, green, blue, alpha = sprite.get_at((x, y))
            if alpha:
                inverted.set_at(
                    (x, y),
                    (255 - red, 255 - green, 255 - blue, alpha),
                )
    return inverted


def load_sprites() -> dict[str, pygame.Surface]:
    sprites: dict[str, pygame.Surface] = {}
    dino = load_sprite('dino.png', (DINOSAUR_WIDTH, DINOSAUR_HEIGHT))
    if dino is not None:
        sprites['dino'] = dino
        sprites['dino_inverted'] = invert_surface(dino)
    return sprites


def main() -> None:
    pygame.init()
    try:
        screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Chrome Dinosaur Stomp Runner")
        clock = pygame.time.Clock()
        font = pygame.font.Font(None, 24)
        medium_font = pygame.font.Font(None, 32)
        large_font = pygame.font.Font(None, 48)
        sprites = load_sprites()
        session = GameSession()
        running = True

        while running:
            frame_ms = clock.tick(FPS)
            dt = min(frame_ms / 1000.0, MAX_DT)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    else:
                        session.handle_key_down(event.key)
                elif event.type == pygame.KEYUP:
                    session.handle_key_up(event.key)

            if not running:
                break

            session.update(dt)
            session.draw(screen, font, large_font, sprites, medium_font)
            pygame.display.flip()
    finally:
        pygame.quit()

if __name__ == "__main__":
    main()