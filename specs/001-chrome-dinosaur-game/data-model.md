# Data Model: Chrome Dinosaur Stomp Runner

## Configuration

Module constants define window size, ground position, frame rate, dinosaur physics, obstacle dimensions, deterministic patterns, movement speeds, score rates, bonuses, attack durations, stun duration, combo rules, ability durations, colors, and spawn limits. Only the BEST record is persisted.

Important invariants:

- 0 < GROUND_Y < SCREEN_HEIGHT.
- The dinosaur’s bottom never remains below GROUND_Y after physics update.
- Scroll speed remains between INITIAL_SCROLL_SPEED and MAX_SCROLL_SPEED.
- Active cacti never exceed MAX_ACTIVE_CACTI.
- Cacti reflect only at the boundary in their current direction, use a slower first reflected return and slightly faster second reflected return, and are removed only by a valid stomp, combo clear, or contact with the ridden pterodactyl.
- A grounded combo attempt starts its cooldown even when it finds no valid target; a successful attempt clears at most three cacti.
- The floor below the ground line uses the normal background color ordinarily and WHITE during rainbow or inverted state; the ground line is BLACK in normal/rainbow state and WHITE in inverted state.
- is_digging can start only from a grounded dinosaur; airborne D input leaves the normal physics update untouched.

## Dinosaur

| Field | Type | Meaning / invariant |
|---|---|---|
| rect | pygame.Rect | Current collision/drawing bounds; x remains in the player lane. |
| position_y | float | Subpixel vertical position used for stable delta-time physics. |
| ground_y | int | Ground clamp coordinate. |
| velocity_y | float | Negative while rising, positive while falling. |
| is_grounded | bool | True only when standing on the base ground. |
| previous_bottom | float | Bottom position before the most recent physics update. |
| previous_velocity_y | float | Vertical direction before the most recent update. |

Operations:

- reset(): restore the lane, ground position, zero velocity, and grounded state.
- jump(): apply the upward impulse only if grounded.
- update(dt): apply gravity, update position, and clamp to the ground.
- land_after_stomp(cactus_top): place the dinosaur at the crossed cactus top and continue falling toward the base ground.
- draw(surface, sprite): render the bundled minimal black-and-white pixel sprite when available, otherwise use the pure-black primitive fallback with one white rectangular eye.

## Cactus and CactusCluster

Cactus represents one rectangular ground target. It owns a variant index and rectangle, and can be removed by a stomp or combo.

CactusCluster owns a non-empty list of cacti, a shared horizontal direction, a has_bounced flag, and a bounce_count. Before its first edge reflection, members move together at the current scroll speed. After the first reflection, the cluster uses CACTUS_BOUNCE_SPEED (125 pixels per second); after the second and later reflections, it uses CACTUS_SECOND_BOUNCE_SPEED (155 pixels per second). The cluster remains active while at least one member remains.

Randomized pattern sizes are one, two, and three cacti. A seedable session generator makes the random sequence repeatable for tests, while normal sessions use a fresh random sequence. Combo target selection is based on forward reach and caps at three cacti.

## FlyingEnemy

| Field | Type | Meaning / invariant |
|---|---|---|
| rect | pygame.Rect | Current pterodactyl bounds. |
| position_x | float | Subpixel horizontal position. |
| height_index | int | Selects a configured flight level. |
| contact_handled | bool | Prevents repeated stun from one enemy encounter. |
| is_sweeper | bool | True while the pterodactyl is the active ride/sweep source. |
| is_ridden | bool | True while the dinosaur is mounted and positioned on top of this enemy. |

Operations:

- update(dt, scroll_speed): move left through the elevated configured levels (190, 145, and 210), or hold position at cactus height while ridden.
- activate_cactus_sweep(rider_rect): move to cactus height, center beneath the rider, and mark the enemy as the active ride/sweep source.
- release_rider(): return to the original flight level when the ride timer expires.
- is_off_screen(): true once the right edge leaves the left side.
- draw(surface): render wings, body, beak, and eye with primitives.

## PunchHitbox

| Field | Type | Meaning / invariant |
|---|---|---|
| rect | pygame.Rect | Forward attack bounds anchored to the dinosaur. |
| remaining_seconds | float | Starts at PUNCH_DURATION and expires at zero. |
| has_hit | bool | At most one pterodactyl receives credit from a punch. |

