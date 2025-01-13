import pygame
import random
import math

# Constants
SIM_WIDTH, SIM_HEIGHT = 1280, 720
FOOD_SIZE = 5
INITIAL_ENERGY = 10
CELL_SPEED = 3
FOOD_ENERGY = 1.5
SIZE_REDUCTION_RATE = 0.05
FOOD_SPAWN_RATE = 0.5 # Number of ticks to spawn new food
MINIMUM_CELL_SIZE = 1  # Minimum size for cell survival

# Colors
GREENGREEN = (0, 255, 0)
WHITE = (255, 255, 255)
RED = (153, 38, 0)
GREEN = (0, 77, 26)
BLUE = (0, 0, 255)
PURPLE = (128,0,128) 
BLOOD = (64, 64, 64)
GREY = (15, 15, 10)

# Initialize Pygame
pygame.init()
screen = pygame.display.set_mode((SIM_WIDTH, SIM_HEIGHT))
clock = pygame.time.Clock()

class Cell:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.energy = INITIAL_ENERGY
        self.direction = random.uniform(0, 2 * math.pi)
        self.speed = CELL_SPEED
        self.type = None
        self.colour = RED
        self.dfns = 1
        self.herbivory = 1

    def move_towards_food(self, food):
        dx = food.x - self.x
        dy = food.y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)
        if distance != 0:
            self.direction = math.atan2(dy, dx)

    def collision_handler(self, other_cells):
        for other_cell in other_cells:
            if other_cell != self:
                distance = math.sqrt((self.x - other_cell.x) ** 2 + (self.y - other_cell.y) ** 2)
                if distance < self.energy + other_cell.energy:
                    if other_cell.type != 'photosynthetic':
                        angle = math.atan2(other_cell.y - self.y, other_cell.x - self.x)
                        self.direction = angle + math.pi


    def move(self, other_cells):
        self.collision_handler(other_cells)

        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

        # Wrap around the screen
        self.x = self.x % SIM_WIDTH
        self.y = self.y % SIM_HEIGHT

    def eat(self, food):
        distance = math.sqrt((self.x - food.x) ** 2 + (self.y - food.y) ** 2)
        if distance < self.energy / 2 + FOOD_SIZE / 2:
            self.energy += FOOD_ENERGY * self.herbivory
            return True
        return False

    def draw(self):
        pygame.draw.circle(screen, self.colour, (round(self.x), round(self.y)), round(self.energy))
        font = pygame.font.Font(None, 20)
        text = font.render(str(round(self.energy)), True, WHITE)
        text_rect = text.get_rect(center=(round(self.x), round(self.y)))
        screen.blit(text, text_rect)

    def split(self):
        if self.energy >= 20:
            self.energy = 10  

            new_cell_type = Cell
            if self.type == 'fast':
                new_cell_type = FastCell
            elif self.type == 'slow':
                new_cell_type = SlowCell
            elif self.type == 'pred':
                new_cell_type = PredaCell
            elif self.type == 'photosynthetic':
                new_cell_type = PhotoCell
                
            new_cell = new_cell_type(self.x + random.uniform(-10, 10), self.y + random.uniform(-10, 10))
            main.all_cells.append(new_cell)

class FastCell(Cell):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.color = BLUE  
        self.speed = CELL_SPEED * 4
        self.type = 'fast'
        self.colour = BLUE
        self.dfns = 0.5

    def move(self, other_cells):
        self.collision_handler(other_cells)

        self.x += (self.speed / 3) * math.cos(self.direction)
        self.y += (self.speed / 3) * math.sin(self.direction)

        self.x = self.x % SIM_WIDTH
        self.y = self.y % SIM_HEIGHT

class SlowCell(Cell):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = CELL_SPEED / 2
        self.type = 'slow'
        self.colour = PURPLE 
        self.dfns = 5

    def move(self, other_cells):
        self.collision_handler(other_cells)

        self.x += self.speed * math.cos(self.direction)
        self.y += self.speed * math.sin(self.direction)

        self.x = self.x % SIM_WIDTH
        self.y = self.y % SIM_HEIGHT

