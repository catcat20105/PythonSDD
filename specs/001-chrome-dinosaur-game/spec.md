# Feature Specification: Chrome Dinosaur Stomp Runner

Feature Branch: 001-chrome-dinosaur-game

Created: 2026-08-27

Status: Draft

Input: User description: "Reverse Chrome Dinosaur Game; jump on cacti and punch the flying things with E for extra points"

## User Scenarios & Testing

### User Story 1 - Run and Stomp Cacti (Priority: P1)

As a player, I want a dinosaur to run automatically and stomp cacti from above so that I can clear hazards and keep the run alive.

Why this priority: Running, jumping, and cactus interaction are the core playable loop.

Independent Test: Launch the game, start a run, jump onto a cactus, and verify that the cactus disappears and the dinosaur continues running. Then allow a side collision and verify game over.

Acceptance Scenarios:

1. Given the ready scene and a grounded dinosaur, when the player presses Space or Up Arrow, the run starts and the dinosaur jumps once.
2. Given a cactus is ahead and the dinosaur is descending over it, when the dinosaur crosses the cactus top, the cactus is removed and the score increases by 50.
3. Given a cactus is ahead, when the player passes over it without stomping, the run continues, the cactus earns no points, and the cactus reverses direction at the screen edge instead of disappearing.
4. Given the dinosaur contacts a cactus from the side or underneath, when the collision is resolved, the run changes to game over.
5. Given the dinosaur is airborne, when the player presses the jump key again, no second jump starts.

### User Story 2 - Punch Flying Enemies (Priority: P2)

As a player, I want to jump and punch flying pterodactyls so that accurate timing earns extra points.

Why this priority: The airborne attack adds a second skillful interaction after the base stomp loop works.

Independent Test: Start a run, jump, press E while airborne as a pterodactyl enters the forward attack area, and verify that it is destroyed and the bonus is shown. Let another pterodactyl touch the dinosaur without a punch and verify the nonfatal stun.

Acceptance Scenarios:

1. Given the dinosaur is airborne, when the player makes a fresh E key press, a forgiving short forward punch hitbox appears immediately and the five-second punch cooldown begins.
2. Given the punch hitbox overlaps a pterodactyl, when the hit is resolved, the pterodactyl is destroyed and the score increases by 100.
3. Given the dinosaur is descending over a pterodactyl, when its bottom crosses the pterodactyl top, the dinosaur mounts it at cactus height for five seconds and each cactus touching the ridden pterodactyl disappears.
4. Given E is held down during a jump, when frames continue, the same key hold does not create repeated punches.
5. Given a pterodactyl touches the dinosaur without being punched or stomped, when the collision is resolved, the dinosaur is stunned briefly, the run continues, and no enemy bonus is awarded.
6. Given the dinosaur is grounded, when E is pressed without the secret combo conditions, no normal punch is created.

### User Story 3 - Discover the Grounded Cactus Combo (Priority: P2)

As a player, I want a hidden grounded E move that can clear up to three nearby cacti so that exploration and timing can produce a useful combo.

Why this priority: The Easter egg is an optional scoring layer that depends on the cactus collection and grounded input state.

Independent Test: Place one to three cacti ahead, hold E while grounded, and verify that up to three are cleared and the combo bonus appears. Repeat with no target and verify that the attempt is wasted and the cooldown starts.

Acceptance Scenarios:

1. Given the dinosaur is grounded and one to three cacti are ahead, when the player holds E for the combo trigger, up to three cacti are cleared and the score increases by 50 per cleared cactus.
2. Given the player has triggered the grounded combo, when E remains held, no second combo attempt occurs until E is released and pressed again.
3. Given no qualifying cactus is ahead, when the player triggers the grounded combo, no cactus is cleared, no points are awarded, and the 15-second cooldown begins.
4. Given the grounded combo cooldown is active, when the player presses or holds E, the attempt is ignored.
5. Given E was pressed while grounded and remains held, when the dinosaur jumps, the held key does not become an airborne punch; E must be released and pressed again in the air.

### User Story 4 - Use W, R, and D Abilities (Priority: P2)

As a player, I want temporary visual and helper abilities that change the challenge without breaking the runner loop.

Acceptance Scenarios:

1. Given a normal running session, a fresh W press starts exact-red background rainbow mode for 15 seconds and then returns to normal; its cooldown is 60 seconds.
2. Given the inverted universe, a fresh W press leaves the background pure black while only cacti and pterodactyls cycle hue.
3. Given a ready R cooldown, a fresh R press summons a helper pterodactyl for five seconds; it clears contacted hazards without awarding points and has a 30-second cooldown.
4. Given a normal running session, one D press advances dig progress and holding D advances it continuously until the inverted universe begins.
5. Given the inverted universe, releasing D and making a fresh D press starts a downward dig; holding D until the dinosaur exits the bottom returns to the normal universe.