A hitbox can be created only by a fresh E key press while airborne, never by held-key polling or a grounded normal punch. The forgiving hitbox lasts 0.12 seconds and its request starts a five-second cooldown.

## GameState

- READY: reset values, grounded dinosaur, staged cacti, and no simulation until a start/jump input.
- RUNNING: active physics, movement, collision, scoring, spawning, attack, stun, ride, and combo timers.
- GAME_OVER: frozen simulation and score; the last gameplay scene is drawable while death_overlay_delay_remaining is positive, then restart feedback is drawn.

Stun is a transient timer within RUNNING, not a separate top-level state. While stunned, jump and punch requests are ignored, but physics, world movement, and survival score continue.

## GameSession

| Field | Type | Meaning / invariant |
|---|---|---|
| state | GameState | Current top-level run state. |
| dinosaur | Dinosaur | Single player avatar. |
| cactus_clusters | list[CactusCluster] | Bounded active ground hazards. |
| flying_enemies | list[FlyingEnemy] | Active pterodactyls. |
| punch_hitbox | PunchHitbox or None | Current one-shot airborne attack. |
| elapsed_seconds | float | Active run time; changes only in RUNNING. |
| survival_score | int | Time-based score component. |
| bonus_score | int | Stomp, punch, and combo rewards. |
| high_score | int | All-time maximum score loaded for the current local user; restart does not clear it. |
| scroll_speed | float | Derived bounded world speed. |
| death_overlay_delay_remaining | float | Nonnegative 0.5-second countdown between a fatal cactus hit and the loss overlay; gameplay remains frozen while it is positive. |
| stun_remaining | float | Nonnegative pterodactyl stun timer. |
| cactus_sweep_remaining | float | Nonnegative five-second ride timer during which the ridden pterodactyl removes touching cacti. |
| riding_enemy | FlyingEnemy or None | The pterodactyl currently carrying the dinosaur, if any. |
| punch_cooldown | float | Time before another airborne punch can be requested. |
| combo_cooldown | float | Time before another grounded combo attempt can begin. |
| e_is_held | bool | Edge state preventing held-key repeats. |
| combo_hold_elapsed | float | Progress for the current grounded hold attempt. |
| combo_attempt_pending | bool | True between grounded E press and trigger. |

Derived score equals survival_score + bonus_score. high_score is the maximum derived score observed and saved for the current local user.

Operations:

- reset(): clear all run entities and timers, re-seed the session generator, stage a fresh randomized cactus sequence, and return to READY without clearing high_score.
- start(): transition READY to RUNNING.
- request_jump(): start from READY or jump only when running, grounded, and not stunned.
- request_punch(): create a punch only when running, airborne, unstunned, and off cooldown.
- handle_key_down(key) / handle_key_up(key): implement Space/Up, E, W, R, and D edge semantics.
- restart(auto_jump, carried_score=0): reset all run fields, enter RUNNING, carry a nonnegative score remainder, and optionally jump immediately.
- update(dt): no-op outside RUNNING; otherwise execute the documented update order.
- draw(surface, fonts): render the current scene and feedback without changing game state.

## State Transitions

| Current | Event / condition | Action | Next |
|---|---|---|---|
| READY | Space or Up | Start and jump | RUNNING |
| READY | Other gameplay input | No simulation change | READY |
| RUNNING | Space/Up while grounded and unstunned | Apply jump impulse | RUNNING |
| RUNNING | Space/Up while airborne or stunned | Ignore, except Space/Up while riding dismounts and launches | RUNNING |
| RUNNING | Airborne fresh E | Create punch if off cooldown | RUNNING |
| RUNNING | Grounded fresh E | Begin combo hold if off cooldown; success clears up to three cacti | RUNNING |
| RUNNING | Fresh W | Start rainbow if its cooldown is ready | RUNNING |
| RUNNING | Fresh R | Summon helper if its cooldown is ready | RUNNING |
| RUNNING | Fresh/held D while grounded | Advance the selected bottom-exit dig in either universe | RUNNING |
| RUNNING | Fresh D while airborne | Ignore input and keep jump physics active | RUNNING |
| RUNNING | Valid cactus stomp | Remove cactus and add 50 | RUNNING |
| RUNNING | Fatal cactus side/underside collision | Freeze session and start the 0.5-second death-overlay delay | GAME_OVER |
| RUNNING | Descending pterodactyl stomp | Mount the dinosaur at cactus height and start the five-second ride | RUNNING |
| RUNNING | Pterodactyl contact without punch or stomp | Set one-time stun timer | RUNNING |
| GAME_OVER | Space/Up | Spend 500 points and carry the remainder when possible; reset, start, and jump | RUNNING |
| GAME_OVER | R | Reset and start standing | RUNNING |
| Any | Escape or QUIT | Exit loop and call pygame.quit() | Exit |

