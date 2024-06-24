from random import randrange as rrange

import pygame

from rendertext import RenderText


class Cell:
	def __init__(self, x, y, x_idx, y_idx, size, font_controller):
		self.x = x
		self.y = y
		self.x_idx = x_idx
		self.y_idx = y_idx
		self.size = size
		self.half_size = size // 2
		self.occupied = False
		self.marked = False
		self.clicked = False
		self.hit_mine = False
		self.display_count = False
		self.neighbor_mine_count = 0
		self.unclicked_color = (76,84,92) # grey
		self.clicked_color = (56,64,72) # dark grey
		self.black = (0,0,0)
		self.red = (255,0,0)
		self.white = (255,255,255)
		self.font_controller = font_controller
		self.flag_image = pygame.image.load('flag.png').convert_alpha()
		self.flag_image = pygame.transform.scale(self.flag_image, (15,15))

	def __str__(self):
		return str(self.x) + "," + str(self.y)

	def gen_mine(self, difficulty):
		x = rrange(1, 1000)
		if x <= difficulty:
			self.occupied = True

	def is_occupied(self):
		return self.occupied

	def click(self, reveal=False):
		self.clicked = True
		self.marked = False

		if self.occupied and not reveal:
			self.hit_mine = True
		elif self.occupied and reveal:
			self.clicked = False
			self.mark()

	def mark(self):
		self.marked = True

	def unmark(self):
		self.marked = False

	def update_neighbor_mine_count(self, newcount):
		self.neighbor_mine_count = newcount

	def display_mine_count(self):
		self.click()
		self.display_count = True

	def render(self, screen):
		col_sel = self.clicked_color if self.clicked else self.unclicked_color

		if self.hit_mine:
			col_sel = self.red

		pygame.draw.rect(screen, col_sel, (self.x, self.y, self.size, self.size))
		pygame.draw.rect(screen, self.white, (self.x, self.y, self.size+1, self.size+1),1)

		if self.hit_mine:
			return

		if self.display_count:
			rendertext = RenderText(self.font_controller, self.white, self.clicked_color)
			rendertext.update_x(self.x + self.half_size)
			rendertext.update_y(self.y + self.half_size)
			rendertext.update_text(str(self.neighbor_mine_count))
			rendertext.draw(screen)

		if self.marked:
			screen.blit(self.flag_image, (self.x + 2, self.y + 2))

class Board:
	def __init__(self, winx, winy, xoffset, yoffset, font_controller):
		self.winx = winx
		self.winy = winy
		self.xoffset = xoffset
		self.yoffset = yoffset
		self.cells = []
		self.marked_cells = set([])
		self.cell_size = 20
		self.font_controller = font_controller
		self.mine_count = 0
		self.red = (255,0,0)
		self.black = (0,0,0)

	def setup(self, difficulty):
		row_cells = (self.winy - self.xoffset) // self.cell_size
		col_cells = (self.winy - self.yoffset) // self.cell_size

		xpos = self.xoffset
		ypos = self.yoffset
		for y in range(0, col_cells):
			cell_row = []
			xpos = 0
			for x in range(0, row_cells):
				xc = Cell(xpos, ypos, x, y, self.cell_size, self.font_controller)
				xc.gen_mine(difficulty)
				cell_row.append(xc)
				xpos += self.cell_size

			self.cells.append(cell_row)
			ypos += self.cell_size

		self.mine_count = self.get_num_mines()

	def reveal_mines(self, reveal_tiles):
		for row in self.cells:
			for cell in row:
				cell.click(reveal_tiles)

	def get_num_mines(self):
		count = 0

		for row in self.cells:
			for cell in row:
				if cell.is_occupied():
					count += 1

		return count

	def mark_cell(self, cell):
		# Don't mark a cell when we know its identity
		if cell.clicked or cell.marked:
			return

		cell.mark()

		if cell.is_occupied():
			self.mine_count -= 1

		self.marked_cells.add(cell)

	def check_win_condition(self):
		for row in self.cells:
			for cell in row:
				if not cell.is_occupied():
					continue
				if cell not in self.marked_cells:
					return False

		self.reveal_mines(True)
		return True

	def get_cell_from_pos(self, posx, posy):
		x = (posx - self.xoffset) // self.cell_size
		y = (posy - self.yoffset) // self.cell_size

		return self.cells[y][x]

	def get_cell_neighbors(self, cell):
		neighbors = []
		row_size = len(self.cells)
		col_size = len(self.cells[0])

		cellx = cell.x_idx
		celly = cell.y_idx

		for y in range(celly - 1, celly + 2, 1):
			for x in range(cellx - 1, cellx + 2, 1):
				if x < 0 or x >= col_size or y < 0 or y >= row_size:
					continue
				if x == cellx and y == celly:
					continue

				neighbors.append(self.cells[y][x])

		return neighbors

	def update_help(self, visited, cell):
		visited.add(cell)

		# Hit a mine
		if cell.is_occupied():
			return True

		cell.click()

		neighbor_mine_count = 0
		neighbors = self.get_cell_neighbors(cell)
		nset = set([])
		#print("neighbors",neighbors)
		for n in neighbors:
			if n in visited:
				continue

			if n.is_occupied():
				neighbor_mine_count += 1
				nset.add(n)
				continue

			n.click()

		cell.update_neighbor_mine_count(neighbor_mine_count)

		for n in neighbors:
			if n in visited or n in nset:
				continue

			l_neighbor_count = 0
			xneighbors = self.get_cell_neighbors(n)
			for x in xneighbors:
				if x.is_occupied():
					l_neighbor_count += 1
					nset.add(n)

			n.update_neighbor_mine_count(l_neighbor_count)
			if l_neighbor_count > 0:
				n.display_mine_count()

		if neighbor_mine_count > 0:
			cell.display_mine_count()
			#return False

		for n in neighbors:
			if n in visited or n in nset or n.is_occupied():
				continue

			res = self.update_help(visited, n)
			if res:
				return res

		return False

	def update(self, clicked_cell, mark):
		if mark:
			self.mark_cell(clicked_cell)
			return

		# Don't re-click an already clicked cell
		if clicked_cell.clicked:
			return

		visited = set([])
		return self.update_help(visited, clicked_cell)

	def display_mines_left(self, screen):
		rendertext = RenderText(self.font_controller, self.red, self.black)
		rendertext.update_x(10)
		rendertext.update_y(10)
		rendertext.update_text(str(self.mine_count))
		rendertext.draw(screen)

	def render(self, screen):
		self.display_mines_left(screen)

		for row in self.cells:
			for cell in row:
				cell.render(screen)