### User Story 5 - Track the Run and Restart (Priority: P3)

As a player, I want visible score, increasing speed, clear game-over feedback, restart controls, and clean exit behavior so that I can play repeated sessions.

Why this priority: Score, difficulty, reset, and shutdown complete the game loop after interactions are reliable.

Independent Test: Survive long enough for score and speed to increase, intentionally hit a cactus, verify that score freezes, restart with R and Space, and exit with Escape and the close button.

Acceptance Scenarios:

1. Given an active run, when time passes without game over, the displayed score increases monotonically and the scroll speed eventually steps up.
2. Given the dinosaur has been hit by a cactus, when the collision update completes, movement and score updates stop; the frozen gameplay scene remains visible for 0.5 seconds, then the game-over/restart instruction is visible.
3. Given the game-over state, when the player presses R, a fresh running scene starts standing with initial score and speed, reset dinosaur motion, cleared transient state, and freshly staged cacti.
4. Given the game-over state, when the player presses Space or Up Arrow, a fresh run starts with the dinosaur jumping immediately.
5. Given any state, when the player presses Escape or closes the window, the game exits cleanly.

## Edge Cases

- A jump request while airborne or stunned is ignored.
- A held E key produces neither repeated airborne punches nor repeated grounded combo attempts.
- Punch hits are resolved before a same-frame pterodactyl contact, so a valid punch prevents the stun.
- A stomp is valid when a descending dinosaur crosses a cactus top or its bottom edge directly touches the cactus top; side and deep underside contact remain fatal.
- Cacti reverse only at the boundary in their current travel direction, use a slower first reflected return and a slightly faster second reflected return, and remain active until stomped or cleared by the combo.
- Cactus spawning uses random singles, pairs, and three-cactus groups without exceeding 12 active cacti; the combo can clear up to three cacti in reach.
- A failed grounded combo attempt consumes its cooldown even when no cacti are in range.
- A pterodactyl can be stomped from above to mount the dinosaur at cactus height for five seconds; only cacti touching the ridden pterodactyl disappear, and the ride does not attack flying enemies.
- A pterodactyl can stun the dinosaur only once per encounter.
- Difficulty speed never exceeds its configured maximum.
- Restart clears all old cacti, enemies, punch state, cooldowns, stun time, score, elapsed time, and dinosaur velocity.
- Both Pygame QUIT and Escape use the same clean shutdown path.

## Requirements

### Functional Requirements

