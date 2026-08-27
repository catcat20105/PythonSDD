# Quickstart: Chrome Dinosaur Stomp Runner

## Prerequisites

- Windows desktop with Python available.
- Project dependencies installed in .venv; the pinned dependency is pygame-ce==2.5.8.
- The generated monochrome sprite is bundled at Day3/assets/dino.png.
- Run commands from C:\Users\CJSCOPE\Desktop\PythonSDD.

If needed, install the dependency:

~~~powershell
& .\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

## Automated checks

~~~powershell
& .\.venv\Scripts\python.exe -m py_compile Day3\prj07.py Day3\test_prj07.py
& .\.venv\Scripts\python.exe -m unittest discover -s Day3 -p "test_*.py" -v
& .\.venv\Scripts\python.exe -c "import Day3.prj07"
~~~

Expected results: compilation succeeds, all deterministic tests pass, and importing the module does not open a Pygame window.

## Manual smoke test

Launch the game:

~~~powershell
& .\.venv\Scripts\python.exe Day3\prj07.py
~~~

Verify:

1. A fixed-size window appears within five seconds with a grounded pure-black pixel dinosaur with one white rectangular eye, black ground line over the normal background-colored floor, randomized cacti, score, BEST, and only the DINO GAME / PRESS SPACE KEY TO START ready screen.
2. Space or Up starts the run. The dinosaur reaches the tuned jump arc, lands on the base ground, and ignores a second jump while airborne.
3. Land on a cactus from above. It disappears and the score increases by 50. Pass over another cactus without stomping and confirm it remains in play and reverses at the screen edge.
4. Touch a cactus from the side. Confirm the gameplay scene remains visible and frozen for 0.5 seconds, then ARE YOU TRYING TO EAT THE CACTUS?, YOU LOSE, and PRESS SPACE TO RESTART appear; world movement and score stop.
5. Jump, press E once while airborne, and hit a pterodactyl at one of the elevated flight lanes. Confirm the forgiving punch removes the enemy and the score increases by 100. A second press is blocked until the five-second cooldown expires, and holding E must not repeat the attack.
6. Let a pterodactyl touch the dinosaur without punching. Confirm the run continues with a brief stun and no enemy bonus. Then jump onto another pterodactyl from above and confirm the dino rides it at cactus height for five seconds; each cactus disappears only when it touches the ridden pterodactyl. While riding, press Space to jump off: the old pterodactyl disappears, the dino launches, and a later pterodactyl can be ridden. Other pterodactyls cannot stun the dino while it is airborne or riding.
7. When one to three cacti are ahead, hold E while grounded for 0.1 seconds. Confirm up to three cacti clear and COMBO xN appears. Try the same action with no target and confirm the attempt is wasted for 15 seconds.
8. Survive for at least 20 seconds. Confirm survival score increases monotonically, BEST never decreases, and movement speed steps up without exceeding the cap.
9. Finish a run with a nonzero score, restart, and confirm BEST remains visible.
10. From game over, press R and verify a standing zero-score reset. On a run with at least 500 points, die and press Space/Up during or after the delay; verify exactly 500 points are spent, the remainder is kept, and the dinosaur jumps immediately. Confirm old enemies, punch state, stun, ride timer, mounted enemy, cooldowns, and speed do not leak.
11. Exit with Escape, then repeat with the window close button. Confirm no exception or lingering Pygame process.

The keyboard and rendering contract is in contracts/ui.md, and entity invariants are in data-model.md.

    
## Latest Controls

- W: press once to start the exact-red background rainbow for 15 seconds; wait through the 60-second cooldown before using it again.
- R: press once to summon the helper pterodactyl for five seconds; it clears hazards it touches without score and has a 30-second cooldown.
- D while grounded: tap, then hold until the dinosaur exits the bottom to enter the inverted universe; release and press D again, then hold through another bottom exit to return to normal. Pressing D during a jump should do nothing.
- In the inverted universe, W keeps the background black while cacti and pterodactyls change hue.
- Close and reopen the game as the same Windows user to verify BEST is still shown.


## Latest Smoke Checks

- Confirm the exact start and loss-screen wording. The loss overlay must wait 0.5 seconds after the fatal cactus frame while the visible gameplay scene and score remain frozen.
- Confirm Space/Up is the 500-point score-preserving revive when enough score exists; R remains the ordinary zero-score standing restart.


## Latest Universe Checks

- In the inverted universe, press and hold D long enough to see the dinosaur travel off the bottom; verify it returns to normal only after that full traversal.
- Confirm the floor below the line uses the normal background ordinarily but becomes pure white during W rainbow and inverted mode; the line itself is black normally/rainbow and white in the inverted universe.


## Latest Dig Smoke Check

- Jump and press D while airborne. Confirm the dinosaur continues its normal arc and does not fly or begin a universe transition; land, release D, and press it again to start digging.
