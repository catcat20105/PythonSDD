# Implementation Plan: Chrome Dinosaur Stomp Runner

Branch: 001-chrome-dinosaur-game | Date: 2026-08-27 | Spec: spec.md

Input: Feature specification from /specs/001-chrome-dinosaur-game/spec.md

## Summary

Build a self-contained Python/Pygame endless runner in Day3/prj07.py. The dinosaur stays in a fixed horizontal lane while cacti and pterodactyls move through the scene. Cacti can be stomped from above or persist and bounce between boundaries with two reflected speed tiers; airborne E presses create forgiving short punch hitboxes with a five-second cooldown; a grounded hold-E Easter egg clears up to three nearby cacti; stomping a pterodactyl mounts the dino on it at cactus height for a five-second contact sweep. W starts rainbow mode, R summons a temporary helper, and D enters the inverted universe. Space/Up can revive a sufficiently high-scoring game over by spending 500 points, while a fatal cactus hit holds the final gameplay scene for 0.5 seconds before the loss overlay. GameSession owns all run state, timers, scoring, spawning, and transitions, while BEST persists per local user and tests remain display-free.

## Technical Context

Language/Version: Python 3.14.7; keep syntax compatible with the project’s Python 3.x exercises

Primary Dependencies: pygame-ce==2.5.8; Python standard-library unittest

Storage: User-local JSON BEST record in LOCALAPPDATA/ChromeDinoStompRunner/high_score.json, with a platform fallback

Testing: py_compile, import checks, unittest, and manual Pygame smoke tests

Target Platform: Windows desktop keyboard with a functioning Pygame display

Project Type: Offline desktop game / educational standalone script

Performance Goals: Target 60 FPS; update only the bounded active entity lists; clamp frame delta time

Constraints: No network, downloaded assets, audio, framework, or additional dependency; local BEST persistence is best-effort; preserve existing Day1/Day2 snapshots and unrelated worktree changes

Scale/Scope: One 960x360 window, one dinosaur, at most 12 active cacti, a small pterodactyl list, five gameplay stories, and no online leaderboard

## Constitution Check

Gate: Must pass before implementation and be re-checked after validation.

| Principle / gate | Evaluation |
|---|---|
| I. 可運作的漸進式學習 | PASS. Work is divided into runnable entities, stomp loop, punch loop, combo/scoring, and restart/UI slices. |
| II. 清楚的 Python 結構與命名 | PASS. Dinosaur, Cactus, CactusCluster, FlyingEnemy, PunchHitbox, and GameSession have focused responsibilities and named constants. |
| III. 明確的遊戲迴圈與狀態 | PASS. Input, timers, physics, movement, attack/stomp resolution, fatal collision, drawing, and display order is explicit; shutdown is centralized. |
| IV. 以可重現驗證確保正確性 | PASS. Physics, reflection, stomp, punch, stun, combo, score, cap, and reset rules have deterministic unit checks plus manual smoke scenarios. |
| V. 可讀、可除錯、可維護的遊戲程式 | PASS. Balance values are centralized; implementation remains limited to a new Day3 exercise and feature documentation. |
| Dependency / scope gate | PASS. The existing pinned Pygame dependency is sufficient; the only artwork is a local generated PNG and no runtime service or download is added. |

## Project Structure

### Documentation

~~~text
specs/001-chrome-dinosaur-game/
├── spec.md
├── plan.md
├── research.md
├── data-model.md
├── quickstart.md
├── contracts/ui.md
└── tasks.md
~~~

### Source Code

~~~text
Day3/
├── prj07.py
└── test_prj07.py
~~~

Structure Decision: Keep the entire game in one learner-readable module, with an adjacent standard-library test module and one local generated sprite in Day3/assets. Do not modify Day1 or Day2, introduce an engine package, or add a runtime service layer.

## Design and Implementation Approach

### Configuration and entities

Centralize the baseline values near the top of prj07.py: 960x360 window, 60 FPS, ground y around 290, initial speed 300, speed cap 520, gravity 1900, tuned jump velocity -780, elevated pterodactyl levels (190, 145, 210), first reflected cactus speed 125, second reflected cactus speed 155, five-second difficulty interval, and ten survival points per second. Add named combat values for 50-point stomps, 100-point punches, up-to-150-point combos, forgiving 0.12-second punches, five-second punch cooldown, 0.5-second enemy stun, five-second cactus sweep, 0.five-second combo hold, 15-second combo cooldown, 320-pixel combo reach, and a 12-cactus active cap. Add five-second helper/30-second helper cooldown, 15-second rainbow/60-second rainbow cooldown, D dig threshold constants, a 500-point revive cost, and a 0.5-second death-overlay delay.

Dinosaur owns its rectangle, float vertical position, previous/current bottom values, velocity, grounded flag, jump, reset, and drawing. The normal renderer uses the bundled minimal black-and-white dino sprite and keeps the primitive renderer as a safe fallback. Cactus owns one ground rectangle and visual variant. CactusCluster moves its members together, reflects only when travelling into the corresponding screen boundary, tracks bounce count for the slower first return and slightly faster second return, and remains until members are stomped or combo-cleared. FlyingEnemy moves left, can be stomped so the dinosaur rides it at cactus height, removes cacti on contact during the ride, and is removed after leaving the left side. PunchHitbox is anchored in front of the dinosaur for its short lifetime and can register one enemy hit.

### Session and input rules

