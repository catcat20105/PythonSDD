# Tasks: Chrome Dinosaur Stomp Runner

Input: Design documents from /specs/001-chrome-dinosaur-game/

Prerequisites: plan.md, spec.md, research.md, data-model.md, contracts/ui.md, quickstart.md

Tests: Included because the feature specification explicitly requires deterministic automated checks.

## Phase 1: Setup

Purpose: Synchronize the feature documentation and establish the Day3 exercise boundary.

- [X] T001 Update specs/001-chrome-dinosaur-game/spec.md with stomp, bounce, punch, stun, combo, scoring, reset, and exit requirements.
- [X] T002 [P] Update specs/001-chrome-dinosaur-game/plan.md, research.md, data-model.md, and quickstart.md with the approved design decisions.
- [X] T003 [P] Add the keyboard, rendering, frame-order, and shutdown contract in specs/001-chrome-dinosaur-game/contracts/ui.md.

## Phase 2: Foundational

Purpose: Create the module-safe runtime structure shared by every story.

- [X] T004 Create the Day3 exercise directory and keep Pygame initialization inside main() in Day3/prj07.py.
- [X] T005 Centralize configuration constants and define GameState, Dinosaur, Cactus, CactusCluster, FlyingEnemy, PunchHitbox, and GameSession interfaces in Day3/prj07.py.

## Phase 3: User Story 1 - Run and Stomp Cacti (Priority: P1) MVP

Goal: Deliver a playable runner with jumping, persistent bouncing cacti, stomp scoring, and fatal cactus collision.

Independent Test: Run the deterministic US1 tests, then launch the window, jump over/onto cacti, and intentionally side-collide.

### Tests for User Story 1

- [X] T006 [US1] Add tests in Day3/test_prj07.py for jump gating, landing clamp, cactus reflection, stomp crossing, side collision, and initial/reset staging.

### Implementation for User Story 1

- [X] T007 [US1] Implement dinosaur delta-time physics and grounded jump rules in Day3/prj07.py.
- [X] T008 [US1] Implement shared-direction cactus clusters, boundary reflection, randomized single/pair/triple patterns, and bounded replenishment in Day3/prj07.py.
- [X] T009 [US1] Implement stomp-versus-fatal-collision resolution and the minimal running scene/rendering in Day3/prj07.py.

## Phase 4: User Story 2 - Punch Flying Enemies (Priority: P2)

Goal: Add airborne press-only E punches, pterodactyl targets, punch bonuses, and nonfatal one-time stun.

Independent Test: Jump, press E against a pterodactyl, verify its removal and bonus, then verify a missed contact stuns without game over.

### Tests for User Story 2

- [X] T010 [US2] Add tests in Day3/test_prj07.py for airborne-only E, punch duration/cooldown, held-key suppression, enemy destruction, and one-time stun.

### Implementation for User Story 2

- [X] T011 [US2] Implement deterministic pterodactyl movement, height variants, drawing, and off-screen removal in Day3/prj07.py.
- [X] T012 [US2] Implement E key-edge handling, short forward punch hitbox, punch bonus, and same-frame hit precedence in Day3/prj07.py.
- [X] T013 [US2] Implement brief stun timers, input blocking during stun, and per-enemy contact suppression in Day3/prj07.py.

## Phase 5: User Story 3 - Discover the Grounded Cactus Combo (Priority: P2)

Goal: Add the hidden grounded hold-E up-to-three-cactus combo and its cooldown behavior.

Independent Test: Trigger the combo with up to three close cacti, then make an empty attempt and verify the 15-second cooldown.

### Tests for User Story 3

- [X] T014 [US3] Add tests in Day3/test_prj07.py for up-to-three target detection, partial/successful/failed combo scoring, one-attempt-per-hold, and cooldown blocking.

### Implementation for User Story 3

- [X] T015 [US3] Implement grounded E hold tracking, up-to-three forward target matching, cooldown consumption, and capped target clearing in Day3/prj07.py.
- [X] T016 [US3] Add survival score, stomp/punch/combo bonus composition, visible notifications, and difficulty speed cap in Day3/prj07.py.

## Phase 6: User Story 4 - Track the Run and Restart (Priority: P3)

Goal: Complete UI feedback, restart variants, state freezing, and clean shutdown.

Independent Test: Reach game over, verify frozen state, restart standing and jumping, and exit through Escape and the close control.

### Tests for User Story 4

- [X] T017 [US4] Add tests in Day3/test_prj07.py for score freeze, complete reset, standing/jumping restart, import safety, and capped difficulty.

### Implementation for User Story 4

- [X] T018 [US4] Implement READY/GAME_OVER overlays, score HUD, restart input, and all transient-state resets in Day3/prj07.py.
- [X] T019 [US4] Implement main() event translation, clock loop, draw order, Escape/QUIT handling, and pygame.quit() cleanup in Day3/prj07.py.

## Phase 7: Polish and Validation

