# Rock Paper Scissor Lab

This project is an interactive hand-game duel using **Pygame**. It introduces students to dictionary-based rule lookups, automated CPU decision-making, temporary result display timers, and modular UI button interaction within an object-oriented codebase.
---

## What's Provided

A working Rock Paper Scissors game with:

- Three interactive choice buttons (`ROCK`, `PAPER`, `SCISSORS`) with mouse hover and click response states
- An automated computer opponent selecting moves at random
- Live scoreboard tracking player score and CPU score independently
- Timed result display that shows the outcome for 1.8 seconds before clearing picks for the next round

It has **one deliberate bug** and **three optional features** left as tasks to implement. You are expected to **analyze**, **interact with an AI assistant**, and **complete/fix** the game to make it fully functional and more interesting.

### **Use an LLM (e.g. ChatGPT or Claude) as your debugging and pair-programming partner for this lab.**
---

## Getting Started

### Setup

1. Make sure you have Python 3.10+ installed.
2. Install dependencies:

```bash
pip install pygame
```

3. Run the game:

```bash
python main.py
```

**Controls:** Left-click colored pads to repeat the sequence. Press R to restart after Game Over.


## Tasks to Complete

Each task must be completed using an iterative process involving LLM suggestions and your critical code review.

### Task 1: Fix the inverted outcome evaluation bug

Whenever the player throws a winning hand against the computer, the game awards the point to the CPU instead of the player. Correct the outcome evaluation logic so standard rules apply (Rock beats Scissors, Scissors beats Paper, and Paper beats Rock).

### Task 2: Implement "First to X Wins" match victory state

The game currently loops endlessly with no decisive match conclusion. Introduce a target win ceiling that halts play when reached, presents an end-of-match victory banner declaring the ultimate winner, and prompts the player to restart.

### Task 3: Implement adaptive AI pattern tracking

The computer currently picks its moves entirely at random. Introduce adaptive intelligence that records the player's recent throw tendencies and dynamically biases CPU selections toward the counter-move when a player repeatedly favors a specific option.

### Task 4: Implement Procedural Gesture Icons & Reveal Animations

Selections are currently rendered as plain text labels. Create distinct visual graphic icons for Rock, Paper, and Scissors, adding a synchronized countdown or shaking reveal animation before displaying both choices each turn.

---

## Expected Behavior

- Clicking any choice button selects that move, rolls a CPU choice, and evaluates the winner correctly.
- Rock beats Scissors, Scissors beats Paper, Paper beats Rock, and identical choices result in a Draw.
- Scores increment accurately and the round outcome stays visible for 1.8 seconds before clearing picks back to
---

## Folder Structure

```
rock_paper_scissors/
├── game/
│   ├── button.py
│   └── game_engine.py
├── main.py
└── README.md
```

## Submission Checklist

Submission is only the following three things:

- [] A 10-second video of gameplay **before** your changes, showing the bug/broken behavior
- [] A 10-second video of gameplay **after** your changes, showing the bug fixed and the new features working
- [] The Chat/LLM used page link, with the complete chat history
