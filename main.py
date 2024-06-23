import pygame

from board import Board
from fontcontroller import FontController

black = (0,0,0)

difficulties = {'easy': 50, 'medium': 250, 'hard': 500}

def main(winx=800, winy=600):
	global difficulties

	pygame.display.init()

	screen = pygame.display.set_mode((winx, winy))
	clock = pygame.time.Clock()

	font_controller = FontController()

	board = Board(winx, winy, font_controller)
	board.setup(difficulties['easy'])
	print(board.get_num_mines(), 'mines')

	done = False

	while not done:
		clock.tick(15)
		events = pygame.event.get()

		for e in events:
			if e.type == pygame.MOUSEBUTTONDOWN:
				mx,my = e.pos[0],e.pos[1]
				xcell = board.get_cell_from_pos(int(mx),int(my))

				res = board.update(xcell, e.button == 3)
				if res: # hit a mine
					board.reveal_mines()
					print("You died!")

				if board.check_win_condition():
					print("Winner!")

			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_ESCAPE:
					done = True
					break

		screen.fill(black)
		board.render(screen)
		pygame.display.flip()

	pygame.display.quit()

if __name__ == "__main__":
	main()
