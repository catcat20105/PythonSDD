# Research: Chrome Dinosaur Stomp Runner

## Repository and runtime baseline

- The repository is a sequential Python/Pygame learning project with standalone examples in Day1/ and Day2/.
- requirements.txt pins the only project dependency to pygame-ce==2.5.8.
- There is no existing Day3 implementation; the feature adds Day3/prj07.py and Day3/test_prj07.py.
- The existing Day2 edits and unrelated untracked/deleted artifacts are outside this feature and must remain untouched.

## Decision 1: Keep a standalone Pygame module

Decision: Use one readable Day3/prj07.py containing entities, session rules, rendering, and main(), with standard-library tests beside it.

Rationale: This matches the learning progression and keeps the complete game loop visible without adding an engine or framework.

Alternatives considered:

- Browser JavaScript: rejected because the repository baseline and requested workflow are Python/Pygame.
- Multiple engine modules: deferred because the first version benefits from a single inspectable exercise file.

## Decision 2: Use explicit state and delta-time movement

Decision: GameSession owns READY, RUNNING, and GAME_OVER; entities update using bounded delta time.

Rationale: State ownership makes reset and freeze behavior traceable, while delta time keeps jump and scroll behavior stable when frame length varies.

## Decision 3: Treat the flying targets as pterodactyls

Decision: Draw simple pterodactyl-shaped flying enemies at a deterministic cycle of elevated heights.

Rationale: Pterodactyls are the recognizable Chrome Dinosaur flying hazard and can be rendered with the same primitive-only constraint.

Behavior decision: Airborne fresh E presses create a forgiving 0.12-second forward melee hitbox with a five-second cooldown. A missed contact causes a 0.5-second nonfatal stun instead of game over; a descending stomp mounts the dinosaur on the pterodactyl at cactus height for a five-second ride.

## Decision 4: Make cacti persistent bouncing targets

Decision: Cacti initially travel left, reverse at the left edge, reverse again at the right edge, and remain until stomped, combo-cleared, or touched by the ridden pterodactyl. The first reflected return uses a slower speed and the second reflected return is only slightly faster.

Rationale: This directly implements the requested “bounce back if not stomped” behavior. A shared CactusCluster direction preserves compact groups as they travel.

Alternatives considered:

- Remove cacti offscreen: rejected because it would lose the requested return behavior.
- Let each cactus in a cluster reflect independently: rejected because it would break the close-group combo condition.

## Decision 5: Use deterministic patterns and a bounded pool

Decision: Randomly choose single, pair, and three-cactus patterns, vary safe spacing, and cap active cacti at 12; accept an optional seed for repeatable tests.

Rationale: Determinism keeps tests repeatable; a cap prevents persistent bouncing objects from growing without bound.

## Decision 6: Implement the grounded E Easter egg as a one-shot hold

Decision: A fresh grounded E press starts a 0.five-second hold attempt. It clears up to three cacti within 320 pixels for 50 points each. Success or failure starts a 15-second cooldown; release/re-press is required.

Rationale: This honors the explicit distinction between press-only airborne punches and the special grounded hold, while making the “wasted chance” behavior testable.

## Decision 7: Keep score composable

Decision: score = int(elapsed_seconds * 10) + bonus_score, with 50-point stomps, 100-point pterodactyl punches, and up to 150 points for a three-cactus combo. Track the maximum score as the all-time high score for the current local user and persist it best-effort. Pterodactyl sweeps do not award a separate bonus.

Rationale: Survival score remains monotonic and easy to reset, while interaction bonuses are independently visible and testable.

## Decision 8: Add pterodactyl sweep state

Decision: A descending dinosaur crossing a pterodactyl top activates that enemy as a ride, places the dinosaur on top at cactus height, and removes cacti only when they touch the ridden pterodactyl for five seconds. The ride is independent of the pterodactyl's original flight level.

Rationale: The mounted pterodactyl becomes the moving cactus counter while preserving the existing nonfatal missed-contact rule.

## Decision 9: Verify pure rules plus manual interaction
Decision: Use unittest for physics, reflection, collision, combat, cooldown, score, cap, and reset rules; use the quickstart for the Pygame window and shutdown paths.

Rationale: This follows the project constitution without introducing GUI automation or additional packages.

    
## Decision 10: Add W, R, and D abilities

Decision: W is a fresh-press 15-second rainbow with a 60-second cooldown; R is a fresh-press five-second helper with a 30-second cooldown; D accumulates tap/hold progress and changes to the selected opposite universe only after a bottom-exit traversal.

Rationale: Each ability has explicit transient fields and an edge state, so keyboard repeat cannot accidentally chain actions. The inverted palette keeps the background black while W animates only hazards, and helper clears avoid changing the scoring economy.

## Decision 11: Persist BEST per local user

Decision: Store a single high_score value in a best-effort JSON file under the current user's local application-data directory.

Rationale: This meets the all-time-by-this-user requirement without accounts, networking, or an online leaderboard. A test-injected path keeps persistence deterministic and import remains side-effect free.

## Decision 12: Verify the latest controls

Decision: Use unittest for W timing and palette rules, helper lifetime/contact clearing/cooldown, D tap/hold/toggle behavior, persistence, and complete reset; use quickstart manual checks for visual colors and keyboard flow.

Rationale: The ability state is deterministic even though the actual window remains a manual smoke-test concern.


## Decision 13: Add a visible death transition and score-preserving revive

Decision: A fatal cactus collision changes the session to GAME_OVER immediately but keeps the last gameplay scene drawable for exactly 0.5 seconds before the loss overlay appears. Space/Up during GAME_OVER spends 500 points and carries the remainder into an automatic jumping restart when the score is sufficient; R remains the zero-score standing restart. Jumping off a ridden pterodactyl removes that ride source, and airborne or mounted contact cannot stun the dinosaur.

Rationale: The short frozen transition lets the player see the collision outcome without advancing the world, while the explicit revive cost makes score preservation meaningful and keeps the ordinary R restart available. The ride rules support chaining without letting a second flying enemy punish a player who is already airborne.


## Decision 14: Make universe digging symmetric

Decision: D always performs a visible downward dig to the bottom edge. A fresh press in normal mode targets the inverted universe; a fresh press in inverted mode targets the normal universe. The universe changes only after the dinosaur exits the screen, and the floor below the ground line uses the normal background ordinarily but becomes pure white during rainbow or inverted mode while the line is black normally and white in the inverted universe.

Rationale: Matching transitions in both directions makes the mechanic understandable and avoids a surprising teleport when leaving the inverted universe. A fixed ground color keeps the playfield readable while the background and hazard colors change.


## Decision 15: Restrict digging to grounded play

Decision: A D press can start a universe dig only while the dinosaur is grounded. Airborne D presses are ignored, leaving the normal gravity-driven jump unchanged.

Rationale: Digging intentionally bypasses the standard vertical physics while the dinosaur travels off the bottom edge. Allowing it in midair creates an unintended flight exploit, so the input guard keeps the two movement modes separate.
