import math
import tempfile
import unittest
from pathlib import Path

import pygame

try:
    from . import prj07 as game
except ImportError:
    import prj07 as game


def advance(session, seconds):
    remaining = seconds
    while remaining > 0:
        step = min(game.MAX_DT, remaining)
        session.update(step)
        remaining -= step


class DinosaurPhysicsTests(unittest.TestCase):
    def test_jump_is_grounded_only_and_lands_on_ground(self):
        dinosaur = game.Dinosaur()

        self.assertTrue(dinosaur.is_grounded)
        self.assertTrue(dinosaur.jump())
        jump_velocity = dinosaur.velocity_y
        self.assertFalse(dinosaur.jump())
        self.assertEqual(dinosaur.velocity_y, jump_velocity)

        for _ in range(120):
            dinosaur.update(1 / 120)

        self.assertTrue(dinosaur.is_grounded)
        self.assertEqual(dinosaur.rect.bottom, game.GROUND_Y)


    def test_jump_arc_reaches_the_higher_tuned_peak(self):
        dinosaur = game.Dinosaur()
        dinosaur.jump()
        highest_top = dinosaur.position_y

        for _ in range(120):
            dinosaur.update(1 / 120)
            highest_top = min(highest_top, dinosaur.position_y)

        self.assertLessEqual(
            highest_top,
            game.GROUND_Y - game.DINOSAUR_HEIGHT - 100,
        )


