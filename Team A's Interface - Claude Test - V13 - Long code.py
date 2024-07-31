import pygame
import sys
import json
from datetime import datetime
import random

pygame.init()

# Set up the display
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("The Oregon Trail")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (0, 123, 255)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
DARK_GREEN = (0, 100, 0)
PRAIRIE_GREEN = (76, 187, 23)
SKY_BLUE = (135, 206, 235)
WAGON_BROWN = (139, 69, 19)
RIVER_BLUE = (65, 105, 225)
MOUNTAIN_GRAY = (105, 105, 105)
YELLOW = (255, 255, 0)

# Fonts
title_font = pygame.font.Font(None, 64)
button_font = pygame.font.Font(None, 36)
small_font = pygame.font.Font(None, 24)

# Game states
MAIN_MENU, CHARACTER_CREATION, CLASS_SELECTION, DIFFICULTY_SELECTION, TRAVEL, SHOP, HIGH_SCORES, VICTORY_SCREEN, DEFEAT_SCREEN, DEATH_SCREEN, RIVER_CROSSING, INVENTORY, CHARACTER_PROGRESS, PROGRESS_MAP, HUNTING = range(15)
current_state = MAIN_MENU

# Button class
class Button:
    def __init__(self, x, y, width, height, text, color, text_color=WHITE, font=button_font):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.text_color = text_color
        self.font = font
        self.tooltip = None

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)  # Add a border
        text_surf = self.font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, pos):
        return self.rect.collidepoint(pos)

# Input box class
class InputBox:
    def __init__(self, x, y, width, height, text=''):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = BLACK
        self.text = text
        self.active = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            self.active = self.rect.collidepoint(event.pos)
        if event.type == pygame.KEYDOWN:
            if self.active:
                if event.key == pygame.K_RETURN:
                    print(self.text)
                    self.text = ''
                elif event.key == pygame.K_BACKSPACE:
                    self.text = self.text[:-1]
                else:
                    self.text += event.unicode

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, 2)
        text_surface = small_font.render(self.text, True, self.color)
        surface.blit(text_surface, (self.rect.x + 5, self.rect.y + 5))

# Log Display class with scrollbar
class LogDisplay:
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)
        self.logs = []
        self.max_logs = 5
        self.scroll_y = 0
        self.scroll_speed = 10

    def add_log(self, message):
        self.logs.append(message)
        if len(self.logs) > self.max_logs:
            self.logs.pop(0)
        self.scroll_y = max(0, len(self.logs) - self.max_logs)

    def handle_scroll(self, direction):
        if direction == 'UP':
            self.scroll_y = max(0, self.scroll_y - self.scroll_speed)
        elif direction == 'DOWN':
            self.scroll_y = min(max(0, len(self.logs) - self.max_logs), self.scroll_y + self.scroll_speed)

    def draw(self, surface):
        pygame.draw.rect(surface, WHITE, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 2)
        visible_logs = self.logs[self.scroll_y:self.scroll_y + self.max_logs]
        for i, log in enumerate(visible_logs):
            log_surf = small_font.render(log, True, BLACK)
            surface.blit(log_surf, (self.rect.x + 5, self.rect.y + 5 + i * 20))

# Tooltip class
class Tooltip:
    def __init__(self, text, font=small_font):
        self.text = text
        self.font = font
        self.surface = font.render(text, True, BLACK)
        self.rect = self.surface.get_rect()

    def draw(self, screen, pos):
        self.rect.topleft = pos
        pygame.draw.rect(screen, LIGHT_BLUE, self.rect.inflate(10, 10))
        pygame.draw.rect(screen, BLACK, self.rect.inflate(10, 10), 2)
        screen.blit(self.surface, self.rect)