- FR-001: The system MUST launch as an offline Python/Pygame desktop game using the existing dependency baseline.
- FR-002: The system MUST display a fixed-size scene with a dinosaur, ground line, cacti, flying pterodactyls, score, and state feedback.
- FR-003: The dinosaur MUST remain in a fixed horizontal lane while the world moves horizontally.
- FR-004: Space and Up Arrow MUST start a ready run or request a jump while grounded.
- FR-005: Jump physics MUST use upward velocity, gravity, and a ground clamp, and MUST prevent double jumping.
- FR-006: Cacti MUST be represented as ground hazards that move left initially, reverse at the left and right playfield boundaries, and use a slower first reflected return followed by a slightly faster second reflected return.
- FR-007: A valid descending cactus stomp MUST remove one cactus and award 50 points.
- FR-008: A side or underside cactus collision MUST transition the run to game over outside an active pterodactyl ride or an active dig.
- FR-009: The system MUST spawn random cactus singles, pairs, and three-cactus groups without exceeding 12 active cacti; seeded sessions MUST remain available for tests.
- FR-010: Flying pterodactyls MUST move through the scene at several configured heights and leave the scene after passing the left boundary.
- FR-011: A fresh E press while airborne MUST create one forgiving short forward punch hitbox, subject to a five-second punch cooldown; holding E MUST NOT repeat it.
- FR-012: A punch hit MUST remove one pterodactyl and award 100 points.
- FR-013: A missed pterodactyl contact MUST stun the dinosaur for a brief configured duration without ending the run or awarding points, and the same enemy MUST NOT retrigger that stun.
- FR-014: A grounded E hold MUST offer one hidden combo attempt only when the dinosaur is grounded and the combo cooldown is ready.
- FR-015: The grounded combo MUST clear between one and three cacti ahead within 320 pixels and award 50 points per cleared cactus, capped at 150.
- FR-016: A grounded combo attempt MUST consume a 15-second cooldown whether it succeeds or fails.
- FR-017: The system MUST increase survival score and scrolling difficulty during active play while enforcing a maximum speed.
- FR-018: Score, movement, and spawning MUST stop after game over.
- FR-019: R MUST restart into a standing run with zero run score; Space/Up MUST restart into a jumping run, consuming 500 points when available and carrying the remaining score, or starting from zero when fewer than 500 points are available.
- FR-020: Restart MUST reset every run-specific value and transient input/combat value while preserving the all-time local-user BEST record.
- FR-021: Escape and window close MUST exit through a clean Pygame shutdown path.
- FR-022: Game constants and state transitions MUST be named and centralized for manual debugging and deterministic tests.
- FR-023: The game MUST remain offline and use project-bundled generated PNG artwork plus Pygame primitives; it MUST NOT require downloaded assets, audio, network services, or remote persistence; a small local high-score record is allowed.
- FR-024: Importing the game module MUST not initialize a display or start the game loop.
- FR-025: The dinosaur artwork MUST be a minimal pixelated pure-black silhouette with one pure-white rectangular eye, with a primitive fallback if the local asset is unavailable.
- FR-026: BEST MUST be the maximum score reached by this local OS user across process restarts, loaded and saved as a small user-local JSON record; restart MUST NOT clear it.
- FR-027: A descending pterodactyl stomp MUST mount the dinosaur on that enemy at cactus height for five seconds; each cactus MUST disappear when it touches the ridden pterodactyl.
- FR-028: The normal airborne punch MUST use a press edge rather than a hold and MUST not attack grounded combo targets.
- FR-029: W MUST begin an exact-red 15-second rainbow background event with a 60-second fresh-press cooldown.
- FR-030: In the inverted universe, W MUST leave the background pure black and animate hue only for cacti and pterodactyls.
- FR-031: R MUST summon a helper pterodactyl for five seconds with a 30-second cooldown; helper contacts clear hazards without awarding points.
- FR-032: D MUST advance dig progress only while the dinosaur is grounded; a fresh grounded press MUST select the opposite universe, and the universe MUST change only after the dinosaur exits the bottom of the screen.
- FR-033: Ability edge state, timers, cooldowns, dig progress, and universe state MUST reset on restart while BEST is preserved.
- FR-034: Space/Up while riding a pterodactyl MUST dismount and launch the dinosaur; the ridden pterodactyl MUST disappear so a later pterodactyl can be ridden.
- FR-035: A pterodactyl contact MUST NOT stun the dinosaur while the dinosaur is airborne, riding, or actively digging.
- FR-036: A fatal cactus hit MUST freeze the visible gameplay scene for exactly 0.5 seconds before the loss overlay is drawn.
- FR-037: The below-ground floor MUST use the normal background color in ordinary mode and pure white while rainbow or inverted mode is active; the ground line MUST be black in normal/rainbow modes and white in the inverted universe.
- FR-038: An airborne D press MUST be ignored and MUST NOT suspend gravity, start digging, or move the dinosaur into a universe transition.

### Key Entities

- Dinosaur: Fixed-lane player avatar with vertical physics, grounded state, previous/current bottom positions, stun state, and draw behavior.
- Cactus: Ground hazard with a rectangle and variant dimensions.
- CactusCluster: One or more cacti that move together, reverse at boundaries, and can be reduced by stomps or the grounded combo.
- FlyingEnemy: Stylized pterodactyl with a rectangle, height variant, movement state, and one-time contact state.
- PunchHitbox: Short-lived forward attack rectangle created by an airborne E press.
- GameSession: Owns state, entities, score, timers, speed, input edge state, cooldowns, and restart transitions.
- Game Configuration: Named constants for dimensions, physics, spawn patterns, score bonuses, cooldowns, colors, and speed limits.

## Success Criteria

### Measurable Outcomes

