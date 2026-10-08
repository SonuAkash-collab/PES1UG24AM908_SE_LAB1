import random
from collections import Counter, deque
import pygame
from game.button import ChoiceButton

class GameEngine:
    def __init__(self, width, height, target_score=3):
        self.width = width
        self.height = height
        self.target_score = max(1, int(target_score))

        self.choices = ["ROCK", "PAPER", "SCISSORS"]
        btn_w, btn_h = 130, 50
        gap = 20
        total_w = 3 * btn_w + 2 * gap
        start_x = (width - total_w) // 2
        btn_y = height - 85

        self.buttons = [
            ChoiceButton("ROCK", pygame.Rect(start_x, btn_y, btn_w, btn_h), (160, 50, 50), (200, 70, 70)),
            ChoiceButton("PAPER", pygame.Rect(start_x + btn_w + gap, btn_y, btn_w, btn_h), (40, 100, 170), (60, 130, 210)),
            ChoiceButton("SCISSORS", pygame.Rect(start_x + 2 * (btn_w + gap), btn_y, btn_w, btn_h), (180, 140, 30), (220, 180, 50)),
        ]

        self.player_choice = None
        self.cpu_choice = None
        self.result_text = "Make your move!"
        self.result_color = (220, 225, 235)

        self.player_score = 0
        self.cpu_score = 0

        self.match_over = False
        self.match_winner = None

        # Adaptive AI: remember the player's recent throws and counter their favourite
        self.history_size = 6        # how many recent player moves to remember
        self.min_history = 3         # moves needed before the CPU starts adapting
        self.favor_threshold = 0.5   # a move is a "habit" if it's at least this share of history
        self.adapt_chance = 0.75     # how often the CPU plays the counter once a habit is found
        self.player_history = deque(maxlen=self.history_size)
        self.counter_move = {"ROCK": "PAPER", "PAPER": "SCISSORS", "SCISSORS": "ROCK"}

        self.round_resolved_time = 0
        self.display_duration = 1800
        self.showing_result = False

        self.font_title = pygame.font.SysFont(None, 36)
        self.font_hud = pygame.font.SysFont(None, 26)
        self.font_arena = pygame.font.SysFont(None, 32)
        self.font_banner = pygame.font.SysFont(None, 48)

    def determine_winner(self, player, cpu):
        if player == cpu:
            return "TIE"
            
        rules = {
            ("ROCK", "SCISSORS"): "PLAYER",
            ("SCISSORS", "PAPER"): "PLAYER",
            ("PAPER", "ROCK"): "PLAYER",
            ("SCISSORS", "ROCK"): "CPU",
            ("PAPER", "SCISSORS"): "CPU",
            ("ROCK", "PAPER"): "CPU",
        }
        return rules.get((player, cpu), "TIE")

    def choose_cpu_move(self):
        if len(self.player_history) >= self.min_history:
            favorite, count = Counter(self.player_history).most_common(1)[0]
            if count / len(self.player_history) >= self.favor_threshold and random.random() < self.adapt_chance:
                return self.counter_move[favorite]
        return random.choice(self.choices)

    def play_round(self, choice):
        if self.match_over:
            return

        self.player_choice = choice
        self.cpu_choice = self.choose_cpu_move()
        self.player_history.append(choice)  # recorded after the CPU picks, so it never sees the current move

        outcome = self.determine_winner(self.player_choice, self.cpu_choice)
        if outcome == "PLAYER":
            self.player_score += 1
            self.result_text = f"You Win! {self.player_choice} beats {self.cpu_choice}."
            self.result_color = (80, 230, 120)
        elif outcome == "CPU":
            self.cpu_score += 1
            self.result_text = f"You Lose! {self.cpu_choice} beats {self.player_choice}."
            self.result_color = (240, 80, 80)
        else:
            self.result_text = f"It's a Draw! Both picked {self.player_choice}."
            self.result_color = (240, 210, 80)

        self.showing_result = True
        self.round_resolved_time = pygame.time.get_ticks()

        if self.player_score >= self.target_score:
            self.match_over = True
            self.match_winner = "PLAYER"
        elif self.cpu_score >= self.target_score:
            self.match_over = True
            self.match_winner = "CPU"

    def reset_match(self):
        self.player_score = 0
        self.cpu_score = 0
        self.player_choice = None
        self.cpu_choice = None
        self.result_text = "Make your move!"
        self.result_color = (220, 225, 235)
        self.showing_result = False
        self.match_over = False
        self.match_winner = None
        self.player_history.clear()

    def handle_event(self, event):
        if self.match_over:
            if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                self.reset_match()
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for btn in self.buttons:
                if btn.contains(event.pos):
                    self.play_round(btn.choice_name)
                    break

    def update(self):
        if self.match_over:
            return

        now = pygame.time.get_ticks()
        if self.showing_result and (now - self.round_resolved_time >= self.display_duration):
            self.player_choice = None
            self.cpu_choice = None
            self.result_text = "Make your move!"
            self.result_color = (190, 195, 205)
            self.showing_result = False

    def render(self, screen):
        screen.fill((24, 28, 36))

        title_surf = self.font_title.render("Rock Paper Scissors", True, (245, 245, 245))
        screen.blit(title_surf, (self.width // 2 - title_surf.get_width() // 2, 14))

        p_surf = self.font_hud.render(f"Player Score: {self.player_score}", True, (100, 180, 255))
        c_surf = self.font_hud.render(f"CPU Score: {self.cpu_score}", True, (255, 120, 120))
        screen.blit(p_surf, (35, 52))
        screen.blit(c_surf, (self.width - c_surf.get_width() - 35, 52))

        goal_surf = self.font_hud.render(f"First to {self.target_score}", True, (170, 175, 190))
        screen.blit(goal_surf, (self.width // 2 - goal_surf.get_width() // 2, 52))

        pygame.draw.line(screen, (45, 52, 66), (25, 82), (self.width - 25, 82), 2)

        p_str = self.player_choice if self.player_choice else "--"
        c_str = self.cpu_choice if self.cpu_choice else "--"

        arena_p = self.font_arena.render(f"Your Pick:  {p_str}", True, (225, 225, 230))
        arena_c = self.font_arena.render(f"CPU Pick:  {c_str}", True, (225, 225, 230))
        screen.blit(arena_p, (self.width // 2 - arena_p.get_width() // 2, 115))
        screen.blit(arena_c, (self.width // 2 - arena_c.get_width() // 2, 155))

        res_surf = self.font_arena.render(self.result_text, True, self.result_color)
        screen.blit(res_surf, (self.width // 2 - res_surf.get_width() // 2, 205))

        for btn in self.buttons:
            btn.render(screen)

        if self.match_over:
            self.render_match_over(screen)

    def render_match_over(self, screen):
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((10, 12, 18, 200))
        screen.blit(overlay, (0, 0))

        if self.match_winner == "PLAYER":
            banner_text = "YOU WIN THE MATCH!"
            banner_color = (80, 230, 120)
        else:
            banner_text = "CPU WINS THE MATCH!"
            banner_color = (240, 80, 80)

        banner_surf = self.font_banner.render(banner_text, True, banner_color)
        score_surf = self.font_arena.render(
            f"Final Score  {self.player_score} - {self.cpu_score}", True, (235, 235, 240)
        )
        prompt_surf = self.font_hud.render("Press R to play again", True, (190, 195, 205))

        cy = self.height // 2
        panel = pygame.Rect(0, 0, 420, 170)
        panel.center = (self.width // 2, cy)
        pygame.draw.rect(screen, (30, 35, 46), panel, border_radius=12)
        pygame.draw.rect(screen, banner_color, panel, width=3, border_radius=12)

        screen.blit(banner_surf, (self.width // 2 - banner_surf.get_width() // 2, cy - 60))
        screen.blit(score_surf, (self.width // 2 - score_surf.get_width() // 2, cy - 5))
        screen.blit(prompt_surf, (self.width // 2 - prompt_surf.get_width() // 2, cy + 40))