# Interactive Map class
class InteractiveMap:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.surface = pygame.Surface((510, 380))
        self.routes = {
            "INDEPENDENCE (START)": (40, 350),
            "FORT KEARNEY": (100, 320),
            "CHIMNEY ROCK": (160, 290),
            "LARAMIE": (220, 260),
            "INDEPENDENCE ROCK": (280, 230),
            "SOUTH PASS": (340, 200),
            "FORT BRIDGER": (390, 170),
            "SODA SPRINGS": (430, 140),
            "FORT HALL": (460, 110),
            "FORT BOISE": (480, 80),
            "BLUE MOUNTAINS": (490, 50),
            "FORT WALLA WALLA": (490, 20),
            "THE DALLES": (480, 10),
            "OREGON CITY (FINISH)": (470, 5),
        }
        self.progress = 0
        self.reached_locations = set()

    def draw(self):
        self.surface.fill(WHITE)  # White background
        
        # Draw the trail
        route_points = list(self.routes.values())
        if len(route_points) >= 2:
            pygame.draw.lines(self.surface, RED, False, route_points, 3)
        
        # Draw progress
        if self.progress > 0:
            progress_points = route_points[:int(self.progress * len(route_points)) + 1]
            if len(progress_points) >= 2:
                pygame.draw.lines(self.surface, GREEN, False, progress_points, 5)
        
        # Draw location markers
        for i, (location, pos) in enumerate(self.routes.items()):
            color = GREEN if location in self.reached_locations else BLUE
            pygame.draw.circle(self.surface, color, pos, 5)
            font = pygame.font.Font(None, 15)
            text = font.render(location, True, BLACK)
            text_rect = text.get_rect(center=(pos[0], pos[1] - 10))
            self.surface.blit(text, text_rect)

    def update_progress(self, progress):
        self.progress = progress
        self.reached_locations = set(list(self.routes.keys())[:int(progress * len(self.routes)) + 1])

    def get_surface(self):
        return self.surface

# Game state
class GameState:
    def __init__(self):
        self.character_name = ""
        self.character_class = ""
        self.difficulty = ""
        self.inventory = {}
        self.progress = 0
        self.health = 100
        self.money = 1000
        self.total_distance = 2000  # Total distance of the Oregon Trail
        self.interactive_map = InteractiveMap(400, 300)
        self.current_location_index = 0
        self.locations = list(self.interactive_map.routes.keys())
        
    def update_progress(self):
        if self.current_location_index < len(self.locations) - 1:
            self.current_location_index += 1
            self.progress = (self.current_location_index / (len(self.locations) - 1)) * 100
            self.interactive_map.update_progress(self.current_location_index / (len(self.locations) - 1))
            return True
        return False

    def get_current_location(self):
        return self.locations[self.current_location_index]

    def get_progress_percentage(self):
        return self.progress

    def save_game(self):
        data = {
            "character_name": self.character_name,
            "character_class": self.character_class,
            "difficulty": self.difficulty,
            "inventory": self.inventory,
            "progress": self.progress,
            "health": self.health,
            "money": self.money,
            "date": str(datetime.now())
        }
        with open("savegame.json", "w") as f:
            json.dump(data, f)

    def load_game(self):
        try:
            with open("savegame.json", "r") as f:
                data = json.load(f)
            self.character_name = data["character_name"]
            self.character_class = data["character_class"]
            self.difficulty = data["difficulty"]
            self.inventory = data["inventory"]
            self.progress = data["progress"]
            self.health = data["health"]
            self.money = data["money"]
            self.interactive_map.update_progress(self.progress / 100)
            return True
        except FileNotFoundError:
            return False

game_state = GameState()
log_display = LogDisplay(270, 500, 510, 280)

# Create buttons
new_game_btn = Button(300, 150, 200, 50, "NEW GAME", BLUE)
continue_btn = Button(300, 220, 200, 50, "CONTINUE", BLUE)
settings_btn = Button(300, 290, 200, 50, "SETTINGS", BLUE)
back_btn = Button(50, 450, 200, 50, "BACK", BLUE)
view_high_scores_btn = Button(300, 360, 200, 50, "HIGH SCORES", BLUE)
help_btn = Button(300, 430, 200, 50, "Help", BLUE)
main_menu_btn = Button(50, 520, 200, 50, "Main Menu", BLUE)

# Input box
name_input = InputBox(200, 200, 400, 32)

# Add tooltips to buttons
new_game_btn.tooltip = Tooltip("Start a new Oregon Trail adventure")
continue_btn.tooltip = Tooltip("Continue your saved game")
settings_btn.tooltip = Tooltip("Adjust game settings")

# Initialize current_buttons
current_buttons = [new_game_btn, continue_btn, settings_btn, view_high_scores_btn, help_btn]

# Function to create buttons for different states
def create_class_selection_buttons():
    return [
        Button(125, 150, 550, 50, "Banker: Start with more money", BLUE),
        Button(125, 220, 550, 50, "Farmer: Better at hunting and gathering", BLUE),
        Button(125, 290, 550, 50, "Carpenter: Wagon breaks down less often", BLUE),
    ]

def create_difficulty_selection_buttons():
    return [
        Button(300, 150, 200, 50, "EASY", GREEN),
        Button(300, 220, 200, 50, "MEDIUM", BLUE),
        Button(300, 290, 200, 50, "HARD", RED),
    ]