Purpose: Validate the full feature and keep the change focused.

- [X] T020 [P] Run py_compile, import, and unittest checks from specs/001-chrome-dinosaur-game/quickstart.md.
- [X] T021 [P] Perform the manual smoke scenarios in specs/001-chrome-dinosaur-game/quickstart.md and record any balance fixes in named constants only.
- [X] T022 Review git diff and git status to confirm only the new Day3 feature and updated spec artifacts are part of this work; preserve unrelated existing changes.

## Phase 8: Player-requested balance, randomness, and score record

- [X] T023 Tune dinosaur jump height, elevate pterodactyl flight lanes, slow post-edge cactus travel, and shorten the grounded combo hold to 0.five seconds.
- [X] T024 Replace the five-target-only combo with a randomized-spawn-compatible combo that clears up to three cacti, including non-cluster singles and pairs, and removes a cactus on bottom-edge stomp contact.
- [X] T025 Add seeded random cactus pattern/spacing selection, per-local-user persistent BEST tracking/HUD, bundled monochrome dino asset loading, and regression coverage.

## Phase 9: Player-requested combat and bounce tuning

- [X] T026 [US2] Make the airborne punch forgiving, press-only, and subject to a five-second cooldown; add coverage for distant hit detection and cooldown blocking.
- [X] T027 [US1] Add first- and second-bounce cactus speed tiers so the first return is slower and later returns are only slightly faster.
- [X] T028 [US2] Add descending pterodactyl stomps that mount the dinosaur at cactus height for five seconds and remove cacti on contact without awarding a separate bonus.
- [X] T029 [P] Synchronize spec.md, plan.md, research.md, data-model.md, quickstart.md, and contracts/ui.md with the final combat and bounce behavior.

## Dependencies and Execution Order

- Setup (Phase 1) precedes Foundational (Phase 2).
- Foundational work precedes every user story.
- US1 is the MVP and precedes the interaction stories because they use its session and entity loop.
- US2 and US3 share Day3/prj07.py and should be completed sequentially even though their tests are independently scoped.
- US4 follows the interaction stories and owns final loop/shutdown integration.
- Polish follows all desired stories.

## Parallel Opportunities

- T002 and T003 can run in parallel with each other.
- Test files and documentation can be prepared independently before the main implementation, but tasks touching Day3/prj07.py remain sequential.
- T020 and T021 can run in parallel after implementation; T022 follows both.

## Implementation Strategy

1. Complete the documentation and module-safe foundation.
2. Implement and validate US1 as the playable MVP.
3. Add airborne punching and stun, then the grounded combo and scoring.
4. Finish restart/UI/shutdown behavior.
5. Run every automated and manual quickstart check before handoff.

    
## Phase 10: Player-requested abilities and persistent BEST

- [X] T030 Add W exact-red rainbow mode with a 15-second active event, 60-second cooldown, and inverted-world hazard-only palette behavior.
- [X] T031 Add R helper pterodactyl state with a five-second lifetime, 30-second cooldown, contact clearing, and no helper combat score.
- [X] T032 Add D tap/hold dig progress, inverted-universe toggle, black-background rule, and held-key edge protection.
- [X] T033 Persist BEST in a per-local-user JSON record with best-effort I/O and test-path injection.
- [X] T034 Add ability, palette, helper, dig, persistence, and complete-reset tests; run compile, import, and headless-render validation.
- [X] T035 Synchronize spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/ui.md, and this task list with the final controls.


## Phase 11: Latest player-requested interaction polish

- [X] T036 Update the READY and delayed GAME_OVER overlays with the exact requested wording; keep the final gameplay scene visible and frozen for 0.5 seconds after fatal cactus contact.
- [X] T037 Allow Space/Up to jump off a ridden pterodactyl, remove the old ride source, support chaining to another pterodactyl, and suppress airborne/ridden enemy stun.
- [X] T038 Make D digging continue until the dinosaur exits the bottom edge before entering the inverted universe.
- [X] T039 Add the 500-point score-preserving Space/Up revive while keeping R as the zero-score standing restart; preserve BEST.
- [X] T040 Add regression coverage and synchronize spec.md, plan.md, research.md, data-model.md, quickstart.md, contracts/ui.md, and tasks.md with the latest interaction rules.


## Phase 12: Symmetric universe digging and ground palette

- [X] T041 Make D digging continue to the bottom edge in both normal and inverted universes before switching the destination universe.
- [X] T042 Use the normal background for the floor ordinarily, switch the floor to pure white during rainbow/inverted mode, and render the line black normally/rainbow and white in the inverted universe.
- [X] T043 Add regression coverage and synchronize the universe-transition and ground-color documentation.


## Phase 13: Grounded-only dig input

- [X] T044 Reject airborne D presses so they cannot suspend jump gravity or create a flying exploit.
- [X] T045 Add regression coverage and synchronize the grounded-only dig rule across the feature artifacts.
