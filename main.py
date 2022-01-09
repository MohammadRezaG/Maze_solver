import pygame
from queue import PriorityQueue

# import threading


pygame.init()
WIDTH = 800
WIN = pygame.display.set_mode((WIDTH, WIDTH + 100))
pygame.display.set_caption("A* Path Finding Algorithm_MRG")


def create_fonts(font_sizes_list):
    "Creates different fonts with one list"
    fonts = []
    for size in font_sizes_list:
        fonts.append(
            pygame.font.SysFont("Arial", size))
    return fonts


avg_fps = []
FONTS = create_fonts([32, 27, 21, 16])
RED = (255, 0, 100)
GREEN = (0, 255, 0)
BLUE = (0, 255, 0)
YELLOW = (255, 255, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
PURPLE = (128, 0, 128)
ORANGE = (255, 165, 0)
GREY = (128, 128, 128)
TURQUOISE = (64, 224, 208)
ROWS = 50
CLOCK = pygame.time.Clock()
CLOCK_ALGORITHM = pygame.time.Clock()
DIAGONAL = False


class Cell:
    def __init__(self, row, col, width, total_rows):
        self.row = row
        self.col = col
        self.x = row * width
        self.y = col * width
        self.color = WHITE
        self.neighbors = []
        self.width = width
        self.total_rows = total_rows
        self.g_score = float("inf")
        self.f_score = float("inf")
        self.came_from = None

    def get_pos(self):
        return self.row, self.col

    def is_closed(self):
        return self.color == RED

    def is_open(self):
        return self.color == GREEN

    def is_barrier(self):
        return self.color == BLACK

    def is_start(self):
        return self.color == ORANGE

    def is_end(self):
        return self.color == TURQUOISE

    def reset(self):
        self.color = WHITE

    def make_start(self):
        self.color = ORANGE

    def make_closed(self):
        self.color = RED

    def make_open(self):
        self.color = GREEN

    def make_barrier(self):
        self.color = BLACK

    def make_end(self):
        self.color = TURQUOISE

    def make_path(self):
        self.color = PURPLE

    def draw(self, screen):
        pygame.draw.rect(
            screen, self.color, (self.x, self.y, self.width, self.width))

    def init_node(self, grid):
        self.neighbors = []

        if self.row < self.total_rows - 1 and not grid[self.row + 1][self.col].is_barrier():  # DOWN
            self.neighbors.append(grid[self.row + 1][self.col])

        if self.row > 0 and not grid[self.row - 1][self.col].is_barrier():  # UP
            self.neighbors.append(grid[self.row - 1][self.col])

        if self.col < self.total_rows - 1 and not grid[self.row][self.col + 1].is_barrier():  # RIGHT
            self.neighbors.append(grid[self.row][self.col + 1])

        if self.col > 0 and not grid[self.row][self.col - 1].is_barrier():  # LEFT
            self.neighbors.append(grid[self.row][self.col - 1])
        if DIAGONAL:
            if (self.row < self.total_rows - 1 and self.col < self.total_rows - 1) and not grid[self.row + 1][
                self.col + 1].is_barrier():  # DOWN RIGHT
                self.neighbors.append(grid[self.row + 1][self.col + 1])

            if (self.row < self.total_rows - 1 and self.col > 0) and not grid[self.row + 1][self.col - 1].is_barrier():
                self.neighbors.append(grid[self.row + 1][self.col - 1])  # DOWN LEFT

            if (self.row > 0 and self.col < self.total_rows - 1) and not grid[self.row - 1][
                self.col + 1].is_barrier():  # UP RIGHT
                self.neighbors.append(grid[self.row - 1][self.col + 1])

            if (self.row > 0 and self.col > 0) and not grid[self.row - 1][self.col - 1].is_barrier():  # UP LEFT
                self.neighbors.append(grid[self.row - 1][self.col - 1])

        self.g_score = float("inf")
        self.f_score = float("inf")
        self.came_from = None

    def __lt__(self, o):
        return self.f_score < o.f_score

    def __le__(self, o):
        return self.f_score <= o.f_score

    def __gt__(self, o):
        return self.f_score > o.f_score

    def __ge__(self, o):
        return self.f_score <= o.f_score


def make_grid(rows, width):
    grid = []
    gap = width // rows
    for i in range(rows):
        grid.append([])
        for j in range(rows):
            cell = Cell(i, j, gap, rows)
            grid[i].append(cell)

    return grid


def draw_grid(screen, rows, width):
    gap = width // rows
    for i in range(rows):
        pygame.draw.line(screen, GREY, (0, i * gap), (width, i * gap))
        for j in range(rows):
            pygame.draw.line(screen, GREY, (j * gap, 0), (j * gap, width))


def render_txt(fnt, what, color, where):
    "Renders the fonts as passed from display_fps"
    text_to_show = fnt.render(what, 1, color)
    WIN.blit(text_to_show, where)


def draw(screen, grid, rows, width):
    screen.fill(WHITE)
    render_txt(FONTS[1], f'FPS {CLOCK.get_fps()}', RED, (20, 810))
    render_txt(FONTS[1], f'FPS algoritm {CLOCK_ALGORITHM.get_fps()}', GREEN, (20, 840))
    if len(avg_fps) != 0:
        render_txt(FONTS[1], f'AV FPS algoritm {sum(avg_fps) / len(avg_fps)}', GREEN, (360, 840))
    else:
        render_txt(FONTS[1], f'AV FPS algoritm 0', GREEN, (350, 840))

    for row in grid:
        for node in row:
            node.draw(screen)

    draw_grid(screen, rows, width)
    CLOCK.tick(60)
    pygame.display.update()


def get_clicked_cell(pos, grid, rows, width):
    gap = width // rows
    x, y = pos

    if x >= 800:
        x = 799

    row = x // gap
    col = y // gap

    return grid[row][col]


def h(p1, p2):
    x1, y1 = p1
    x2, y2 = p2
    return abs(x1 - x2) + abs(y1 - y2)


# def reconstruct_path(came_from, current, draw):
#     while current in came_from:
#         current = came_from[current]
#         current.make_path()
#         draw()

def reconstruct_path(start: Cell, current: Cell, draw):
    while current != start:
        current = current.came_from
        current.make_path()
        draw()


def algorithm(draw, grid, start: Cell, end: Cell):
    global avg_fps
    avg_fps = []
    count = 0
    open_set = PriorityQueue()
    open_set.put((0, count, start))

    start.g_score = 0
    start.f_score = h(start.get_pos(), end.get_pos())
    open_set_hash = {start}

    while not open_set.empty():
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        current = open_set.get()[2]
        open_set_hash.remove(current)

        if current == end:
            reconstruct_path(start, end, draw)
            start.make_start()
            end.make_end()
            return True

        for neighbor in current.neighbors:
            temp_g_score = current.g_score + 1

            if temp_g_score < neighbor.g_score:
                neighbor.came_from = current
                neighbor.g_score = temp_g_score
                neighbor.f_score = temp_g_score + h(neighbor.get_pos(), end.get_pos())
                if neighbor not in open_set_hash:
                    count += 1
                    open_set.put((neighbor.f_score, count, neighbor))
                    open_set_hash.add(neighbor)
                    neighbor.make_open()

        CLOCK_ALGORITHM.tick(60)
        avg_fps.append(CLOCK_ALGORITHM.get_fps())
        draw()

        if current != start:
            current.make_closed()

    return False


def main(screen, width):
    grid = make_grid(ROWS, width)

    start = None
    end = None

    run = True
    while run:
        draw(screen, grid, ROWS, width)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

            if pygame.mouse.get_pressed()[0]:  # LEFT
                pos = pygame.mouse.get_pos()
                clicked_cell = get_clicked_cell(pos, grid, ROWS, width)
                if not start and clicked_cell != end:
                    start = clicked_cell
                    start.make_start()

                elif not end and clicked_cell != start:
                    end = clicked_cell
                    end.make_end()

                elif clicked_cell != end and clicked_cell != start:
                    keys = pygame.key.get_pressed()
                    if keys[pygame.K_s]:
                        start.reset()
                        start = clicked_cell
                        start.make_start()
                    elif keys[pygame.K_e]:
                        end.reset()
                        end = clicked_cell
                        end.make_end()
                    else:
                        clicked_cell.make_barrier()

            elif pygame.mouse.get_pressed()[2]:  # RIGHT
                pos = pygame.mouse.get_pos()
                clicked_cell = get_clicked_cell(pos, grid, ROWS, width)
                clicked_cell.reset()
                if clicked_cell == start:
                    start = None
                elif clicked_cell == end:
                    end = None

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE and start and end:
                    for row in grid:
                        for clicked_cell in row:
                            clicked_cell.init_node(grid)

                    algorithm(lambda: draw(screen, grid, ROWS, width), grid, start, end)

                if event.key == pygame.K_c:
                    start = None
                    end = None
                    grid = make_grid(ROWS, width)

    pygame.quit()


if __name__ == '__main__':
    main(WIN, WIDTH)
