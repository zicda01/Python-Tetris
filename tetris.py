import pygame
import random

print("Pygame 초기화 시작...") # 이 줄을 추가
pygame.init()
print("Pygame 초기화 완료!") # 이 줄을 추가

# --- 화면 및 게임 설정 ---
SCREEN_WIDTH = 300
SCREEN_HEIGHT = 600
BLOCK_SIZE = 30
COLUMNS = 10
ROWS = 20

# --- 색상 정의 ---
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)
COLORS = [
    (0, 255, 255), # I (시안)
    (0, 0, 255),   # J (파랑)
    (255, 165, 0), # L (주황)
    (255, 255, 0), # O (노랑)
    (0, 255, 0),   # S (초록)
    (128, 0, 128), # T (보라)
    (255, 0, 0)    # Z (빨강)
]

# --- 테트로미노 모양 정의 ---
# 각 배열은 회전 상태를 나타냅니다 (1이 그려지는 블록)
SHAPES = [
    # I
    [[[0,0,0,0], [1,1,1,1], [0,0,0,0], [0,0,0,0]],
     [[0,1,0,0], [0,1,0,0], [0,1,0,0], [0,1,0,0]]],
    # J
    [[[1,0,0], [1,1,1], [0,0,0]],
     [[0,1,1], [0,1,0], [0,1,0]],
     [[0,0,0], [1,1,1], [0,0,1]],
     [[0,1,0], [0,1,0], [1,1,0]]],
    # L
    [[[0,0,1], [1,1,1], [0,0,0]],
     [[0,1,0], [0,1,0], [0,1,1]],
     [[0,0,0], [1,1,1], [1,0,0]],
     [[1,1,0], [0,1,0], [0,1,0]]],
    # O
    [[[1,1], [1,1]]],
    # S
    [[[0,1,1], [1,1,0], [0,0,0]],
     [[0,1,0], [0,1,1], [0,0,1]]],
    # T
    [[[0,1,0], [1,1,1], [0,0,0]],
     [[0,1,0], [0,1,1], [0,1,0]],
     [[0,0,0], [1,1,1], [0,1,0]],
     [[0,1,0], [1,1,0], [0,1,0]]],
    # Z
    [[[1,1,0], [0,1,1], [0,0,0]],
     [[0,0,1], [0,1,1], [0,1,0]]]
]

class Piece:
    """현재 떨어지는 블록(테트로미노)의 상태를 관리하는 클래스"""
    def __init__(self, x, y, shape_idx):
        self.x = x
        self.y = y
        self.shape_idx = shape_idx
        self.color = COLORS[shape_idx]
        self.rotation = 0 # 현재 회전 상태

    @property
    def image(self):
        """현재 회전 상태에 맞는 블록의 형태를 반환"""
        return SHAPES[self.shape_idx][self.rotation % len(SHAPES[self.shape_idx])]

def create_grid(locked_positions={}):
    """화면에 표시될 2D 그리드를 생성합니다."""
    grid = [[BLACK for _ in range(COLUMNS)] for _ in range(ROWS)]
    for y in range(ROWS):
        for x in range(COLUMNS):
            if (x, y) in locked_positions:
                grid[y][x] = locked_positions[(x, y)]
    return grid

def valid_space(piece, grid):
    """블록이 이동하거나 회전할 위치가 유효한지(벽이나 다른 블록과 충돌하지 않는지) 검사합니다."""
    accepted_positions = [[(x, y) for x in range(COLUMNS) if grid[y][x] == BLACK] for y in range(ROWS)]
    accepted_positions = [x for item in accepted_positions for x in item]

    formatted = []
    for y, row in enumerate(piece.image):
        for x, col in enumerate(row):
            if col == 1:
                formatted.append((piece.x + x, piece.y + y))

    for pos in formatted:
        if pos not in accepted_positions:
            # 블록이 화면 위에서 시작될 때는 예외 처리
            if pos[1] > -1:
                return False
    return True

def check_lost(locked_positions):
    """블록이 화면 꼭대기까지 닿았는지(게임 오버) 확인합니다."""
    for pos in locked_positions:
        if pos[1] < 1:
            return True
    return False

