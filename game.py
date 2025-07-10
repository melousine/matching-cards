import pygame
import random
from pygame.locals import *

class CEvent:
    def __init__(self, app):
        self.app = app

    def on_key_down(self, event):
        if event.key == K_q:
            self.app.running = False

    def on_mouse_button_down(self, event):
        if event.button == 1:
            self.app.handle_click(event.pos)

class App:
    def __init__(self):
        pygame.init()
        self.running = True
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Matching Cards Game")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 48)
        self.font_score = pygame.font.SysFont(None, 24)
        self.event = CEvent(self)
        
        # Card image loading
        self.card_images_1 = [pygame.image.load(f"{i}.png") for i in range(1, 7)]
        self.card_images_2 = [pygame.image.load(f"{i}.png") for i in range(1, 13)]
        self.tile_back = pygame.image.load("13.png")

        self.cols = 4
        self.rows = 3
        self.level = 1
        self.cards = []
        self.selected_cards = []
        self.score = 0
        self.delay_counter = 0
        self.matched_count = 0
        self.total_pairs = 0
        self.card_size = (0, 0)

        self.state = 'menu'

    def draw_centered_text(self, text, y):
        surface = self.font.render(text, True, (255, 255, 255))
        rect = surface.get_rect(center=(400, y))
        self.screen.blit(surface, rect)

    def set_level(self, level):
        self.level = level
        if level == 1:
            card_images = self.card_images_1
            self.total_pairs = 6
        else:
            card_images = self.card_images_2
            self.total_pairs = 12

        total_cards = self.total_pairs * 2
        self.card_size = self.calculate_card_size(total_cards)
        positions = self.generate_positions(total_cards)
        images = card_images * 2
        random.shuffle(images)

        self.cards = []
        for i in range(total_cards):
            rect = pygame.Rect(*positions[i], *self.card_size)
            self.cards.append({
                "rect": rect,
                "image": images[i],
                "flipped": False,
                "matched": False
            })

        self.score = 0
        self.selected_cards = []
        self.delay_counter = 0
        self.matched_count = 0
        self.state = 'game'

    def calculate_card_size(self, total_cards):
        rows = (total_cards + self.cols - 1) // self.cols
        avail_width = 800 - (self.cols + 1) * 10
        avail_height = 600 - (rows + 1) * 10
        w = avail_width // self.cols
        h = avail_height // rows
        ratio = 1.65 / 2.5
        if w / h > ratio:
            w = int(h * ratio)
        else:
            h = int(w / ratio)
        return w, h

    def generate_positions(self, total_cards):
        rows = (total_cards + self.cols - 1) // self.cols
        grid_width = self.cols * self.card_size[0] + (self.cols - 1) * 10
        grid_height = rows * self.card_size[1] + (rows - 1) * 10

        offset_x = (800 - grid_width) // 2
        offset_y = (600 - grid_height) // 2
        positions = []
        for r in range(rows):
            for c in range(self.cols):
                x = offset_x + c * (self.card_size[0] + 10)
                y = offset_y + r * (self.card_size[1] + 10)
                positions.append((x, y))
        return positions


    def handle_click(self, pos):
        if self.state == 'menu':
            self.state = 'choose_level'
        elif self.state == 'choose_level':
            y = pos[1]
            if 310 < y < 350:
                self.set_level(1)
            elif 350 < y < 390:
                self.set_level(2)
        elif self.state == 'game' and self.delay_counter == 0:
            for card in self.cards:
                if card["rect"].collidepoint(pos) and not card["flipped"] and not card["matched"]:
                    card["flipped"] = True
                    self.selected_cards.append(card)
                    if len(self.selected_cards) == 2:
                        if self.selected_cards[0]["image"] == self.selected_cards[1]["image"]:
                            for c in self.selected_cards:
                                c["matched"] = True
                            self.score += 10
                            self.matched_count += 1
                            self.selected_cards.clear()
                            if self.matched_count == self.total_pairs:
                                self.state = 'game_over'
                        else:
                            self.delay_counter = 60

        elif self.state == 'game_over':
            self.state = 'menu'

    def on_event(self, event):
        if event.type == QUIT:
            self.running = False
        elif event.type == KEYDOWN:
            self.event.on_key_down(event)
        elif event.type == MOUSEBUTTONDOWN:
            self.event.on_mouse_button_down(event)

    def render_menu(self):
        self.screen.fill((135, 206, 235))
        self.draw_centered_text("Matching Cards Game", 250)
        self.draw_centered_text("Klik untuk Mulai", 310)

    def render_choose_level(self):
        self.screen.fill((135, 206, 235))
        self.draw_centered_text("Pilih Level", 250)
        self.draw_centered_text("Level 1: 6 Pasang Kartu", 310)
        self.draw_centered_text("Level 2: 12 Pasang Kartu", 370)

    def render_game(self):
        self.screen.fill((135, 206, 235))
        for card in self.cards:
            image = card["image"] if card["flipped"] or card["matched"] else self.tile_back
            img = pygame.transform.scale(image, self.card_size)
            self.screen.blit(img, card["rect"])
        score_text = self.font_score.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (10, 10))

        if self.delay_counter > 0:
            self.delay_counter -= 1
            if self.delay_counter == 0:
                for card in self.selected_cards:
                    card["flipped"] = False
                self.selected_cards.clear()

    def render_game_over(self):
        self.screen.fill((135, 206, 235))
        self.draw_centered_text("Permainan Selesai!", 250)
        self.draw_centered_text(f"Skor Anda: {self.score}", 300)
        self.draw_centered_text("Klik untuk Kembali ke Menu", 350)

    def render(self):
        if self.state == 'menu':
            self.render_menu()
        elif self.state == 'choose_level':
            self.render_choose_level()
        elif self.state == 'game':
            self.render_game()
        elif self.state == 'game_over':
            self.render_game_over()

        pygame.display.flip()

    def execute(self):
        while self.running:
            for event in pygame.event.get():
                self.on_event(event)
            self.render()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    app = App()
    app.execute()