class PredaCell(Cell):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.speed = CELL_SPEED / 2
        self.type = 'pred'
        self.colour = BLOOD
        self.last_attacked_cell = None
        self.herbivory = 0.2


    def chase_closest_cell(self, other_cells):
        closest_cell = self.find_closest_cell(other_cells)
        if closest_cell:
            dx = closest_cell.x - self.x
            dy = closest_cell.y - self.y
            self.distance = math.sqrt(dx ** 2 + dy ** 2)
            if self.distance != 0:
                self.direction = math.atan2(dy, dx)

    def move(self, other_cells):
        self.collision_handler(other_cells)
        self.chase_closest_cell(other_cells)

        self.x += (self.speed * 100/self.distance) * math.cos(self.direction)
        self.y += (self.speed * 100/self.distance) * math.sin(self.direction)

        self.x = self.x % SIM_WIDTH
        self.y = self.y % SIM_HEIGHT

    def find_closest_cell(self, other_cells):
        closest_cell = None
        min_distance = float('inf')
        for other_cell in other_cells:
            if other_cell != self and other_cell.type != self.type and other_cell != self.last_attacked_cell:
                distance = math.sqrt((self.x - other_cell.x) ** 2 + (self.y - other_cell.y) ** 2)
                if distance < min_distance:
                    min_distance = distance
                    closest_cell = other_cell
        return closest_cell

    def collision_handler(self, other_cells):
        for other_cell in other_cells:
            if other_cell != self and other_cell != self.last_attacked_cell:
                distance = math.sqrt((self.x - other_cell.x) ** 2 + (self.y - other_cell.y) ** 2)
                if distance < self.energy + other_cell.energy:
                    angle = math.atan2(other_cell.y - self.y, other_cell.x - self.x)
                    self.direction = angle + math.pi
                    if self.type != other_cell.type:
                        # Deal damage to the collided cell
                        dmg = (self.energy / 8) / other_cell.dfns
                        other_cell.energy -= dmg
                        self.energy += dmg

                        self.last_attacked_cell = other_cell


                        

    def draw(self):
        cell_size = round(self.energy)
        pygame.draw.rect(screen, self.colour, (self.x - cell_size // 2, self.y - cell_size // 2, cell_size, cell_size))
        font = pygame.font.Font(None, 20)
        text = font.render(str(round(self.energy)), True, WHITE)
        text_rect = text.get_rect(center=(round(self.x), round(self.y)))
        screen.blit(text, text_rect)

class PhotoCell(Cell):
    def __init__(self, x, y):
        super().__init__(x, y)
        self.energy = INITIAL_ENERGY
        self.type = 'photosynthetic'
        self.colour = GREENGREEN

    def move(self):
        pass

    def photosynthesize(self):
        self.energy += 0.05

    def draw(self):
        pygame.draw.circle(screen, self.colour, (round(self.x), round(self.y)), round(self.energy),2)
        font = pygame.font.Font(None, 20)
        text = font.render(str(round(self.energy)), True, WHITE)
        text_rect = text.get_rect(center=(round(self.x), round(self.y)))
        screen.blit(text, text_rect)

class Food:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def draw(self):
        pygame.draw.circle(screen, GREEN, (self.x, self.y), FOOD_SIZE)

class Main():
    cells = [Cell(random.randint(0, SIM_WIDTH), random.randint(0, SIM_HEIGHT)) for _ in range(5)]
    fast_cells = [FastCell(random.randint(0, SIM_WIDTH), random.randint(0, SIM_HEIGHT)) for _ in range(5)]
    slow_cells = [SlowCell(random.randint(0, SIM_WIDTH), random.randint(0, SIM_HEIGHT)) for _ in range(5)]
    preda_cells = [PredaCell(random.randint(0, SIM_WIDTH), random.randint(0, SIM_HEIGHT)) for _ in range(2)]
    photo_cells = [PhotoCell(random.randint(0, SIM_WIDTH), random.randint(0, SIM_HEIGHT)) for _ in range(5)]

    all_cells = cells + fast_cells + slow_cells + preda_cells + photo_cells
    foods = [Food(random.randint(0, SIM_WIDTH), random.randint(0, SIM_HEIGHT)) for _ in range(50)]

    food_spawn_timer = FOOD_SPAWN_RATE

    running = True
    ticks = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        self.food_spawn_timer -= 1
        self.ticks += 1
        if self.food_spawn_timer <= 0:
            self.foods.append(Food(random.randint(0, SIM_WIDTH), random.randint(0, SIM_HEIGHT)))
            self.food_spawn_timer = FOOD_SPAWN_RATE

        for cell in self.all_cells[:]:

            if cell.type == 'photosynthetic':
                cell.photosynthesize()
                cell.move()
            else:
                cell.move(self.all_cells)

            food_eaten = False
            for food in self.foods[:]:
                if cell.eat(food):
                    self.foods.remove(food)
                    food_eaten = True

            if not food_eaten:
                closest_food = min(self.foods, key=lambda f: math.sqrt((cell.x - f.x) ** 2 + (cell.y - f.y) ** 2))
                cell.move_towards_food(closest_food)

            cell.energy -= (SIZE_REDUCTION_RATE * cell.speed) / 8
            cell.split()

            if cell.energy <= MINIMUM_CELL_SIZE:
                self.all_cells.remove(cell)

    def draw_objects(self):
        screen.fill(GREY)
        for cell in self.all_cells:
            cell.draw()
        for food in self.foods:
            food.draw()

main = Main()

while main.running:
    main.handle_events()
    main.update()
    main.draw_objects()

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
