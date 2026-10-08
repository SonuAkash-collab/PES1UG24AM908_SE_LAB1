import math
import random
from collections import Counter, deque
import pygame
from game.button import ChoiceButton
from game.icons import draw_icon

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

        # Reveal animation: both hands shake in sync to "ROCK... PAPER... SCISSORS..." before the picks are shown
        self.revealing = False
        self.reveal_start_time = 0
        self.countdown_words = ["ROCK...", "PAPER...", "SCISSORS..."]
        self.beat_duration = 350
        self.reveal_duration = self.beat_duration * len(self.countdown_words)
        self.shake_height = 14
        self.pop_duration = 180
        self.last_outcome = None

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
        if self.match_over or self.revealing:
            return

        self.player_choice = choice
        self.cpu_choice = self.choose_cpu_move()
        self.player_history.append(choice)  # recorded after the CPU picks, so it never sees the current move

        # Scores are only applied once the countdown animation finishes (see update -> resolve_round)
        self.revealing = True
        self.showing_result = False
        self.last_outcome = None
        self.reveal_start_time = pygame.time.get_ticks()
        self.result_text = self.countdown_words[0]
        self.result_color = (235, 235, 240)

    def resolve_round(self):
        self.revealing = False
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

        self.last_outcome = outcome
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
        self.revealing = False
        self.last_outcome = None

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
        if self.revealing:
            elapsed = now - self.reveal_start_time
            if elapsed >= self.reveal_duration:
                self.resolve_round()
            else:
                beat = min(elapsed // self.beat_duration, len(self.countdown_words) - 1)
                self.result_text = self.countdown_words[beat]
            return

        if self.showing_result and (now - self.round_resolved_time >= self.display_duration):
            self.player_choice = None
            self.cpu_choice = None
            self.result_text = "Make your move!"
            self.result_color = (190, 195, 205)
            self.showing_result = False
            self.last_outcome = None

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

        self.render_arena(screen)

        res_surf = self.font_arena.render(self.result_text, True, self.result_color)
        screen.blit(res_surf, (self.width // 2 - res_surf.get_width() // 2, 232))

        for btn in self.buttons:
            btn.render(screen)

        if self.match_over:
            self.render_match_over(screen)

    def render_arena(self, screen):
        now = pygame.time.get_ticks()
        icon_cy = 152
        icon_size = 72

        shake = 0
        if self.revealing:
            phase = ((now - self.reveal_start_time) % self.beat_duration) / self.beat_duration
            shake = -int(abs(math.sin(phase * math.pi)) * self.shake_height)

        pop = 1.0
        if self.showing_result:
            t = (now - self.round_resolved_time) / self.pop_duration
            if t < 1:
                pop = 0.6 + 0.4 * max(0.0, t)

        slots = [
            ("YOU", self.player_choice, self.width // 2 - 120, (100, 180, 255), "PLAYER"),
            ("CPU", self.cpu_choice, self.width // 2 + 120, (255, 120, 120), "CPU"),
        ]
        for label, choice, cx, label_color, side in slots:
            label_surf = self.font_hud.render(label, True, label_color)
            screen.blit(label_surf, (cx - label_surf.get_width() // 2, 88))

            ring_color = (60, 68, 84)
            if self.last_outcome == side:
                ring_color = (80, 230, 120)
            elif self.last_outcome == "TIE":
                ring_color = (240, 210, 80)
            elif self.last_outcome is not None:
                ring_color = (240, 80, 80)
            pygame.draw.circle(screen, (34, 40, 52), (cx, icon_cy), 46)
            pygame.draw.circle(screen, ring_color, (cx, icon_cy), 46, 3)

            if self.revealing:
                # Both sides shake a closed fist together during the countdown
                draw_icon(screen, "ROCK", cx, icon_cy + shake, icon_size)
                name = "..."
            elif choice:
                draw_icon(screen, choice, cx, icon_cy, int(icon_size * pop))
                name = choice
            else:
                q_surf = self.font_banner.render("?", True, (90, 98, 115))
                screen.blit(q_surf, (cx - q_surf.get_width() // 2, icon_cy - q_surf.get_height() // 2))
                name = "--"

            name_surf = self.font_hud.render(name, True, (225, 225, 230))
            screen.blit(name_surf, (cx - name_surf.get_width() // 2, 204))

        vs_surf = self.font_arena.render("VS", True, (150, 155, 170))
        screen.blit(vs_surf, (self.width // 2 - vs_surf.get_width() // 2, icon_cy - vs_surf.get_height() // 2))

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
