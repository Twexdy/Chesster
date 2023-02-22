import pygame
import io

pygame.init()
clock = pygame.time.Clock()


class new:
    class ChessPiece:
        def __init__(self, team, index, coordinates, moved = False):
            self.team = team
            self.index = index
            self.moved = moved
            self.coordinates = coordinates
        def updatePosition(self, new_index_pos, new_coordinate_pos):
            self.index = new_index_pos
            self.coordinates = new_coordinate_pos
            
        
    class Pawn(ChessPiece):
        def __init__(self, team, position, moved = False):
            self.type = "p"
            super().__init__(team, position, moved)
        def __str__(self):
            return f"{self.team}{self.type}"

    class Knight(ChessPiece):
        def __init__(self, team, position, moved = False):
            self.type = "n"
            super().__init__(team, position, moved)
        def __str__(self):
            return f"{self.team}{self.type}"
        
    class Bishop(ChessPiece):
        def __init__(self, team, position, moved = False):
            self.type = "b"
            super().__init__(team, position, moved)
        def __str__(self):
            return f"{self.team}{self.type}"
        
    class Rook(ChessPiece):
        def __init__(self, team, position, moved = False):
            self.type = "r"
            super().__init__(team, position, moved)
        def __str__(self):
            return f"{self.team}{self.type}"
        
    class Queen(ChessPiece):
        def __init__(self, team, position, moved = False):
            self.type = "q"
            super().__init__(team, position, moved)
        def __str__(self):
            return f"{self.team}{self.type}" 
        
    class King(ChessPiece):
        def __init__(self, team, position, moved = False):
            self.type = "k"
            super().__init__(team, position, moved)
        def __str__(self):
            return f"{self.team}{self.type}"
    
