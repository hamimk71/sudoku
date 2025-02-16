import csv
import pygame
import copy
import random
import os

# Constants
CELL_SIZE = 30
GRID_SIZE = CELL_SIZE * 9
BUTTON_SIZE = 30
MARGIN = 10
MARGIN_NUM_PAD = 5

COLORS = {
    'background': (192, 192, 192),      # GRAY
    'grid_line': (0, 0, 0),             # BLACK
    'fixed_text': (0, 0, 139),          # NAVY BLUE
    'user_text': (50, 0, 0),            # BLACK RED 
    'selected': (180, 0, 0),            # DARK RED
    'num_button': (0, 100, 0),          # GREEN
    'info_button': (50,0,0),            # BLACK RED    
    'instruction_button': (0, 0, 0),
    'button_text': (255, 255, 255)
}

def play_sound(sound_file):
    try:
        pygame.mixer.music.load(sound_file)
        pygame.mixer.music.play()
    except pygame.error as e:
        print(f"Error playing sound {sound_file}: {e}")

def read_board_from_file(filename):
    board = [[0]*9 for _ in range(9)]
    try:
        with open(filename, 'r') as file:
            reader = csv.reader(file)
            for idx, row in enumerate(reader):
                if idx >= 9:
                    break
                if len(row) != 9:
                    raise ValueError("Row must have 9 elements")
                converted_row = [int(num) if num.strip().isdigit() else 0 for num in row]
                board[idx] = converted_row
            return board
    except Exception as e:
        print(f"Error: {e}")
        return [[0]*9 for _ in range(9)]