def get_shape():
    """새로운 무작위 블록을 생성합니다."""
    return Piece(COLUMNS // 2 - 2, 0, random.randint(0, len(SHAPES) - 1))

def clear_rows(locked):
    """가로로 꽉 찬 줄이 있는지 확인하고 삭제한 뒤, 위에 있는 블록들을 아래로 내립니다."""
    lines_cleared = 0
    y = ROWS - 1
    while y >= 0:
        # 현재 줄이 모두 블록으로 꽉 차 있는지 확인
        if all((x, y) in locked for x in range(COLUMNS)):
            lines_cleared += 1
            # 해당 줄 삭제
            for x in range(COLUMNS):
                del locked[(x, y)]
            # 삭제된 줄 위에 있는 모든 블록을 한 칸씩 아래로 이동
            for move_y in range(y - 1, -1, -1):
                for x in range(COLUMNS):
                    if (x, move_y) in locked:
                        locked[(x, move_y + 1)] = locked.pop((x, move_y))
        else:
            y -= 1
    return lines_cleared

def draw_grid(surface, grid):
    """화면에 그리드 선과 블록들을 그립니다."""
    # 블록 색상 채우기
    for y in range(ROWS):
        for x in range(COLUMNS):
            pygame.draw.rect(surface, grid[y][x], (x * BLOCK_SIZE, y * BLOCK_SIZE, BLOCK_SIZE, BLOCK_SIZE), 0)

    # 격자 선 그리기
    for y in range(ROWS):
        pygame.draw.line(surface, GRAY, (0, y * BLOCK_SIZE), (SCREEN_WIDTH, y * BLOCK_SIZE))
    for x in range(COLUMNS):
        pygame.draw.line(surface, GRAY, (x * BLOCK_SIZE, 0), (x * BLOCK_SIZE, SCREEN_HEIGHT))

def draw_window(surface, grid):
    surface.fill(BLACK)
    draw_grid(surface, grid)
    pygame.display.update()

def main():
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption('테트리스 (Tetris)')
    clock = pygame.time.Clock()

    locked_positions = {}
    grid = create_grid(locked_positions)

    change_piece = False
    run = True
    current_piece = get_shape()
    next_piece = get_shape()

    fall_time = 0
    fall_speed = 0.3 # 블록이 떨어지는 기본 속도 (초 단위)

    while run:
        grid = create_grid(locked_positions)
        fall_time += clock.get_rawtime()
        clock.tick()

        # 블록 자동 낙하 로직
        if fall_time / 1000 >= fall_speed:
            fall_time = 0
            current_piece.y += 1
            # 바닥이나 다른 블록에 닿았을 때
            if not valid_space(current_piece, grid) and current_piece.y > 0:
                current_piece.y -= 1
                change_piece = True

        # 키보드 이벤트 처리
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.display.quit()
                quit()

            if event.type == pygame.KEYDOWN:
                # 좌측 이동
                if event.key == pygame.K_LEFT:
                    current_piece.x -= 1
                    if not valid_space(current_piece, grid):
                        current_piece.x += 1 # 이동 불가능하면 원상복구
                        
                # 우측 이동
                elif event.key == pygame.K_RIGHT:
                    current_piece.x += 1
                    if not valid_space(current_piece, grid):
                        current_piece.x -= 1
                        
                # 시계방향 회전
                elif event.key == pygame.K_UP:
                    current_piece.rotation += 1
                    if not valid_space(current_piece, grid):
                        current_piece.rotation -= 1
                        
                # 아래로 빠르게 이동 (소프트 드롭)
                elif event.key == pygame.K_DOWN:
                    current_piece.y += 1
                    if not valid_space(current_piece, grid):
                        current_piece.y -= 1
                        
                # 한 번에 바닥으로 떨어지기 (하드 드롭)
                elif event.key == pygame.K_SPACE:
                    while valid_space(current_piece, grid):
                        current_piece.y += 1
                    current_piece.y -= 1 # 유효한 마지막 위치로 보정

        shape_pos = []
        for y, row in enumerate(current_piece.image):
            for x, col in enumerate(row):
                if col == 1:
                    shape_pos.append((current_piece.x + x, current_piece.y + y))

        # 현재 떨어지고 있는 블록을 화면 그리드에 추가
        for pos in shape_pos:
            x, y = pos
            if y > -1:
                grid[y][x] = current_piece.color

        # 블록이 바닥에 닿아 고정되어야 할 때
        if change_piece:
            for pos in shape_pos:
                p = (pos[0], pos[1])
                locked_positions[p] = current_piece.color
            
            # 새 블록 생성
            current_piece = next_piece
            next_piece = get_shape()
            change_piece = False
            
            # 줄이 꽉 찼는지 확인 후 삭제
            clear_rows(locked_positions)

        draw_window(screen, grid)

        # 게임 오버 체크
        if check_lost(locked_positions):
            run = False

    pygame.display.quit()

if __name__ == '__main__':
    main()