class CactusTests(unittest.TestCase):
    def test_cluster_reflects_at_both_boundaries_and_stays_active(self):
        cluster = game.CactusCluster(10, (0,))
        cluster.direction = -1
        cluster.update(0.1, 300)

        self.assertEqual(cluster.left, 0)
        self.assertEqual(cluster.direction, 1)
        self.assertTrue(cluster.is_active)

        cluster.update(0.1, 300)
        self.assertGreater(cluster.left, 0)

        cluster = game.CactusCluster(game.SCREEN_WIDTH - 20, (0,))
        cluster.direction = 1
        cluster.update(0.1, 300)

        self.assertEqual(cluster.right, game.SCREEN_WIDTH)
        self.assertEqual(cluster.direction, -1)
        self.assertTrue(cluster.is_active)

    def test_bounced_cluster_uses_the_slower_return_speed(self):
        cluster = game.CactusCluster(2, (0,))
        cluster.update(0.01, game.INITIAL_SCROLL_SPEED)

        self.assertTrue(cluster.has_bounced)
        start_left = cluster.left
        cluster.update(0.1, game.INITIAL_SCROLL_SPEED)

        self.assertLess(
            cluster.left - start_left,
            game.INITIAL_SCROLL_SPEED * 0.1,
        )

    def test_second_bounce_is_only_a_little_faster_than_first_return(self):
        first = game.CactusCluster(400, (0,))
        first.has_bounced = True
        first.bounce_count = 1
        first_start = first.cacti[0].position_x
        first.update(0.1, game.INITIAL_SCROLL_SPEED)
        first_distance = abs(first.cacti[0].position_x - first_start)

        second = game.CactusCluster(400, (0,))
        second.has_bounced = True
        second.bounce_count = 2
        second_start = second.cacti[0].position_x
        second.update(0.1, game.INITIAL_SCROLL_SPEED)
        second_distance = abs(second.cacti[0].position_x - second_start)

        self.assertAlmostEqual(
            first_distance,
            game.CACTUS_BOUNCE_SPEED * 0.1,
        )
        self.assertAlmostEqual(
            second_distance,
            game.CACTUS_SECOND_BOUNCE_SPEED * 0.1,
        )
        self.assertGreater(second_distance, first_distance)
        self.assertLess(
            second_distance,
            game.INITIAL_SCROLL_SPEED * 0.1,
        )

    def test_bottom_side_touch_removes_cactus(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.spawning_enabled = False
        session.cactus_clusters = []
        session.flying_enemies = []
        session.world_speed_override = 0

        cluster = game.CactusCluster(160, (0,))
        cactus = cluster.cacti[0]
        session.cactus_clusters.append(cluster)

        dinosaur = session.dinosaur
        dinosaur.position_y = float(cactus.rect.top - dinosaur.height)
        dinosaur.rect.top = round(dinosaur.position_y)
        dinosaur.previous_bottom = dinosaur.current_bottom
        dinosaur.previous_velocity_y = 0
        dinosaur.velocity_y = 0
        dinosaur.is_grounded = False

        session.update(0)

        self.assertEqual(session.state, game.GameState.RUNNING)
        self.assertNotIn(cactus, session.cacti)
        self.assertEqual(session.bonus_score, game.STOMP_BONUS)

    def test_stomp_removes_cactus_and_awards_points(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.spawning_enabled = False
        session.cactus_clusters = []
        session.flying_enemies = []
        session.world_speed_override = 0

        cluster = game.CactusCluster(160, (0,))
        cactus = cluster.cacti[0]
        session.cactus_clusters.append(cluster)

        dinosaur = session.dinosaur
        dinosaur.position_y = cactus.rect.top - dinosaur.rect.height - 5
        dinosaur.rect.top = round(dinosaur.position_y)
        dinosaur.velocity_y = 200
        dinosaur.is_grounded = False

        session.update(0.05)

        self.assertEqual(session.state, game.GameState.RUNNING)
        self.assertEqual(session.bonus_score, game.STOMP_BONUS)
        self.assertNotIn(cactus, cluster.cacti)

    def test_seeded_cactus_spawns_are_repeatable_but_not_fixed(self):
        first = game.GameSession(seed=1, persist_high_score=False)
        same_seed = game.GameSession(seed=1, persist_high_score=False)
        different_seed = game.GameSession(seed=2, persist_high_score=False)

        def signature(session):
            return [
                (
                    len(cluster.cacti),
                    cluster.gap,
                    tuple(cactus.variant_index for cactus in cluster.cacti),
                )
                for cluster in session.cactus_clusters
            ]

        self.assertEqual(signature(first), signature(same_seed))
        self.assertNotEqual(signature(first), signature(different_seed))
        self.assertLessEqual(len(first.cacti), game.MAX_ACTIVE_CACTI)
        self.assertTrue(all(len(cluster.cacti) <= 3 for cluster in first.cactus_clusters))

    def test_side_contact_causes_game_over(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.spawning_enabled = False
        session.cactus_clusters = []
        session.flying_enemies = []
        session.world_speed_override = 0

        cactus_x = session.dinosaur.rect.right - 4
        session.cactus_clusters.append(game.CactusCluster(cactus_x, (0,)))

        session.update(0)

        self.assertEqual(session.state, game.GameState.GAME_OVER)


class PunchAndEnemyTests(unittest.TestCase):
    def make_running_session(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.spawning_enabled = False
        session.cactus_clusters = []
        session.flying_enemies = []
        session.world_speed_override = 0
        return session

    def test_airborne_e_creates_one_punch_and_destroys_enemy(self):
        session = self.make_running_session()
        dinosaur = session.dinosaur
        dinosaur.jump()

        enemy = game.FlyingEnemy(dinosaur.rect.right + 72, dinosaur.rect.top)
        session.flying_enemies.append(enemy)

        session.handle_key_down(pygame.K_e)

        self.assertEqual(session.punch_cooldown, game.PUNCH_COOLDOWN)
        self.assertEqual(game.PUNCH_COOLDOWN, 5.0)
        self.assertIsNotNone(session.punch_hitbox)
        session.update(0.01)

        self.assertEqual(session.bonus_score, game.PUNCH_BONUS)
        self.assertNotIn(enemy, session.flying_enemies)

    def test_grounded_e_does_not_create_normal_punch(self):
        session = self.make_running_session()

        session.handle_key_down(pygame.K_e)

        self.assertIsNone(session.punch_hitbox)
        self.assertTrue(session.combo_attempt_pending)

    def test_held_e_does_not_repeat_air_punch(self):
        session = self.make_running_session()
        dinosaur = session.dinosaur
        dinosaur.jump()

        first_enemy = game.FlyingEnemy(dinosaur.rect.right + 8, dinosaur.rect.top)
        session.flying_enemies.append(first_enemy)
        session.handle_key_down(pygame.K_e)
        session.update(0.01)

        second_enemy = game.FlyingEnemy(dinosaur.rect.right + 8, dinosaur.rect.top)
        session.flying_enemies.append(second_enemy)
        advance(session, 0.5)
        session.handle_key_down(pygame.K_e)

        self.assertEqual(session.bonus_score, game.PUNCH_BONUS)
        self.assertIn(second_enemy, session.flying_enemies)

    def test_stomping_pterodactyl_starts_five_second_ride(self):
        session = self.make_running_session()
        dinosaur = session.dinosaur

        cluster = game.CactusCluster(dinosaur.rect.right + 20, (0,))
        session.cactus_clusters = [cluster]
        enemy = game.FlyingEnemy(dinosaur.rect.right - 10, 145)
        session.flying_enemies = [enemy]

        dinosaur.position_y = float(enemy.rect.top - dinosaur.height - 5)
        dinosaur.rect.top = round(dinosaur.position_y)
        dinosaur.previous_bottom = dinosaur.current_bottom
        dinosaur.velocity_y = 200
        dinosaur.is_grounded = False

        session.update(0.05)

        self.assertEqual(session.state, game.GameState.RUNNING)
        self.assertTrue(enemy.is_sweeper)
        self.assertTrue(enemy.is_ridden)
        self.assertEqual(
            enemy.rect.top,
            game.GROUND_Y - game.FLYING_ENEMY_HEIGHT,
        )
        self.assertEqual(
            dinosaur.rect.bottom,
            enemy.rect.top,
        )
        self.assertEqual(session.cactus_sweep_remaining, game.CACTUS_SWEEP_SECONDS)
        self.assertIn(cluster.cacti[0], session.cacti)
        self.assertEqual(session.last_notification, 'RIDING PTERODACTYL')

        cactus = cluster.cacti[0]
        cactus.position_x = float(enemy.rect.right - 5)
        cactus.rect.x = round(cactus.position_x)
        session.update(0.1)

        self.assertNotIn(cactus, session.cacti)
        self.assertLess(session.cactus_sweep_remaining, game.CACTUS_SWEEP_SECONDS)

        advance(session, game.CACTUS_SWEEP_SECONDS)
        self.assertIsNone(session.riding_enemy)
        self.assertFalse(enemy.is_ridden)
        self.assertEqual(enemy.rect.top, enemy.flight_y)

    def test_unpunched_enemy_stuns_once_without_game_over(self):
        session = self.make_running_session()
        dinosaur = session.dinosaur
        enemy = game.FlyingEnemy(dinosaur.rect.left, dinosaur.rect.top + 8)
        session.flying_enemies.append(enemy)

        session.update(0.01)
        first_stun = session.stun_remaining
        session.update(0.01)

        self.assertGreater(first_stun, 0)
        self.assertLess(session.stun_remaining, first_stun)
        self.assertEqual(session.state, game.GameState.RUNNING)
        self.assertTrue(enemy.contact_handled)
        self.assertEqual(session.bonus_score, 0)


class ComboAndScoreTests(unittest.TestCase):
    def make_running_session(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.spawning_enabled = False
        session.flying_enemies = []
        session.world_speed_override = 0
        return session

    def test_three_cacti_trigger_ground_combo_once_per_hold(self):
        session = self.make_running_session()
        start_x = session.dinosaur.rect.right + 20
        cluster = game.CactusCluster(start_x, (0, 0, 0), gap=8)
        session.cactus_clusters = [cluster]

        self.assertEqual(len(session.find_combo_targets()), 3)

        session.handle_key_down(pygame.K_e)
        advance(session, game.GROUND_COMBO_HOLD_SECONDS)

        self.assertEqual(session.bonus_score, game.COMBO_BONUS)
        self.assertEqual(session.last_notification, "COMBO x3")

        session.handle_key_up(pygame.K_e)
        session.handle_key_down(pygame.K_e)
        advance(session, game.GROUND_COMBO_HOLD_SECONDS)

        self.assertEqual(session.bonus_score, game.COMBO_BONUS)

    def test_combo_uses_other_cacti_but_caps_at_three_targets(self):
        session = self.make_running_session()
        start_x = session.dinosaur.rect.right + 20
        session.cactus_clusters = [
            game.CactusCluster(start_x + index * 90, (0,))
            for index in range(4)
        ]

        session.handle_key_down(pygame.K_e)
        advance(session, game.GROUND_COMBO_HOLD_SECONDS)

        self.assertEqual(len(session.cacti), 1)
        self.assertEqual(session.bonus_score, 3 * game.STOMP_BONUS)
        self.assertEqual(session.last_notification, 'COMBO x3')

    def test_high_score_records_and_survives_restart(self):
        session = self.make_running_session()
        session.bonus_score = 75
        session.update(0)

        self.assertEqual(session.high_score, 75)

        session.state = game.GameState.GAME_OVER
        session.handle_key_down(pygame.K_r)

        self.assertEqual(session.high_score, 75)
        self.assertEqual(session.score, 0)

    def test_empty_combo_attempt_starts_cooldown_and_blocks_retry(self):
        session = self.make_running_session()
        session.cactus_clusters = []

        session.handle_key_down(pygame.K_e)
        advance(session, game.GROUND_COMBO_HOLD_SECONDS)
        failed_cooldown = session.combo_cooldown

        session.handle_key_up(pygame.K_e)
        session.handle_key_down(pygame.K_e)
        advance(session, game.GROUND_COMBO_HOLD_SECONDS)

        self.assertGreater(failed_cooldown, game.GROUND_COMBO_COOLDOWN - 1)
        self.assertEqual(session.bonus_score, 0)
        self.assertGreater(session.combo_cooldown, 0)

    def test_survival_score_increases_and_speed_is_capped(self):
        session = self.make_running_session()
        session.world_speed_override = None
        session.cactus_clusters = []
        session.flying_enemies = []

        advance(session, game.DIFFICULTY_INTERVAL + 1)
        self.assertGreater(session.score, 0)
        self.assertGreater(session.scroll_speed, game.INITIAL_SCROLL_SPEED)

        advance(session, game.DIFFICULTY_INTERVAL * 30)
        self.assertLessEqual(session.scroll_speed, game.MAX_SCROLL_SPEED)

    def test_score_freezes_after_game_over(self):
        session = self.make_running_session()
        session.cactus_clusters = []
        advance(session, 1)
        session.state = game.GameState.GAME_OVER
        score = session.score
        elapsed = session.elapsed_seconds

        advance(session, 2)

        self.assertEqual(session.score, score)
        self.assertEqual(session.elapsed_seconds, elapsed)


    def test_cactus_death_delays_loss_overlay_for_half_second(self):
        session = self.make_running_session()
        cactus_x = session.dinosaur.rect.right - 4
        session.cactus_clusters = [game.CactusCluster(cactus_x, (0,))]

        session.update(0)

        self.assertEqual(session.state, game.GameState.GAME_OVER)
        self.assertEqual(
            session.death_overlay_delay_remaining,
            game.DEATH_SCREEN_DELAY,
        )
        score = session.score
        elapsed = session.elapsed_seconds

        advance(session, game.DEATH_SCREEN_DELAY / 2)
        self.assertGreater(session.death_overlay_delay_remaining, 0)
        self.assertEqual(session.score, score)
        self.assertEqual(session.elapsed_seconds, elapsed)

        advance(session, game.DEATH_SCREEN_DELAY / 2 + game.MAX_DT)
        self.assertEqual(session.death_overlay_delay_remaining, 0)


class AbilityTests(unittest.TestCase):
    def make_running_session(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.spawning_enabled = False
        session.cactus_clusters = []
        session.flying_enemies = []
        session.world_speed_override = 0
        return session

    def test_w_starts_red_rainbow_and_uses_sixty_second_cooldown(self):
        session = self.make_running_session()

        self.assertTrue(session.handle_key_down(pygame.K_w))
        self.assertEqual(session.get_background_color(), (255, 0, 0))
        self.assertEqual(session.rainbow_remaining, game.RAINBOW_SECONDS)
        self.assertEqual(session.rainbow_cooldown, game.RAINBOW_COOLDOWN)

        session.handle_key_up(pygame.K_w)
        session.update(0.1)
        self.assertNotEqual(session.get_background_color(), (255, 0, 0))

        advance(session, game.RAINBOW_SECONDS)
        self.assertEqual(session.rainbow_remaining, 0)
        self.assertEqual(session.get_background_color(), game.SKY_COLOR)
        self.assertFalse(session.handle_key_down(pygame.K_w))

    def test_d_tap_and_hold_enter_inverted_world_and_d_toggles_back(self):
        session = self.make_running_session()

        self.assertTrue(session.handle_key_down(pygame.K_d))
        session.handle_key_up(pygame.K_d)
        self.assertGreater(session.dig_progress, 0)
        self.assertFalse(session.is_inverted)

        session.handle_key_down(pygame.K_d)
        advance(session, game.DIG_SECONDS_TO_INVERT)
        self.assertTrue(session.is_inverted)
        self.assertEqual(session.get_background_color(), game.BLACK)
        session.handle_key_up(pygame.K_d)

        session.handle_key_down(pygame.K_w)
        self.assertEqual(session.get_background_color(), game.BLACK)
        normal_cactus_colors = (game.CACTUS_COLOR, game.CACTUS_DARK_COLOR)
        self.assertNotEqual(session.get_cactus_colors(), normal_cactus_colors)
        session.handle_key_up(pygame.K_w)

        self.assertTrue(session.handle_key_down(pygame.K_d))
        self.assertTrue(session.is_inverted)
        self.assertTrue(session.is_digging)
        advance(session, game.DIG_SECONDS_TO_INVERT)
        self.assertFalse(session.is_inverted)
        self.assertFalse(session.is_digging)
        self.assertEqual(session.dig_progress, 0)
        self.assertTrue(session.dinosaur.is_grounded)
        session.handle_key_up(pygame.K_d)

    def test_ground_line_and_floor_colors_are_distinct(self):
        session = self.make_running_session()
        surface = pygame.Surface((game.SCREEN_WIDTH, game.SCREEN_HEIGHT))

        session.draw(surface)
        self.assertEqual(session.get_ground_color(), game.BLACK)
        self.assertEqual(
            surface.get_at((20, game.GROUND_Y))[:3],
            game.BLACK,
        )
        self.assertEqual(
            surface.get_at((20, game.GROUND_Y + 4))[:3],
            game.SKY_COLOR,
        )

        session.rainbow_remaining = game.RAINBOW_SECONDS
        session.draw(surface)
        self.assertEqual(session.get_floor_color(), game.WHITE)
        self.assertEqual(
            surface.get_at((20, game.GROUND_Y))[:3],
            game.BLACK,
        )
        self.assertEqual(
            surface.get_at((20, game.SCREEN_HEIGHT - 1))[:3],
            game.WHITE,
        )

        session.is_inverted = True
        session.draw(surface)
        self.assertEqual(session.get_ground_color(), game.WHITE)
        self.assertEqual(session.get_floor_color(), game.WHITE)
        self.assertEqual(
            surface.get_at((20, game.GROUND_Y))[:3],
            game.WHITE,
        )
        self.assertEqual(
            surface.get_at((20, game.SCREEN_HEIGHT - 1))[:3],
            game.WHITE,
        )

    def test_airborne_does_not_start_dig_or_cancel_jump_gravity(self):
        session = self.make_running_session()
        dinosaur = session.dinosaur
        dinosaur.jump()

        self.assertFalse(session.handle_key_down(pygame.K_d))
        self.assertFalse(session.is_digging)
        self.assertEqual(session.dig_progress, 0)
        session.handle_key_up(pygame.K_d)

        position_before = dinosaur.position_y
        session.update(game.MAX_DT)

        self.assertLess(dinosaur.position_y, position_before)
        self.assertFalse(session.is_digging)


    def test_r_summons_helper_that_clears_contacts_for_five_seconds(self):
        session = self.make_running_session()

        self.assertTrue(session.handle_key_down(pygame.K_r))
        helper = session.helper_enemy
        self.assertIsNotNone(helper)
        self.assertTrue(helper.is_helper)
        self.assertEqual(session.helper_remaining, game.HELPER_SECONDS)
        self.assertEqual(session.helper_cooldown, game.HELPER_COOLDOWN)
        self.assertFalse(session.handle_key_down(pygame.K_r))

        cactus_cluster = game.CactusCluster(helper.rect.left, (0,))
        cactus = cactus_cluster.cacti[0]
        session.cactus_clusters = [cactus_cluster]
        session.update(0)

        self.assertNotIn(cactus, session.cacti)
        session.handle_key_up(pygame.K_r)
        advance(session, game.HELPER_SECONDS)
        self.assertIsNone(session.helper_enemy)
        self.assertFalse(helper in session.flying_enemies)
        self.assertGreater(session.helper_cooldown, 0)
        self.assertFalse(session.handle_key_down(pygame.K_r))

    def test_high_score_is_persistent_for_a_user_path(self):
        with tempfile.TemporaryDirectory() as temporary_directory:
            score_path = Path(temporary_directory) / 'score.json'
            first = game.GameSession(high_score_path=score_path)
            first.start()
            first.spawning_enabled = False
            first.cactus_clusters = []
            first.flying_enemies = []
            first.world_speed_override = 0
            first.bonus_score = 321
            first.update(0)

            second = game.GameSession(high_score_path=score_path)
            self.assertEqual(second.high_score, 321)


class ResetTests(unittest.TestCase):
    def test_space_revives_with_remaining_score_after_spending_500(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.spawning_enabled = False
        session.cactus_clusters = []
        session.flying_enemies = []
        session.bonus_score = game.REVIVE_COST + 150
        session.state = game.GameState.GAME_OVER

        session.handle_key_down(pygame.K_SPACE)

        self.assertEqual(session.state, game.GameState.RUNNING)
        self.assertEqual(session.score, 150)
        self.assertFalse(session.dinosaur.is_grounded)
        self.assertEqual(session.dinosaur.velocity_y, game.JUMP_VELOCITY)

    def test_restart_clears_transient_state_and_supports_both_restart_styles(self):
        session = game.GameSession(persist_high_score=False)
        session.start()
        session.state = game.GameState.GAME_OVER
        session.bonus_score = 123
        session.elapsed_seconds = 7
        session.stun_remaining = 0.3
        session.cactus_sweep_remaining = 4.0
        session.flying_enemies = [game.FlyingEnemy(200, 200)]
        session.riding_enemy = session.flying_enemies[0]
        session.flying_enemies[0].is_ridden = True
        session.punch_cooldown = 0.2
        session.combo_cooldown = 9
        session.helper_remaining = 4
        session.helper_cooldown = 29
        session.rainbow_remaining = 14
        session.rainbow_cooldown = 59
        session.rainbow_elapsed = 3
        session.dig_progress = 1
        session.is_inverted = True
        session.punch_hitbox = game.PunchHitbox(session.dinosaur.rect)
        session.e_is_held = True
        session.w_is_held = True
        session.r_is_held = True
        session.d_is_held = True
        session.handle_key_up(pygame.K_e)
        session.handle_key_down(pygame.K_r)

        self.assertEqual(session.state, game.GameState.RUNNING)
        self.assertTrue(session.dinosaur.is_grounded)
        self.assertEqual(session.score, 0)
        self.assertEqual(session.scroll_speed, game.INITIAL_SCROLL_SPEED)
        self.assertEqual(session.elapsed_seconds, 0)
        self.assertEqual(session.stun_remaining, 0)
        self.assertEqual(session.cactus_sweep_remaining, 0)
        self.assertEqual(session.helper_remaining, 0)
        self.assertEqual(session.helper_cooldown, 0)
        self.assertEqual(session.rainbow_remaining, 0)
        self.assertEqual(session.rainbow_cooldown, 0)
        self.assertEqual(session.rainbow_elapsed, 0)
        self.assertEqual(session.dig_progress, 0)
        self.assertFalse(session.is_inverted)
        self.assertIsNone(session.helper_enemy)
        self.assertIsNone(session.riding_enemy)
        self.assertEqual(session.punch_cooldown, 0)
        self.assertEqual(session.combo_cooldown, 0)
        self.assertIsNone(session.punch_hitbox)
        self.assertFalse(session.e_is_held)
        self.assertFalse(session.w_is_held)
        self.assertFalse(session.r_is_held)
        self.assertFalse(session.d_is_held)
        self.assertEqual(session.flying_enemies, [])
        self.assertGreater(len(session.cacti), 0)

        session.state = game.GameState.GAME_OVER
        session.handle_key_down(pygame.K_SPACE)

        self.assertEqual(session.state, game.GameState.RUNNING)
        self.assertFalse(session.dinosaur.is_grounded)


class VisualAssetTests(unittest.TestCase):
    def test_dinosaur_asset_is_exact_black_white_and_transparent(self):
        asset_path = game.ASSET_DIR / 'dino.png'
        self.assertTrue(asset_path.is_file())

        sprite = pygame.image.load(str(asset_path))
        visible_colors = set()
        white_pixels = 0
        for y in range(sprite.get_height()):
            for x in range(sprite.get_width()):
                color = sprite.get_at((x, y))
                if color.a == 0:
                    continue
                visible_colors.add((color.r, color.g, color.b, color.a))
                white_pixels += int((color.r, color.g, color.b) == (255, 255, 255))

        self.assertEqual(visible_colors, {(0, 0, 0, 255), (255, 255, 255, 255)})
        self.assertGreater(white_pixels, 0)


if __name__ == "__main__":
    unittest.main()