- SC-001: From a clean checkout with the documented dependency installed, the game opens to a playable scene within 5 seconds.
- SC-002: During a 30-second run, the window remains responsive near the 60 FPS target without visible stutter.
- SC-003: A player can stomp a reachable cactus and see it removed with a 50-point increase while the dinosaur stays above the ground line.
- SC-004: A player can hit a reachable pterodactyl with one forgiving airborne E press and see a 100-point increase; a missed contact produces a brief nonfatal stun, while a stomp starts the cactus sweep.
- SC-005: A grounded combo clears one to three nearby cacti and awards 50 points per clear, capped at 150; an empty attempt blocks another attempt for 15 seconds.
- SC-006: During a surviving 20-second run, score increases monotonically and the scrolling speed increases at least once without exceeding its maximum.
- SC-007: After game over, both restart controls produce the documented standing/jumping reset behavior with no leaked transient state.
- SC-008: Escape, window close, game over, and restart flows complete without an unhandled exception or lingering Pygame window.
- SC-009: The BEST HUD value never decreases during a session and survives both restart styles.
- SC-010: A player can stomp a pterodactyl, ride it at cactus height for five seconds, and observe each cactus disappear on contact with the ridden pterodactyl.
- SC-011: W starts the documented normal and inverted rainbow palettes with the exact durations and cooldown.
- SC-012: R summons a helper that clears contacted hazards for five seconds and cannot be immediately resummoned.
- SC-013: D tap/hold reaches the inverted universe, and a fresh D press followed by another bottom-exit dig returns to normal.
- SC-017: The below-ground floor uses the normal background in ordinary mode and pure white in rainbow/inverted modes, while the ground line is black in normal/rainbow modes and white in the inverted universe.
- SC-014: BEST survives closing and reopening the process for the same local user.
- SC-015: A fatal cactus hit leaves the last gameplay scene visible for 0.5 seconds before showing the loss overlay.
- SC-016: A game-over Space/Up revive consumes exactly 500 points when the score is sufficient and carries the remaining score into the new jumping run; R still resets to zero.

## Assumptions

- “Flying idk name things” means stylized pterodactyls.
- Passing over a cactus is safe but does not remove it; side and underside contact remains fatal as in the original runner design.
- A missed pterodactyl is nonfatal; direct contact produces a 0.5-second stun and the enemy cannot retrigger that stun.
- Normal airborne punches use a forgiving 0.12-second hitbox and five-second cooldown; only fresh E key presses qualify, so releasing and pressing E is required for another attempt.
- The hidden grounded combo triggers after a 0.five-second hold, clears up to three cacti ahead within 320 pixels, has a 15-second cooldown, and does not attack flying enemies.
- Each cactus cleared by the combo contributes the regular 50-point reward, up to 150 points for three targets, and the notification shows COMBO xN.
- Survival score uses 10 points per active second and is added to interaction bonuses.
- The target is a Windows desktop keyboard using the project virtual environment; BEST is stored best-effort for the current local user and is not an online record.

    
## Latest Ability Details

- W is a fresh key press. It starts a 15-second rainbow event at exact RGB (255, 0, 0), then returns the normal background and remains unavailable until its 60-second cooldown expires.
- R is a fresh key press. It summons a front-line pterodactyl helper for five seconds and starts a 30-second cooldown. The helper clears cacti and flying enemies on contact without awarding points.
- D is both a tap and hold control in either universe. A tap advances dig progress; holding advances it continuously until the dinosaur exits the bottom. The destination universe is then entered, and the held key cannot toggle repeatedly.
- In the inverted universe the background is black, the below-ground floor is white, and the ground line is white. W changes hue only for cacti and pterodactyls; it does not change the background.
- BEST is persisted for the current local OS user in a best-effort JSON file and survives closing and reopening the game.


## Latest Player-Requested Revisions

- The start scene shows only DINO GAME and PRESS SPACE KEY TO START; after the death delay, the loss scene shows ARE YOU TRYING TO EAT THE CACTUS?, YOU LOSE, and PRESS SPACE TO RESTART.
- Jumping while riding a pterodactyl launches the dinosaur, removes the old ridden pterodactyl, and permits chaining onto another pterodactyl. Pterodactyl contact cannot stun the dinosaur while it is airborne or riding.
- A D hold moves the dinosaur downward until it exits the bottom of the screen before entering the selected destination universe. The same full dig is required to leave the inverted universe, and digging is intentionally slower than a jump.
- Space/Up during GAME_OVER is the score-preserving revive when the score is at least 500: it subtracts 500 and starts a jumping run with the remainder. R always starts a standing run with zero score.
- A fatal cactus collision freezes the final gameplay frame for 0.5 seconds before the loss overlay appears; the score and world remain frozen during that interval.


## Latest Universe and Ground Rules

- D is symmetric but grounded-only: from the ground in the normal universe it digs to the inverted universe; from the ground in the inverted universe it digs until the dinosaur exits the bottom and then returns to normal. Airborne D presses are ignored.
- D does not teleport between universes. The dinosaur is reset to the ground only after the bottom-exit transition completes.
- The floor below the ground line uses the normal background color ordinarily and pure white during W rainbow or inverted mode. The ground line itself is black in normal and W rainbow mode, then white in the inverted universe.


## Latest Dig Input Rule

D can begin or continue a universe transition only from the ground. Pressing D during a jump is ignored, leaves normal jump physics active, and cannot make the dinosaur fly.