def create_travel_buttons():
    return [
        Button(50, 100, 200, 50, "INVENTORY", BLUE),
        Button(50, 170, 200, 50, "CHARACTER", BLUE),
        Button(50, 240, 200, 50, "HUNT", BLUE),
        Button(50, 310, 200, 50, "SHOP", BLUE),
        Button(50, 380, 200, 50, "TRAVEL", BLUE),
    ]

def create_high_scores_buttons():
    return []

# State management
def set_state(new_state):
    global current_state, current_buttons
    current_state = new_state
    if new_state == MAIN_MENU:
        current_buttons = [new_game_btn, continue_btn, settings_btn, view_high_scores_btn, help_btn]
    elif new_state == CHARACTER_CREATION:
        current_buttons = [Button(300, 250, 200, 50, "NEXT", BLUE)]
    elif new_state == CLASS_SELECTION:
        current_buttons = create_class_selection_buttons()
    elif new_state == DIFFICULTY_SELECTION:
        current_buttons = create_difficulty_selection_buttons()
    elif new_state == TRAVEL:
        current_buttons = create_travel_buttons()
    elif new_state == HIGH_SCORES:
        current_buttons = create_high_scores_buttons()
    elif new_state in [SHOP, INVENTORY, CHARACTER_PROGRESS, PROGRESS_MAP, HUNTING]:
        current_buttons = []
    elif new_state == VICTORY_SCREEN:
        current_buttons = [Button(300, 300, 200, 50, "MAIN MENU", BLUE)]
    
    if new_state != MAIN_MENU:
        current_buttons.append(back_btn)
        current_buttons.append(main_menu_btn)