# init function
    def __init__(self, start_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1", scale=60, hide_console_messages = False, background_color=(49, 46, 43), light_board_color=(239, 217, 181),
                 dark_board_color=(181, 136, 99), light_highlight_color=(248, 236, 90), 
                 dark_highlight_color=(218, 196, 49), spotlighted_square_color=(240, 240, 240), refresh_rate_cap=60,
                 animation_speed=10, debug_mode = False):
        pygame.display.set_caption("Chesster")
        pygame.mixer.init()

        # drawing pieces and board
        self.hovering_piece = None
        self.highlighted_squares = []
        self.mouse_hovering_over = None
        self.highlight_piece_moves = []
        self.highlighted_attacking_squares = []
        self.background_color = background_color
        self.spotlighted_square_color = spotlighted_square_color
        self.regular_board_colors = [light_board_color, dark_board_color]
        self.highlight_board_colors = [light_highlight_color, dark_highlight_color]
        self.colors = [(242, 130, 116), (213, 89, 75)] 

        # animations
        self.step = 0
        self.animating = None
        self.start_pixel_x = None
        self.end_pixel_x = None
        self.start_pixel_y = None
        self.end_pixel_y = None
        self.animation_speed = animation_speed

        # game logic
        self.start_FEN = start_FEN
        self.turn = "w"
        self.in_check = False
        self.board_length = 8
        self.legal_moves = []
        self.pseudo_legal_moves = []
        self.squares_to_border = [0] * self.board_length ** 2
        self.offsets = {"n": (-10, -17, -15, -6, 10, 17, 15, 6), "b": (-9, -7, 9, 7), "r": (8, -1, -8, 1), "q": (-9, -7, 9, 7, 8, -1, -8, 1 ), "k": (-9, -7,  9, 7, -8, -1, 8, 1)}

        # misc
        self.board = []
        self.last_move = []
        self.sounds = None
        self.sprites = None
        self.xy_mouse_pos = None
        self.selected_piece = None
        self.deselect_flag = False
        self.version = "Pre-alpha"
        self.debug_mode = debug_mode
        self.hide_console_messages = hide_console_messages
        self.piece_id_to_class = {"p": self.Pawn, "n": self.Knight, "b": self.Bishop, "r": self.Rook, "q": self.Queen, "k": self.King, "--": "--"}
        
        # window/UI scaling
        self.scale = scale
        self.refresh_rate_cap = refresh_rate_cap
        self.padding = self.scale * self.board_length // 40
        self.window_size = (2 * (self.scale * self.board_length) + self.padding, self.scale * self.board_length + (self.padding * 2))
        
        self.root_surf = pygame.display.set_mode(self.window_size)
        
                
        self.__log(f"\nChesster {self.version} // Check for updates at [https://github.com/Twexdy/Chesster]")
        self.sounds = None
        self.sprites = {}
        self.loadGame(self.start_FEN)
        
        self.__log(f"\n")

    def __log(self, *message, end = '\n') -> None:
        """Similar to the print() function, but it will not print anything if hide_console_messages is True.

        Args:
            message (any, any): The values to be printed.
            end (str, optional): The end character. Defaults to '\n'.
        """
        if self.hide_console_messages:
            return
        print(*message, end=end)     
        
    def quit(self, message = "Exiting Chesster...") -> None:
        """ Exits chesster with an optional message.
        
        Args:
            message (str, optional): The values to be printed when exiting. Defaults to 'Exiting Chesster'.
         """        
        self.__log(f"{message}")
        pygame.quit()
        exit()
        
    def __lerp(self, x1: float, x2: float, alpha: float) -> float:
        """Returns a value interpolated between a value and a goal value by the fraction alpha.

        Args:
            x1 (float): The initial value
            x2 (float): The goal
            alpha (float): The fraction

        Returns:
            float: The interpolated value
        """
        return (1 - alpha) * x1 + alpha * x2
    
    def __clamp(self, min: float, max: float, val: float) -> float:
        """ Returns max if the given value is bigger than max and vice versa.

        Args:
            min (float): The minimum value the given number can be
            max (float): The maximum value the given number can be
            val (float): The given number

        Returns:
            float: The clamped number
        """
        if val < min:
            return min
        elif val > max:
            return max
        else:
            return val

    def __scaleSvg(self, filename: str, scale):
        """Scales an SVG image to a specific size.

        Args:
            filename (str): The file path to the SVG.
            scale (int): The size to make the SVG

        Returns:
            _type_: _description_
        """
        with open(filename, "rt") as svg:
            svg_string = svg.read()
            start_scale = svg_string.find("<svg")    
            
            first_quote_x = svg_string.find('"', svg_string.find("width") + 1)
            second_quote_x = svg_string.find('"', first_quote_x + 1)
            first_quote_y = svg_string.find('"', svg_string.find("height") + 1)
            second_quote_y = svg_string.find('"', first_quote_y + 1)
            dimensions = float(svg_string[first_quote_x + 1: second_quote_x])
            
            if start_scale and first_quote_x > 0:
                svg_string = f"{svg_string[: first_quote_x + 1:]}{scale}{svg_string[second_quote_x: first_quote_y + 1:]}{scale}{svg_string[second_quote_y: :]}"
                svg_string = svg_string[: start_scale+4] + f' transform="scale({scale * 1/dimensions})"' + svg_string[start_scale+4:]
            
            return io.BytesIO(svg_string.encode())

    def __loadAssets(self):
        try:
            self.__log("Loading sprites...", end='')
            self.sprites = {image: pygame.image.load(self.__scaleSvg(f"main/sprites/{image}.svg", self.scale)) for image in ["wk", "wq", "wr", "wb", "wn", "wp", "bk", "bq", "br", "bb", "bn", "bp"]}
            self.sprites["circle"] = pygame.transform.scale(pygame.image.load("main/sprites/circle.png"), (self.scale, self.scale)).convert_alpha()
            self.sprites["bigcircle"] = pygame.transform.scale(pygame.image.load("main/sprites/bigcircle.png"), (self.scale, self.scale)).convert_alpha()
            self.__log("Done!")
            self.__log("Loading sounds...", end='')
            self.sounds = {sound: pygame.mixer.Sound(f"main/sounds/{sound}.wav") for sound in ["move", "capture", "check", "castle"]}
            self.__log("Done!")
            return self.sprites, self.sounds
        except Exception as e:
                self.__log(f"Error! Make sure your directories are configured correctly.\n{e} ")
                self.quit()

    def __select_deselect_piece(self, deselect, piece = None):
        if deselect:
            self.showPieceMoves(None)
            self.setHoveringPiece(None)
            self.setHighlightedSquares(*self.last_move)
            self.selected_piece = None
            self.deselect_flag = False
            return
        self.selected_piece = piece
        self.showPieceMoves(piece)
        self.setHoveringPiece(piece)
        self.setHighlightedSquares(piece.index, *self.last_move)
        
    def showPieceMoves(self, piece):
        if not piece:
            self.highlight_piece_moves.clear()
            return
        highlight = []
        for move in self.legal_moves:
            if move[0] == piece:
                highlight.append(move)
        self.highlight_piece_moves = highlight
        
    def setHighlightedSquares(self, *squares_to_highlight):
        self.highlighted_squares.clear()
        for square in squares_to_highlight:
            self.highlighted_squares.append(square)

    def setHoveringPiece(self, piece):
           self.hovering_piece = piece

    def animate_piece(self, start_piece=None, end_square=None):
        if not start_piece:
            self.animating = None
            return

        self.step = 0
        start_xy = (start_piece.index % self.board_length, start_piece.index // self.board_length)
        end_xy = (end_square % self.board_length, end_square // self.board_length)

        self.animating = self.board[start_xy[0] + start_xy[1] * self.board_length]
        self.start_pixel_x, self.start_pixel_y = ((start_xy[0] * self.scale + self.scale / 2) + self.padding,(start_xy[1] * self.scale + self.scale / 2) + self.padding)
        self.end_pixel_x, self.end_pixel_y = ((end_xy[0] * self.scale + self.scale / 2) + self.padding, (end_xy[1] * self.scale + self.scale / 2) + self.padding)

    def update(self):
        self.row_column_pos = {"c": (pygame.mouse.get_pos()[0] - self.padding) // self.scale, "r": (pygame.mouse.get_pos()[1] - self.padding) // self.scale}
        self.index_pos = (self.row_column_pos["c"] + self.row_column_pos["r"] * self.board_length)
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                pygame.quit()
                exit()

            # this horrible if/else wrapping is needed because i can't really use guard clauses as returning this function would skip a frame, might try to refactor it later.
            if ev.type == pygame.MOUSEBUTTONDOWN:
                if 0 <= self.row_column_pos["r"] <= self.board_length - 1 and 0 <= self.row_column_pos["c"] <= self.board_length - 1:
                    
                    if self.board[self.index_pos] != "--" and not self.selected_piece:
                        self.__select_deselect_piece(False, self.board[self.index_pos])
                        
                    elif self.selected_piece:
                        self.setHoveringPiece(self.selected_piece)
                        if self.selected_piece != self.board[self.index_pos]:
                            moveresult = self.move(self.selected_piece, self.index_pos)
                            if moveresult and self.board[self.index_pos] != "--":
                                self.__select_deselect_piece(False, self.board[self.index_pos])
                                self.deselect_flag = False
                            else:
                                self.__select_deselect_piece(True)
                        else:
                            self.deselect_flag = True
                    else:
                        self.setHighlightedSquares(*self.last_move)
                else:
                    self.__select_deselect_piece(True)
                            
            if ev.type == pygame.MOUSEBUTTONUP:
                if self.hovering_piece:
                    if 0 <= self.row_column_pos["r"] <= self.board_length - 1 and 0 <= self.row_column_pos["c"] <= self.board_length - 1:
                        if self.hovering_piece != self.board[self.index_pos]:
                            moveresult = self.move(self.hovering_piece, self.index_pos, False)
                            if not moveresult:
                                self.setHighlightedSquares(self.selected_piece, *self.last_move)
                                self.__select_deselect_piece(True)
                        else:
                            if self.deselect_flag:
                                self.__select_deselect_piece(True)
                self.setHoveringPiece(None)
        

        self.root_surf.fill(self.background_color)
        for row in range(self.board_length):
            for column in range(self.board_length):
                pygame.draw.rect(self.root_surf, self.regular_board_colors[(row + column) % 2], pygame.Rect((((row * self.scale) + self.padding), ((column * self.scale) + self.padding), self.scale,self.scale)))
                if self.highlighted_squares:
                    if column * self.board_length + row in self.highlighted_squares:
                        pygame.draw.rect(self.root_surf, self.highlight_board_colors[(row + column) % 2], pygame.Rect((((row * self.scale) + self.padding), (( column * self.scale) + self.padding), self.scale, self.scale)))
                
                if self.highlighted_attacking_squares and self.debug_mode:
                    if column * self.board_length + row in self.highlighted_attacking_squares:
                        pygame.draw.rect(self.root_surf, self.colors[(row + column) % 2], pygame.Rect((((row * self.scale) + self.padding), (( column * self.scale) + self.padding), self.scale, self.scale)))     
       
        for row in range(self.board_length):
            for column in range(self.board_length):
                piece = self.board[(row + column * self.board_length)]
                if piece == "--":
                    continue
                piece_to_add = f"{piece.team}{piece.type}"
                if piece in [self.hovering_piece, self.animating]:
                    continue
                self.root_surf.blit(self.sprites[piece_to_add], self.sprites[piece_to_add].get_rect( center=((row * self.scale + self.scale / 2) + self.padding, (column * self.scale + self.scale / 2) + self.padding)))  
      
        if self.highlight_piece_moves:
            for sqr in self.highlight_piece_moves:
                if self.board[sqr[1]] == "--":
                    self.root_surf.blit(self.sprites["circle"], self.sprites["circle"].get_rect(center=((sqr[1] % self.board_length * self.scale + self.scale / 2) + self.padding, ((sqr[1] // self.board_length * self.scale + self.scale / 2) + self.padding))))
                else:
                    self.root_surf.blit(self.sprites["bigcircle"], self.sprites["bigcircle"].get_rect(center=((sqr[1] % self.board_length * self.scale + self.scale / 2) + self.padding, ((sqr[1] // self.board_length * self.scale + self.scale / 2) + self.padding))))    
        
        if self.animating:
            self.step += self.animation_speed / self.refresh_rate_cap # adding 1 so you dont get a divide by 0 exception if you set no limit
            if self.step >= 1:
                self.root_surf.blit(self.sprites[f"{self.animating.team}{self.animating.type}"], self.sprites[f"{self.animating.team}{self.animating.type}"].get_rect(center=(self.end_pixel_x, self.end_pixel_y)))
                self.animate_piece(None)
                return
            self.root_surf.blit(self.sprites[f"{self.animating.team}{self.animating.type}"], self.sprites[f"{self.animating.team}{self.animating.type}"].get_rect(center=(self.__lerp(self.start_pixel_x, self.end_pixel_x, self.step),self.__lerp(self.start_pixel_y, self.end_pixel_y, self.step))))
        
        if self.hovering_piece:
           if 0 <= self.row_column_pos["r"] <= self.board_length - 1 and 0 <= self.row_column_pos["c"] <= self.board_length - 1:
               pygame.draw.rect(self.root_surf, self.spotlighted_square_color, pygame.Rect(self.row_column_pos["c"] * self.scale + self.padding, self.row_column_pos["r"] * self.scale + self.padding, self.scale, self.scale), self.padding // 4)
               
           self.root_surf.blit(self.sprites[f"{self.hovering_piece.team}{self.hovering_piece.type}"], self.sprites[f"{self.hovering_piece.team}{self.hovering_piece.type}"].get_rect(center=( self.__clamp(self.padding, self.scale*self.board_length+self.padding, pygame.mouse.get_pos()[0]), self.__clamp(self.padding, self.scale * self.board_length+self.padding, pygame.mouse.get_pos()[1]))))
         
               
    def getPieceMoves(self, piece, attacking_moves = False):
        if piece == "--" or not piece:
            return []
        moves = []
        if self.turn != piece.team and not attacking_moves:
            return moves
        
        def slidingPieceMoves(offsets): # Will optimize this later
            for offset in offsets:
                for i in range(1, self.board_length):
                    end_rank = piece.coordinates["rank"]
                    end_file = piece.coordinates["file"]
                    if offset == self.board_length:
                        end_rank += i
                    elif offset == -self.board_length:
                        end_rank -= i
                    elif offset == 1:
                        end_file += i
                    elif offset == -1:
                        end_file -= i
                    elif offset == -self.board_length + 1:
                        end_file -= i
                        end_rank -= i
                    elif offset == -self.board_length - 1:
                        end_file += i
                        end_rank -= i
                    elif offset ==  self.board_length + 1:
                        end_file += i
                        end_rank += i
                    elif offset == self.board_length - 1:
                        end_file -= i
                        end_rank += i
                    end_index = end_rank * self.board_length + end_file
                    if not (0 <= end_rank < self.board_length) or not (0 <= end_file < self.board_length):
                        break
                    end_piece = self.board[end_index]
                    if end_piece == "--":
                        moves.append((piece, end_index, 1))
                    elif end_piece.team != piece.team:
                        moves.append((piece, end_index, 1))
                        if not attacking_moves or end_piece.type != "k": 
                            break
                    else:
                        if attacking_moves:
                            moves.append((piece, end_index, 1))
                        break
            return
                    
        match piece.type:
            case "p":
                if piece.team == "w": # if white piece
                    if self.squares_to_border[piece.index]["up"] and self.board[piece.index - self.board_length] == '--' and not attacking_moves:
                        moves.append((piece, piece.index - self.board_length, 1))
                        if not piece.moved and self.board[piece.index - 2 * self.board_length] == '--':
                            moves.append((piece, piece.index - self.board_length * 2, 1)) 
                    
                    if self.squares_to_border[piece.index]["right"]:
                        if str(self.board[piece.index - (self.board_length - 1)])[0] == "b" or attacking_moves:
                            moves.append((piece, piece.index - (self.board_length - 1), 1))
                            
                    if self.squares_to_border[piece.index]["left"]:
                        if str(self.board[piece.index - (self.board_length + 1)])[0] == "b" or attacking_moves:
                            moves.append((piece, piece.index - (self.board_length + 1), 1))
                        
                elif piece.team == "b":
                    if self.squares_to_border[piece.index]["down"] and self.board[piece.index + self.board_length] == '--' and not attacking_moves: # if not on top rank and piece above pawn is empty
                        moves.append((piece, piece.index + self.board_length, 1)) # add move to move one rank up
                        if not piece.moved and self.board[piece.index + 2 * self.board_length] == '--': # if piece has not moved and two squares above it are empty
                            moves.append((piece, piece.index + self.board_length * 2, 1)) # add double pawn push
                            
                    if self.squares_to_border[piece.index]["right"]:
                        if str(self.board[piece.index + (self.board_length + 1)])[0] == 'w' or attacking_moves:
                            moves.append((piece, piece.index + self.board_length + 1, 1))
                            
                    if self.squares_to_border[piece.index]["left"] or attacking_moves:
                        if str(self.board[piece.index + (self.board_length - 1)])[0] == 'w' or attacking_moves:
                            moves.append((piece, piece.index + self.board_length - 1, 1))
                            
            case "n":
                for offset in self.offsets["n"]:
                    
                    index = piece.index
                    end_index = index + offset
                    rank, file = divmod(index, self.board_length)
                    end_row, end_file = divmod(end_index, self.board_length)
                    
                    if end_row < 0 or end_row > self.board_length - 1 or end_file < 0 or end_file > self.board_length - 1:
                        continue
                    if abs(end_file - file) in [1, 2] and abs(end_row - rank) in [1, 2]:
                        dest_piece = self.board[end_index]
                        if dest_piece == "--" or dest_piece.team != piece.team:
                            moves.append((piece, end_index, 1))
                        elif attacking_moves:
                            moves.append((piece, end_index, 1))
                            
            case "b":
                slidingPieceMoves(self.offsets["b"])
                
            case "r":
                slidingPieceMoves(self.offsets["r"])
                
            case "q": 
                slidingPieceMoves(self.offsets["q"])
                
            case "k":
                for offset in self.offsets["k"]:
                    index = piece.index
                    end_index = index + offset
                    rank, file = index // self.board_length, index % self.board_length
                    end_row, end_file = end_index // self.board_length, end_index % self.board_length
                    if end_row < 0 or end_row > self.board_length - 1 or end_file < 0 or end_file > self.board_length - 1:
                        continue
                    if abs(end_file - file) in [0, 1] and abs(end_row - rank) in [0, 1]:
                        dest_piece = self.board[end_index]
                        if dest_piece == "--" or dest_piece.team != piece.team:
                            moves.append((piece, end_index, 1))
                        elif attacking_moves:
                            moves.append((piece, end_index, 1))
                          
        return moves


    def updateLegalMoves(self):
        
        self.highlighted_attacking_squares.clear()
        
        def get_attack_directions(king_pos, attack_pos, attacking_piece_type):
            attack_directions = []
            
            
            row_diff = (attack_pos // 8) - (king_pos // 8)
            col_diff = (attack_pos % 8) - (king_pos % 8)
            if attacking_piece_type in ("n", "p"):
                return attacking_piece_type
            if attacking_piece_type in ('r', 'q'):
                if row_diff == 0:
                    attack_directions.append(1 if col_diff > 0 else -1)
                elif col_diff == 0:
                    attack_directions.append(8 if row_diff > 0 else -8)
            if attacking_piece_type in ('b', 'q'):
                if row_diff == col_diff:
                    attack_directions.append(9 if row_diff > 0 else -9)
                if row_diff == -col_diff:
                    attack_directions.append(7 if row_diff > 0 else -7)
            
            return attack_directions
        
        def get_squares_between(king_pos, attack_pos, attack_direction):
            between_squares = []
            curr_pos = king_pos
            while curr_pos != attack_pos:
                between_squares.append(curr_pos)
                curr_pos += attack_direction
            return between_squares
        
        self.legal_moves.clear()
        self.in_check = False
        
        attacking_piece = None
        enemy_attacking_squares_and_pieces = {}
        for piece in self.board:
            if piece == '--' or piece.team == self.turn:
                continue
            buffer = []
            for move in self.getPieceMoves(piece, True):
                buffer.append(move[1])
            enemy_attacking_squares_and_pieces[piece] = buffer

        only_attacking_squares = []

        for v in enemy_attacking_squares_and_pieces.values():
            only_attacking_squares.extend(v)

        buffer = []
        for piece in self.board:
            
            if piece == '--':
                continue
                

            if piece.type == "k" and piece.team == self.turn:
                
                king_pos = piece.index
                
                for move in self.getPieceMoves(piece):
                        if move[1] not in only_attacking_squares:
                            self.legal_moves.append(move)

                attacking_pieces = []
                for k, v in enemy_attacking_squares_and_pieces.items():
                    if piece.index in v:
                        attacking_pieces.append(k)
                        self.in_check = True
                        self.__log(f"'{piece}' at {piece.index} in check by -> '{k}' at {k.index}")
                        
                        
                        
                for attacking_piece in attacking_pieces:
                    attack_pos = attacking_piece.index
                    attack_directions = get_attack_directions(king_pos, attack_pos, attacking_piece.type)
                    if attack_directions in ["p","n"]:
                        between_squares = [king_pos, attacking_piece.index]
                        self.highlighted_attacking_squares.extend(between_squares)
                    else:
                        for attack_direction in attack_directions:
                            between_squares = get_squares_between(king_pos, attack_pos, attack_direction)
                            for pos in between_squares:
                                if self.board[pos] != '--':
                                    break
                            self.highlighted_attacking_squares.extend(list(between_squares) + [attack_pos])

                if not attacking_pieces:
                    self.highlighted_attacking_squares = [] 

        for piece in self.board:
            if piece == "--":
                continue
            
            if piece.type == "k":
                continue
            if piece.team != self.turn:
                continue

            
            piece_moves = self.getPieceMoves(piece)
            for move in piece_moves:
                
                if self.in_check:
                    if move[1] in list(between_squares) + [attack_pos] and len(attacking_pieces) == 1:
                        self.legal_moves.append(move)
                    continue
                else:
                    self.legal_moves.append(move)
            
        if self.in_check and not self.legal_moves:
            self.__log(f"Checkmate!", end='')
            if self.turn == "W":
                self.__log(f" Black wins.")
            else:
                self.__log(f" White wins.")
            
        if not self.in_check and not self.legal_moves:
            self.__log("Stalemate!")         
         
    def move(self, start_piece, end_square, animate_piece=True):
        for move in self.legal_moves:
            if (start_piece, end_square) == (move[0], move[1]):
                movetype = move[2]
                break
        else:
            return 1

        move_made = "move"
        self.animate_piece(None)
            
        # NOT DONE
        match movetype:
            # regular move
            case 1:
                if not start_piece.moved:
                    start_piece.moved = True
                self.last_move = [start_piece.index, end_square]
                if animate_piece:
                    self.animate_piece(start_piece, end_square)
                if self.board[end_square] == "--":
                    self.__log(f"'{start_piece}' at [{start_piece.index}] moved -> [{end_square}]")
                    move_made = "move"
                elif not self.board[end_square] == "--":
                    self.__log(f"'{start_piece}' at [{start_piece.index}] captured -> '{self.board[end_square]}' at [{end_square}]'")
                    move_made = "capture"
                self.board[end_square] = self.board[start_piece.index]
                self.board[start_piece.index] = "--"
                start_piece.updatePosition(self.board.index(start_piece), {"rank": end_square // self.board_length, "file": end_square % self.board_length})
            # en passant
            case 2:
                pass
            # castling
            case 3:
                pass
            # promotion
            case 4:
                pass
        
        
        self.turn = {"w":"b","b":"w"}[self.turn]
        self.updateLegalMoves()
        
        if self.in_check:
            self.sounds["check"].play()
        else:
            self.sounds[move_made].play()
      
    def loadGame(self, FEN_string): 
        self.__loadAssets()
        self.__log("Loading game...", end='')
        for r in range(self.board_length):
            for f in range(self.board_length):
                square = r * self.board_length + f
                down = self.board_length - 1 - r
                up = r
                right = self.board_length - 1 - f
                left = f
                self.squares_to_border[square] = {"up":up, "down":down, "left":left, "right":right} 
        def invalid_FEN(error_message):
                raise ValueError(f"Invalid FEN string inputted [{error_message}]")
              
        try:
            rank = 0
            file = 0
            index_position = 0
            self.board.clear()
            self.board = ["--" for _ in range(self.board_length ** 2)]
            sections = FEN_string.split(" ")

            for char in sections[0]:
                index_position = (file + rank * self.board_length)
                if char == "/":
                    file = 0
                    rank += 1
                    continue
                if char.isupper():
                    self.board[index_position] = self.piece_id_to_class[char.lower()]("w", index_position, {"rank": rank, "file":file})
                    file += 1
                elif char.islower() and char != "/":
                    self.board[index_position] = self.piece_id_to_class[char]("b", index_position, {"rank": rank, "file":file})
                    file += 1
                elif char.isdigit():
                    file += int(char)
            self.turn = sections[1]

            self.updateLegalMoves()
            self.__log("Done!")
            
        except Exception as e:
            self.__log(f"Error!\n{e} ")
            self.board = ["--" for _ in range(self.board_length ** 2)]

"""
Test loop

main = new(scale=80, hide_console_messages=False)
while True:
    main.update()
    pygame.display.flip()
    clock.tick(main.refresh_rate_cap)
"""