def write_board_to_file(filename, board):
    try:
        with open(filename, 'w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(board)
    except Exception as e:
        print(f"Error writing file: {e}")
###########################################################################################################################
def is_valid_move(board, row, col, num):
    for i in range(9):
        if board[row][i] == num or board[i][col] == num:
            return False
    start_row, start_col = 3 * (row // 3), 3 * (col // 3)
    for i in range(3):
        for j in range(3):
            if board[start_row + i][start_col + j] == num:
                return False
    return True
##########################################################################################################################
def solve_sudoku(board):
    empty = find_empty_cell(board)
    if not empty:
        return True
    row, col = empty
    for num in range(1, 10):
        if is_valid_move(board, row, col, num):
            board[row][col] = num
            if solve_sudoku(board):
                return True
            board[row][col] = 0
    return False
##########################################################################################################################
def find_empty_cell(board):
    for i in range(9):
        for j in range(9):
            if board[i][j] == 0:
                return (i, j)
    return None
##########################################################################################################################
def draw_grid(screen, position):
    top_left_x, top_left_y = position
    for i in range(10):
        thickness = 4 if i % 3 == 0 else 2
        pygame.draw.line(screen, COLORS['grid_line'],
                         (top_left_x, top_left_y + i * CELL_SIZE),
                         (top_left_x + GRID_SIZE, top_left_y + i * CELL_SIZE),
                         thickness)
        pygame.draw.line(screen, COLORS['grid_line'],
                         (top_left_x + i * CELL_SIZE, top_left_y),
                         (top_left_x + i * CELL_SIZE, top_left_y + GRID_SIZE),
                         thickness)

######################################################################################################################
def draw_numbers(screen, board, prev_board, position, selected):
    font = pygame.font.SysFont('Arial', 24)
    top_left_x, top_left_y = position
    if board is not None:
        for i in range(9):
            for j in range(9):
                num = board[i][j]
                if num == 0:
                    continue
                color = COLORS['fixed_text'] if prev_board[i][j] != 0 else COLORS['user_text']
                text = font.render(str(num), True, color)
                x = top_left_x + j * CELL_SIZE + (CELL_SIZE - text.get_width()) // 2
                y = top_left_y + i * CELL_SIZE + (CELL_SIZE - text.get_height()) // 2
                screen.blit(text, (x, y))
        if selected:
            row, col = selected
            pygame.draw.rect(screen, COLORS['selected'],
                             (top_left_x + col * CELL_SIZE, top_left_y + row * CELL_SIZE, CELL_SIZE, CELL_SIZE), 2)
    else:
        print(f"draw_numbers(): Board is Empty!")
###########################################################################################################################
def draw_buttons(screen, grid_position, count_error, start_time):
    buttons = {}
    screen_width = screen.get_width()

    number_pad_y = grid_position[1] + GRID_SIZE + MARGIN * 2
    total_num_width = 9 * (BUTTON_SIZE + MARGIN_NUM_PAD)
    start_x = (screen_width - total_num_width) // 2
    for i in range(9):
        x = start_x + i * (BUTTON_SIZE + MARGIN_NUM_PAD)
        rect = pygame.Rect(x, number_pad_y, BUTTON_SIZE, BUTTON_SIZE)
        pygame.draw.rect(screen, COLORS['num_button'], rect)
        font = pygame.font.SysFont('Arial', 20, bold=True)
        text = font.render(str(i+1), True, COLORS['button_text'])
        text_rect = text.get_rect(center=rect.center)
        screen.blit(text, text_rect)
        buttons[str(i+1)] = rect

    error_counter_y = number_pad_y + BUTTON_SIZE + MARGIN
    font = pygame.font.SysFont('Arial', 16, bold=True)

    error_text = f"ERRORS: {count_error}"
    error_surface = font.render(error_text, True, COLORS['button_text'])
    error_width = error_surface.get_width() + 20

    elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
    hours = elapsed_time // 3600
    minutes = (elapsed_time % 3600) // 60
    seconds = elapsed_time % 60
    info_text = f"TIME: {hours:02}:{minutes:02}:{seconds:02}"
    info_surface = pygame.font.SysFont('Arial', 16, bold=True).render(info_text, True, COLORS['button_text'])
    info_width = info_surface.get_width() + 20

    total_width = error_width + info_width + MARGIN
    start_x = (screen_width - total_width) // 2

    error_rect = pygame.Rect(start_x, error_counter_y, error_width, BUTTON_SIZE)
    pygame.draw.rect(screen, COLORS['info_button'], error_rect)
    screen.blit(error_surface, (start_x + 10, error_counter_y + (BUTTON_SIZE - error_surface.get_height()) // 2))
    buttons["ERROR COUNTER"] = error_rect

    info_rect = pygame.Rect(start_x + error_width + MARGIN, error_counter_y, info_width, BUTTON_SIZE)
    pygame.draw.rect(screen, COLORS['info_button'], info_rect)
    screen.blit(info_surface, (info_rect.x + 10, error_counter_y + (BUTTON_SIZE - info_surface.get_height()) // 2))
    buttons["INFO"] = info_rect

    controls = ['SOLVE', 'NEW','REPLAY', 'EMPTY', 'QUIT']
    num_controls = len(controls)
    total_control_width = num_controls * (BUTTON_SIZE * 2 + MARGIN) - MARGIN
    if total_control_width > screen_width:
        button_width = (screen_width - (num_controls + 1) * MARGIN) // num_controls
    else:
        button_width = BUTTON_SIZE * 2

    start_x = (screen_width - total_control_width) // 2
    y = GRID_SIZE + BUTTON_SIZE + MARGIN + BUTTON_SIZE + MARGIN + 50
    for i, label in enumerate(controls):
        x = start_x + i * (button_width + MARGIN)
        rect = pygame.Rect(x, y, button_width, BUTTON_SIZE)
        pygame.draw.rect(screen, COLORS['instruction_button'], rect)
        text = pygame.font.SysFont('Arial', 16, bold=True).render(label, True, COLORS['button_text'])
        screen.blit(text, (x + 5, y + 5))
        buttons[label] = rect

    return buttons
##########################################################################################################################
def draw_background_moles(screen, board, prev_board, position):

    x = y = 0

    try:
        mole_image = pygame.image.load('img_mole.png')
    except pygame.error as e:
        print(f"Error loading mole image: {e}")
        return

    mole_image = pygame.transform.scale(mole_image, (CELL_SIZE - 4, CELL_SIZE - 4))
    top_left_x, top_left_y = position
    font = pygame.font.SysFont('Arial', 24)

    for i in range(9):
        for j in range(9):
            if prev_board[i][j] == 0 or board[i][j] == 0:
                x = top_left_x + j * CELL_SIZE + 2
                y = top_left_y + i * CELL_SIZE + 2
                screen.blit(mole_image, (x, y))            
            text = font.render(" ", True, COLORS['user_text'])
            text_rect = text.get_rect(center=(x + CELL_SIZE // 2, y + CELL_SIZE // 2))
            screen.blit(text, text_rect)
############################################################################################################################
def generate_board(board, num_missing_cell):

    solved_board = copy.deepcopy(board)
    if not solve_sudoku(solved_board):
        print("Failed to generate a Sudoku solution.")
        return board
    
    for i in range(9):
        for j in range(9):
            board[i][j] = solved_board[i][j]
    
    count = 0
    while count < num_missing_cell:
        row = random.randint(0, 8)
        col = random.randint(0, 8)
        if board[row][col] != 0:
            board[row][col] = 0
            count += 1
    
    return board
############################################################################################################################
def draw_background(screen):
    background_image = pygame.image.load('img_bg1.png')
    background_image = pygame.transform.scale(background_image, (screen.get_width() // 3, screen.get_height()))
    screen.fill(COLORS['background'])
    screen.blit(background_image, (0, 0))

def main():
    global grid_position
    grid_position = (0, 0)
    levels = {"Beginner":15,
             "Intermediate":35,
             "Advanced":55,
             "Pro":65}
    count_error = 0
    start_time = pygame.time.get_ticks()
    os.chdir('C:/Users/hamim/OneDrive/Desktop/Python/Working')
    pygame.init()
    screen = pygame.display.set_mode((GRID_SIZE + MARGIN * 2, GRID_SIZE + BUTTON_SIZE * 4 + MARGIN * 5), pygame.RESIZABLE)

    ori_board = read_board_from_file('sudoku_board.csv')
    if not ori_board or len(ori_board) != 9 or any(len(row) != 9 for row in ori_board):
        print("Failed to load the board or board is not a 9x9 grid.")
        return

    board = copy.deepcopy(ori_board)
    prev_board = copy.deepcopy(ori_board)
    selected_cell = None
    running = True
    label = "NEW"

    while running:
        draw_background(screen)
        screen.fill(COLORS['background'], (grid_position[0], grid_position[1], GRID_SIZE, GRID_SIZE))
        grid_x = (screen.get_width() - GRID_SIZE) // 2
        grid_position = (grid_x, MARGIN)
        buttons = draw_buttons(screen, grid_position, count_error, start_time)
        draw_grid(screen, grid_position)
    
        draw_background_moles(screen, board, prev_board, grid_position)
        draw_numbers(screen, board, prev_board, grid_position, selected_cell)
        pygame.display.update()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if (grid_position[0] < x < grid_position[0] + GRID_SIZE and
                    grid_position[1] < y < grid_position[1] + GRID_SIZE):
                    col = (x - grid_position[0]) // CELL_SIZE
                    row = (y - grid_position[1]) // CELL_SIZE
                    if board[row][col] == 0:
                        selected_cell = (row, col)
                for label, rect in buttons.items():
                    if rect.collidepoint(x, y):
                        if label == 'QUIT':
                            play_sound("noti_alarm.mp3")
                            pygame.time.delay(3000)
                            running = False
                        elif label == 'SOLVE':
                            temp_board = copy.deepcopy(board)
                            if solve_sudoku(temp_board):
                                board = temp_board
                                play_sound("noti_happy.wav")
                            else:
                                 play_sound("noti_alarm.mp3")
                        elif label == 'NEW':
                            ori_board = copy.deepcopy(prev_board)
                            board = generate_board(board,levels['Intermediate'])
                            prev_board = copy.deepcopy(board)
                            play_sound("noti_confirm.wav")
                        elif label == 'REPLAY':
                            if all(cell == 0 for row in prev_board for cell in row):
                                board = copy.deepcopy(ori_board)
                                prev_board = copy.deepcopy(ori_board)
                                play_sound("noti_error.mp3")
                            else:
                                board = copy.deepcopy(prev_board)
                                play_sound("noti_pop.wav")
                        elif label == 'EMPTY':
                            ori_board = copy.deepcopy(prev_board)
                            prev_board = [[0]*9 for _ in range(9)]
                            board = [[0]*9 for _ in range(9)]
                            play_sound("noti_pop.wav")
                        elif label.isdigit() and selected_cell:
                            num = int(label)
                            row, col = selected_cell
                            if is_valid_move(board, row, col, num):
                                board[row][col] = num
                                prev_board[row][col] = num
                                play_sound("noti_confirm.wav")
                            else:
                                count_error += 1
                                play_sound("noti_pop.wav")

    pygame.quit()

if __name__ == "__main__":
    main()