# Hunting Mini-Game
def hunting_game():
    clock = pygame.time.Clock()
    deer_width, deer_height = 50, 50
    deer_x = random.randint(0, WIDTH - deer_width)
    deer_y = HEIGHT // 2.3
    deer_speed = 4
    deer_direction = 1
    score = 0
    game_duration = 10000  # 10 seconds in milliseconds
    start_time = pygame.time.get_ticks()

    # Create instruction text
    instruction_font = pygame.font.Font(None, 24)
    instruction_text = "To score: Hover mouse over the moving square and press spacebar"
    instruction_surf = instruction_font.render(instruction_text, True, BLACK)
    instruction_rect = instruction_surf.get_rect(centerx=WIDTH // 2, bottom=HEIGHT - 10)

    while pygame.time.get_ticks() - start_time < game_duration:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if deer_x < pygame.mouse.get_pos()[0] < deer_x + deer_width and \
                       deer_y < pygame.mouse.get_pos()[1] < deer_y + deer_height:
                        score += 1
                        deer_x = random.randint(0, WIDTH - deer_width)

        deer_x += deer_speed * deer_direction
        if deer_x <= 0 or deer_x >= WIDTH - deer_width:
            deer_direction *= -1

        # Fill the background
        screen.fill(PRAIRIE_GREEN)
        pygame.draw.rect(screen, SKY_BLUE, (0, 0, WIDTH, HEIGHT // 2))
        
        pygame.draw.rect(screen, WAGON_BROWN, (deer_x, deer_y, deer_width, deer_height))
        
        # Draw score
        score_surf = small_font.render(f"Score: {score}", True, BLACK)
        screen.blit(score_surf, (10, 10))

        # Calculate and draw timer
        time_left = (game_duration - (pygame.time.get_ticks() - start_time)) // 1000
        timer_surf = small_font.render(f"Time left: {time_left}s", True, BLACK)
        screen.blit(timer_surf, (WIDTH - timer_surf.get_width() - 10, 10))

        # Draw instruction text
        screen.blit(instruction_surf, instruction_rect)

        pygame.display.flip()
        clock.tick(250)

    return score

# Confirmation dialog
def show_confirmation_dialog(message):
    dialog_rect = pygame.Rect(200, 200, 400, 200)
    pygame.draw.rect(screen, WHITE, dialog_rect)
    pygame.draw.rect(screen, BLACK, dialog_rect, 2)
    text_surf = small_font.render(message, True, BLACK)
    screen.blit(text_surf, (dialog_rect.centerx - text_surf.get_width() // 2, dialog_rect.top + 50))
    yes_btn = Button(dialog_rect.left + 50, dialog_rect.bottom - 70, 100, 40, "Yes", GREEN)
    no_btn = Button(dialog_rect.right - 150, dialog_rect.bottom - 70, 100, 40, "No", RED)
    yes_btn.draw(screen)
    no_btn.draw(screen)
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if yes_btn.is_clicked(event.pos):
                    return True
                elif no_btn.is_clicked(event.pos):
                    return False
    return False

# Error message display
def show_error_message(message, suggestion):
    error_rect = pygame.Rect(200, 200, 400, 200)
    pygame.draw.rect(screen, WHITE, error_rect)
    pygame.draw.rect(screen, RED, error_rect, 2)
    error_text = small_font.render(message, True, RED)
    suggestion_text = small_font.render(suggestion, True, BLACK)
    screen.blit(error_text, (error_rect.centerx - error_text.get_width() // 2, error_rect.top + 50))
    screen.blit(suggestion_text, (error_rect.centerx - suggestion_text.get_width() // 2, error_rect.top + 100))
    pygame.display.flip()
    pygame.time.wait(3000)

# Help screen
def show_help_screen():
    help_rect = pygame.Rect(100, 100, 600, 380)
    pygame.draw.rect(screen, WHITE, help_rect)
    pygame.draw.rect(screen, BLACK, help_rect, 2)
    
    help_text = [
        "Goal: Travel from Independence, Missouri to Oregon City, Oregon.",
        "- Manage your resources carefully",
        "- Hunt for food when supplies are low",
        "- Trade with others along the trail",
        "- Watch out for diseases and injuries",
        "Keyboard Shortcuts:",
        "ESC - Return to Main Menu",
        "I - Open Inventory",
        "M - Open Map",
        "H - Start Hunting",
        "Good luck on your journey!"
    ]
    
    for i, line in enumerate(help_text):
        text_surf = small_font.render(line, True, BLACK)
        screen.blit(text_surf, (help_rect.left + 20, help_rect.top + 20 + i * 30))
    
    close_btn = Button(help_rect.centerx - 50, help_rect.bottom - 40, 100, 40, "Close", RED)
    close_btn.draw(screen)
    
    pygame.display.flip()
    
    waiting = True
    while waiting:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN and close_btn.is_clicked(event.pos):
                waiting = False

# Main game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if current_state == MAIN_MENU:
                if new_game_btn.is_clicked(event.pos):
                    if show_confirmation_dialog("Start a new game? Unsaved progress will be lost."):
                        set_state(CHARACTER_CREATION)
                        log_display.add_log("Started a new game")
                elif continue_btn.is_clicked(event.pos):
                    if game_state.load_game():
                        set_state(TRAVEL)
                        log_display.add_log("Continued saved game")
                    else:
                        show_error_message("No saved game found", "Start a new game instead")
                elif settings_btn.is_clicked(event.pos):
                    set_state(DIFFICULTY_SELECTION)
                    log_display.add_log("Opened settings")
                elif view_high_scores_btn.is_clicked(event.pos):
                    set_state(HIGH_SCORES)
                    log_display.add_log("Viewing high scores")
                elif help_btn.is_clicked(event.pos):
                    show_help_screen()
            else:
                for button in current_buttons:
                    if button.is_clicked(event.pos):
                        if button.text == "BACK":
                            if current_state in [SHOP, INVENTORY, CHARACTER_PROGRESS, PROGRESS_MAP, HUNTING]:
                                set_state(TRAVEL)
                            else:
                                set_state(MAIN_MENU)
                            log_display.add_log(f"Returned to {'Travel' if current_state == TRAVEL else 'Main Menu'}")
                        elif button.text == "Main Menu":
                            if show_confirmation_dialog("Return to Main Menu?"):
                                game_state.save_game()
                                set_state(MAIN_MENU)
                        elif current_state == CLASS_SELECTION:
                            game_state.character_class = button.text.split(":")[0]
                            set_state(DIFFICULTY_SELECTION)
                            log_display.add_log(f"Selected class: {game_state.character_class}")
                        elif current_state == DIFFICULTY_SELECTION:
                            game_state.difficulty = button.text
                            set_state(TRAVEL)
                            log_display.add_log(f"Set difficulty: {button.text}")
                        elif current_state == TRAVEL:
                            if button.text == "INVENTORY":
                                set_state(INVENTORY)
                            elif button.text == "CHARACTER":
                                set_state(CHARACTER_PROGRESS)
                            elif button.text == "HUNT":
                                score = hunting_game()
                                log_display.add_log(f"Completed hunting game with score: {score}")
                                set_state(TRAVEL)
                            elif button.text == "SHOP":
                                set_state(SHOP)
                            elif button.text == "TRAVEL":
                                if game_state.update_progress():
                                    log_display.add_log(f"Traveled to {game_state.get_current_location()}")
                                    if game_state.get_progress_percentage() >= 100:
                                        set_state(VICTORY_SCREEN)
                                        log_display.add_log("Congratulations! You've reached Oregon!")
                                else:
                                    log_display.add_log("You've already reached Oregon City!")
                            log_display.add_log(f"Opened {button.text.lower()}")
                        elif current_state == CHARACTER_CREATION and button.text == "NEXT":
                            game_state.character_name = name_input.text
                            set_state(CLASS_SELECTION)
                            log_display.add_log(f"Created character: {game_state.character_name}")
                        elif current_state == VICTORY_SCREEN and button.text == "MAIN MENU":
                            set_state(MAIN_MENU)
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if current_state != MAIN_MENU:
                    if show_confirmation_dialog("Are you sure you want to return to the main menu? Your progress will be saved."):
                        game_state.save_game()
                        set_state(MAIN_MENU)
            elif event.key == pygame.K_i and current_state == TRAVEL:
                set_state(INVENTORY)
            elif event.key == pygame.K_m and current_state == TRAVEL:
                set_state(PROGRESS_MAP)
            elif event.key == pygame.K_h and current_state == TRAVEL:
                set_state(HUNTING)
        if current_state == CHARACTER_CREATION:
            name_input.handle_event(event)

    # Fill the background
    screen.fill(PRAIRIE_GREEN)
    pygame.draw.rect(screen, SKY_BLUE, (0, 0, WIDTH, HEIGHT // 2))

    if current_state == MAIN_MENU:
        # Draw title
        title_surf = title_font.render("The Oregon Trail", True, BLACK)
        screen.blit(title_surf, (WIDTH//2 - title_surf.get_width()//2, 50))
    elif current_state == CHARACTER_CREATION:
        title = title_font.render("Create Character", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        name_input.draw(screen)
    elif current_state == CLASS_SELECTION:
        title = title_font.render("Select Class", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    elif current_state == DIFFICULTY_SELECTION:
        title = title_font.render("Select Difficulty", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    elif current_state == TRAVEL:
        title = title_font.render("Map of the Oregon Trail", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        
        # Draw the interactive map
        game_state.interactive_map.draw()
        map_surface = game_state.interactive_map.get_surface()
        screen.blit(map_surface, (WIDTH - map_surface.get_width() - 20, 100))
    elif current_state == SHOP:
        title = title_font.render("Shop", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    elif current_state == HIGH_SCORES:
        title = title_font.render("High Scores", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
        # Draw empty high score list
        pygame.draw.rect(screen, WHITE, (150, 100, 500, 330))
        pygame.draw.rect(screen, BLACK, (150, 100, 500, 330), 2)
    elif current_state == INVENTORY:
        title = title_font.render("Inventory", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    elif current_state == CHARACTER_PROGRESS:
        title = title_font.render("Character Progress", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    elif current_state == PROGRESS_MAP:
        title = title_font.render("Progress Map", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))
    elif current_state == VICTORY_SCREEN:
        title = title_font.render("Victory!", True, GREEN)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        message = button_font.render("You've successfully reached Oregon!", True, BLACK)
        screen.blit(message, (WIDTH // 2 - message.get_width() // 2, 200))

    # Draw current state's buttons
    for button in current_buttons:
        button.draw(screen)

    # Draw tooltips
    mouse_pos = pygame.mouse.get_pos()
    for button in current_buttons:
        if hasattr(button, 'tooltip') and button.tooltip is not None and button.rect.collidepoint(mouse_pos):
            button.tooltip.draw(screen, mouse_pos)

    # Draw the log display
    log_display.draw(screen)
    pygame.draw.rect(screen, BLACK, (log_display.rect.right - 10, log_display.rect.top, 10, log_display.rect.height))  # Scrollbar

    # Draw progress bar
    progress_bar = pygame.Rect(50, 20, 700, 20)
    pygame.draw.rect(screen, WHITE, progress_bar, 2)
    progress_width = int(progress_bar.width * (game_state.get_progress_percentage() / 100))
    pygame.draw.rect(screen, GREEN, (progress_bar.left, progress_bar.top, progress_width, progress_bar.height))
    progress_text = small_font.render(f"Progress: {game_state.get_progress_percentage():.1f}% - {game_state.get_current_location()}", True, BLACK)
    screen.blit(progress_text, (progress_bar.left, progress_bar.bottom + 5))

    pygame.display.flip()

# Save game before quitting
game_state.save_game()
pygame.quit()
sys.exit()
