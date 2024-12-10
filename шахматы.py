import pygame
import chess
import chess.engine
import sys
import select
from datetime import datetime

pygame.init()

WINDOW_SIZE = 800
CELL_SIZE = WINDOW_SIZE // 8

WHITE = (245, 245, 220)
BROWN = (139, 69, 19)
HIGHLIGHT = (200, 200, 100)
CHECK_HIGHLIGHT = (255, 100, 100)

PIECES = {
    "r": pygame.image.load("assets/b-t.png"),
    "n": pygame.image.load("assets/b-kn.png"),
    "b": pygame.image.load("assets/b-c.png"),
    "q": pygame.image.load("assets/b-q.png"),
    "k": pygame.image.load("assets/b-k.png"),
    "p": pygame.image.load("assets/b-b.png"),
    "R": pygame.image.load("assets/w-t.png"),
    "N": pygame.image.load("assets/w-kn.png"),
    "B": pygame.image.load("assets/w-c.png"),
    "Q": pygame.image.load("assets/w-q.png"),
    "K": pygame.image.load("assets/w-k.png"),
    "P": pygame.image.load("assets/w-b.png"),
}

for key in PIECES:
    PIECES[key] = pygame.transform.smoothscale(PIECES[key], (CELL_SIZE, CELL_SIZE))


class ChessGame:
    def __init__(self, game_code=None):
        self.board = chess.Board()
        self.selected_square = None
        self.valid_moves = []
        self.engine = chess.engine.SimpleEngine.popen_uci("/opt/homebrew/bin/stockfish")
        self.use_ai = game_code is None
        self.current_player = "white"
        self.message = ""
        self.game_code = game_code or str(int(datetime.now().timestamp()))
        self.move_log = []

    def draw_board(self, screen):
        for row in range(8):
            for col in range(8):
                color = WHITE if (row + col) % 2 == 0 else BROWN
                pygame.draw.rect(screen, color, pygame.Rect(col * CELL_SIZE, row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        if self.board.is_check():
            king_square = self.board.king(chess.WHITE if self.current_player == "white" else chess.BLACK)
            king_row, king_col = divmod(king_square, 8)
            pygame.draw.rect(screen, CHECK_HIGHLIGHT, pygame.Rect(king_col * CELL_SIZE, king_row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for move in self.valid_moves:
            to_row, to_col = divmod(move.to_square, 8)
            pygame.draw.rect(screen, HIGHLIGHT, pygame.Rect(to_col * CELL_SIZE, to_row * CELL_SIZE, CELL_SIZE, CELL_SIZE))

        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                row, col = divmod(square, 8)
                screen.blit(PIECES[piece.symbol()], (col * CELL_SIZE, row * CELL_SIZE))

    def handle_click(self, row, col):
        square = row * 8 + col
        if self.selected_square is None:
            piece = self.board.piece_at(square)
            if piece and ((self.current_player == "white" and piece.color == chess.WHITE) or (self.current_player == "black" and piece.color == chess.BLACK)):
                self.selected_square = square
                self.valid_moves = [move for move in self.board.legal_moves if move.from_square == square]
        else:
            move = chess.Move(self.selected_square, square)
            if move in self.valid_moves:
                self.board.push(move)
                self.log_move(move.uci())
                self.check_game_status()
                self.current_player = "black" if self.current_player == "white" else "white"
            self.selected_square = None
            self.valid_moves = []

    def process_terminal_command(self, command):
        if command == "reset":
            self.board.reset()
            self.current_player = "white"
            self.move_log = []
            self.message = "Partie réinitialisée."
        elif command == "quit":
            self.close_engine()
            sys.exit()
        else:
            try:
                move = chess.Move.from_uci(command)
                if move in self.board.legal_moves:
                    self.board.push(move)
                    self.log_move(command)
                    self.check_game_status()
                    self.current_player = "black" if self.current_player == "white" else "white"
                else:
                    self.message = "Mouvement illégal."
            except ValueError:
                self.message = "Commande invalide."

    def log_move(self, move):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.move_log.append(f"{timestamp}: {move}")
        print(self.move_log[-1])

    def ai_move(self):
        if self.current_player == "black" and self.use_ai:
            result = self.engine.play(self.board, chess.engine.Limit(time=1.0))
            self.board.push(result.move)
            self.log_move(result.move.uci())
            self.check_game_status()
            self.current_player = "white"

    def check_game_status(self):
        if self.board.is_checkmate():
            self.message = "Échec et mat ! " + ("Blancs gagnent" if self.current_player == "black" else "Noirs gagnent")
        elif self.board.is_stalemate():
            self.message = "Partie nulle (Pat)"
        elif self.board.is_check():
            self.message = "Échec !"
        else:
            self.message = ""

    def close_engine(self):
        self.engine.quit()


screen = pygame.display.set_mode((WINDOW_SIZE, WINDOW_SIZE))
pygame.display.set_caption("Chess Game - Terminal Edition")

chess_game = ChessGame()

clock = pygame.time.Clock()
running = True

print(f"Code de la partie : {chess_game.game_code}")
print("Entrez un mouvement (ex : e2e4), 'reset' pour recommencer ou 'quit' pour quitter.")

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            row, col = y // CELL_SIZE, x // CELL_SIZE
            chess_game.handle_click(row, col)

    if chess_game.use_ai:
        chess_game.ai_move()

    chess_game.draw_board(screen)
    pygame.display.flip()

    if sys.stdin in select.select([sys.stdin], [], [], 0)[0]:
        command = input()
        chess_game.process_terminal_command(command)

    clock.tick(60)

chess_game.close_engine()
pygame.quit()
sys.exit()