## Collision Rules

1. Move dinosaur, cacti, and enemies before collision checks.
2. Resolve punch hits before enemy body contacts.
3. A stomp requires horizontal overlap, previous dinosaur bottom at or above the cactus top, current bottom at or below the top, and descending motion.
4. After stomp resolution, any remaining cactus overlap from the side or underside is fatal.
5. A descending pterodactyl stomp is checked using previous/current dinosaur bottoms, mounts the dinosaur at cactus height for five seconds, and removes each cactus that touches the ridden pterodactyl.
6. A pterodactyl contact sets stun only once per enemy and does not award points; airborne, mounted, and actively digging dinosaurs are immune to this contact stun.
7. A fatal cactus transition freezes the scene and score; update() only counts down death_overlay_delay_remaining until the loss overlay becomes eligible.
8. Space/Up while mounted removes the ridden enemy before launching the dinosaur, so the old ride source cannot be reused.

## Reset Invariant

After reset() or restart(), the session has initial score and speed, zero elapsed time, grounded dinosaur, no flying enemies or ride, no punch, zero stun/ride/cooldown timers, released E state, a bounded randomized cactus sequence, and the documented next state.

    
## Latest Ability Fields

GameSession also owns helper_enemy, helper_remaining, and helper_cooldown for the R helper; rainbow_remaining, rainbow_cooldown, and rainbow_elapsed for W; dig_progress and is_inverted for D; and w_is_held, r_is_held, d_is_held, and dig_toggle_blocked for key edges.

A fresh W starts the red-to-rainbow background event for 15 seconds and consumes a 60-second cooldown. When is_inverted is true, the background remains black and only cactus and pterodactyl palettes use the rainbow hue. A fresh R creates an is_helper pterodactyl at cactus height for five seconds and consumes a 30-second cooldown. Helper contact removes cacti and other flying enemies without score and the helper is excluded from punch, stomp, and stun logic.

A D tap adds DIG_TAP_AMOUNT. While D remains held, progress advances using delta time until the dinosaur exits the bottom. A fresh D press selects the opposite universe, and the transition resets the dinosaur only after that exit. The held key cannot repeat the transition. All of these fields reset on restart.

## Persistent BEST

The default high-score record is a JSON object with one high_score integer in the current user's local application-data directory. A missing or malformed file reads as zero and any operating-system error during save is ignored. The record is updated only when the current score exceeds it and is preserved by reset and restart.


## Latest Player-Requested Fields and Rules

death_overlay_delay_remaining starts at DEATH_SCREEN_DELAY (0.5 seconds) on a fatal cactus collision. During the delay, the session remains in GAME_OVER, score and entity positions do not advance, and draw() renders the frozen gameplay scene. When the timer reaches zero, draw() renders the exact loss message and restart prompt.

A game-over Space/Up input checks the current derived score before reset. If it is at least REVIVE_COST (500), restart carries score - 500 as the new run's bonus score and auto-jumps; otherwise it starts a zero-score jumping run. R always resets to a zero-score standing run. The all-time BEST record is preserved in both cases. get_ground_color() returns BLACK in normal/rainbow state and WHITE in inverted state.


## Symmetric Dig Invariant

GameSession stores dig_target_inverted when a fresh grounded D press starts. _advance_dig() moves the dinosaur downward whether the current universe is normal or inverted. When the rectangle exits the bottom edge, the session sets is_inverted to the stored target, resets the dinosaur to the ground, and emits the matching universe notification. No direct teleport is used for the return transition. An airborne D press cannot enter this state.


## Dig Start Invariant

request_dig() requires Dinosaur.is_grounded. This prevents an airborne D press from setting is_digging, so Dinosaur.update() continues applying gravity throughout every jump. D must be released and pressed again after landing if the player pressed it during the jump.