GameSession owns READY, RUNNING, and GAME_OVER, the dinosaur, cactus clusters, flying enemies, score components, elapsed time, speed, seeded random generator, all-time per-local-user high score, punch state, stun timer, cactus-sweep timer, E-held state, combo hold timer, and cooldowns. score is survival score plus bonuses; it freezes automatically because update() is a no-op outside RUNNING.

Use KEYDOWN/KEYUP edge handling for E. A fresh airborne E press creates one forgiving punch and starts a five-second cooldown; a held key cannot repeat it. A fresh grounded E press begins the hidden hold attempt; if held for 0.five seconds it clears up to three cacti in reach, consumes the cooldown whether successful or not, and requires release/re-press for another attempt. A held key that began on the ground never becomes an airborne punch, and the combo never attacks flying enemies. Space/Up while riding dismounts and launches the dinosaur, removing the old ridden pterodactyl; airborne or ridden contact with another pterodactyl cannot stun.

### Collision and update order

Each running frame performs: decrement transient timers; end an expired ride; update score and bounded speed; update dinosaur physics; move cactus clusters and flying enemies; synchronize a mounted dinosaur; update punch hitbox; resolve punch hits; resolve descending cactus stomps; resolve descending pterodactyl stomps and start any ride; remove cacti touching the ridden pterodactyl; resolve one-time pterodactyl stun; resolve fatal cactus side/underside collision; if fatal, freeze the scene and start the 0.5-second death-overlay delay; remove spent enemies; replenish cleared cactus slots; then draw.

Stomp detection uses the dinosaur previous/current bottom values plus a direct bottom-edge touch check. A valid crossing or edge touch places the dinosaur at the cactus top for the frame, removes that cactus, and awards 50.

### Spawning, feedback, and shutdown

Use randomized single, pair, and three-cactus patterns with a seedable random generator for tests. Stage randomized safe groups beyond the right edge, replenish only when a cactus is stomped/cleared, never exceed 12 active cacti, and never spawn a new pattern overlapping an existing one. Spawn pterodactyls on a deterministic height cycle, allow a descending stomp to turn one into a cactus-level ride that removes cacti on contact for five seconds, and remove it after the ride ends or it passes the left boundary.

Draw hazards and feedback with Pygame primitives, load the bundled dino PNG after the display is initialized, and scale it with nearest-neighbor pixels. Show score, BEST, GAME OVER/restart instructions, punch/combo/ride notifications, a ride countdown, and a small stun indicator. Initialize Pygame, fonts, display, and clock only inside main(). Use try/finally so both QUIT and Escape reach pygame.quit().

## Verification Slices

1. Write deterministic tests and implement the module-safe configuration, GameState, dinosaur physics, cactus clusters, stomp resolution, and minimal scene.
2. Add pterodactyl movement, airborne E edge handling, punch hitbox, bonus scoring, and one-time stun behavior.
3. Add grounded combo hold/cooldown, deterministic clusters, bounded replenishment, survival score, and difficulty cap.
4. Add restart/UI/exit handling, run compile/import/unit checks, and execute the documented manual smoke scenarios.

## Post-Implementation Constitution Re-check

The final validation must confirm that the game remains a focused standalone Day3 exercise, that all new timers and states reset, that collision occurs after movement and before drawing, and that no unrelated dirty worktree changes are included.

## Complexity Tracking

No constitution violations are expected. CactusCluster preserves compact groups while allowing shared boundary reflection; randomized selection remains seedable for tests and no broader engine abstraction is introduced.

    
## Latest Ability Slice

GameSession keeps helper, rainbow, dig, inverted-universe, and held-key fields transient. W begins red normal-background rainbow mode for 15 seconds with a 60-second cooldown. In the inverted universe W leaves the black background unchanged and animates only cactus and pterodactyl palettes. R creates a five-second cactus-level helper with a 30-second cooldown; contact clears do not score. D adds progress on a tap or continuously while held only when grounded, exits the bottom of the screen before changing universe in either direction, and returns to normal only after a full second dig. Airborne D is ignored.

The default BEST path is resolved from the current user's local application-data directory. Loading and saving are best-effort, and reset preserves the loaded record while clearing every run-specific ability field.


## Latest Player-Requested Revision Slice

The mounted pterodactyl remains active for five seconds, but Space/Up can end the ride early by removing the ridden enemy and launching the dinosaur. The dinosaur can then stomp another pterodactyl; other pterodactyls cannot stun it while it is airborne or mounted. D digging advances until the dinosaur exits the bottom edge, at which point the dinosaur is restored to the ground and the inverted universe begins. After a fatal cactus collision, GAME_OVER freezes score and gameplay for 0.5 seconds while the last scene remains drawable. Once the delay expires, the loss overlay is shown. During GAME_OVER, Space/Up spends 500 points and carries the remainder into an automatic jumping restart when possible; R always performs a zero-score standing restart.


## Latest Universe and Ground Revision

D digging now has the same bottom-exit transition in both directions. The target is captured when a fresh D press begins: normal targets inverted, and inverted targets normal. The dinosaur remains visibly in the downward traversal until it exits the screen; only then is it reset to the ground and the target universe activated. The floor below the ground line uses the normal background color ordinarily and WHITE during rainbow or inverted mode; the line itself is BLACK in normal/rainbow mode and WHITE in the inverted universe.


## Latest Input Guard

The dig state may start only when Dinosaur.is_grounded is true. An airborne D press does not alter the jump, does not bypass gravity, and does not select a destination universe.
