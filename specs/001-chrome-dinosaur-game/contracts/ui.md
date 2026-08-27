# UI Contract: Chrome Dinosaur Stomp Runner

## Window and rendering

- The game opens one fixed 960x360 desktop window.
- The scene contains a light sky/background, black ground line over the normal background-colored floor, minimal pure-black pixel dinosaur with one white rectangular eye, randomized green cacti, stylized pterodactyls, score text, and BEST text.
- The dinosaur remains in a fixed horizontal lane; hazards provide the horizontal motion.
- Active punch and score feedback are visible briefly enough for manual verification.
- READY shows only DINO GAME and PRESS SPACE KEY TO START. After a fatal cactus, GAME_OVER draws the frozen gameplay scene for 0.5 seconds, then shows ARE YOU TRYING TO EAT THE CACTUS?, YOU LOSE, and PRESS SPACE TO RESTART.

## Keyboard contract

| Key | Ready | Running | Game over |
|---|---|---|---|
| Space / Up Arrow | Start and jump | Jump only when grounded and unstunned; while riding, dismount and jump | If score is at least 500, spend 500 and restart with the remainder while jumping; otherwise reset to zero and jump |
| E keydown while airborne | N/A | Create one punch if cooldown is ready | Ignored |
| E keydown while grounded | N/A | Begin hidden combo hold if cooldown is ready | Ignored |
| E keyup | Release the current E edge/hold | Release the current E edge/hold | Release the current E edge/hold |
| W keydown | N/A | Start rainbow if ready | Ignored |
| W keyup | Release W edge | Release W edge | Release W edge |
| R | Ignored | Summon helper if ready | Reset and start standing |
| D keydown | Ignored until running | Start or continue a bottom-exit dig toward the opposite universe only while grounded; ignore while airborne | Ignored |
| D keyup | Release D edge | Stop continuous dig and unlock a future toggle | Release D edge |
| Escape | Exit | Exit | Exit |

E is processed as a key edge. OS key-repeat or a held key cannot create repeated normal punches or repeated combo attempts. An airborne press creates one forgiving punch and starts the five-second punch cooldown. A grounded combo attempt requires holding E for the configured trigger duration, succeeds for up to three qualifying cacti, and consumes its cooldown even on failure.

## Gameplay feedback

- A stomp shows a 50-point increase.
- A pterodactyl punch shows a 100-point increase.
- A successful grounded secret shows COMBO xN and awards 50 points per cleared cactus, up to three targets.
- An unpunched pterodactyl contact shows a brief stun state but does not show game over.
- A descending pterodactyl stomp mounts the dino on the enemy at cactus height, shows the ride countdown, and removes each cactus when it touches the ridden pterodactyl for five seconds. Jumping while riding removes that old enemy and launches the dino.
- A fatal cactus contact freezes the last scene and score for 0.5 seconds, then shows the loss overlay with R and Space/Up restart instructions. BEST remains the all-time highest score for the current local user and is persisted best-effort.

## Frame contract

Every frame must process, in order:

1. Limit the clock and calculate bounded delta time.
2. Translate events into session actions.
3. Decrement transient timers and update score/speed.
4. Update dinosaur physics.
5. Move cacti and pterodactyls.
6. Synchronize a mounted dinosaur and update the punch hitbox.
7. Resolve punch hits.
8. Resolve descending cactus stomps.
9. Resolve descending pterodactyl stomps and start a ride.
10. Remove cacti touching the ridden pterodactyl.
11. Resolve one-time pterodactyl stun.
12. Resolve fatal cactus side/underside collision.
13. Remove spent enemies, replenish eligible cactus slots, draw, and flip the display.

Collision checks occur after movement and before drawing. Simulation and score updates stop when the session is in GAME_OVER. The only GAME_OVER update is the 0.5-second death-overlay countdown; after it expires, drawing changes from the frozen scene to the loss overlay.

## Shutdown contract

The Pygame QUIT event and Escape both stop the outer loop. pygame.quit() executes in a finally block so the display and Pygame resources are released on either exit path.

    
## Ability rendering details

W starts normal mode at RGB (255, 0, 0), cycles hue for 15 seconds, and then restores the normal sky. In the inverted universe the background is always RGB (0, 0, 0), while W animates only cactus and pterodactyl colors. The floor below the line uses the normal background RGB ordinarily and RGB (255, 255, 255) during rainbow or inverted mode; the line is RGB (0, 0, 0) normally/rainbow and RGB (255, 255, 255) in the inverted universe. R shows a HELPER countdown during its five-second lifetime. D shows DIG progress during a bottom-exit traversal in either direction. The helper clears contacted hazards without a score notification.


## Latest Input and Transition Details

- A pterodactyl contact never stuns an airborne, riding, or actively digging dinosaur.
- D digging advances until the dinosaur exits the bottom edge before the selected universe begins; the same traversal is required to leave the inverted universe. Airborne D is ignored and normal gravity continues.
- Space/Up during GAME_OVER is the revive action when the score is at least 500; it spends 500 points, carries the remainder, and auto-jumps. R always starts a zero-score standing run.


## Ground Rendering Invariant

The floor below the line uses the normal background color ordinarily and pure white during rainbow or inverted mode. The line is black in normal/rainbow mode and white in the inverted universe.


## Dig Input Invariant

D is a grounded-only action. An airborne D keydown must not set is_digging, alter vertical velocity, or interrupt the jump.
