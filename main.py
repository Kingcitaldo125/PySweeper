import pygame

from board import Board
from fontcontroller import FontController
from rendertext import RenderText
from timer import Timer

red = (255,0,0)
black = (0,0,0)

difficulties = {'easy': 50, 'medium': 150, 'hard': 300}
font_controller = FontController()
timer = Timer(1)


def reset(difficulty, xoffset, yoffset, winx, winy):
	global font_controller, timer

	board = Board(winx, winy, xoffset, yoffset, font_controller)
	board.setup(difficulty)
	print(board.get_num_mines(), 'mines')

	timer.reset()

	return board

def render(screen, board, timer, winx):
	global black, red

	screen.fill(black)
	board.render(screen)

	# Render the time
	rendertext = RenderText(font_controller, red, black)
	rendertext.update_x(winx-10)
	rendertext.update_y(10)
	rendertext.update_text(str(timer.get_time()))
	rendertext.draw(screen)

	pygame.display.flip()

def main(winx=400, winy=400):
	global difficulties, timer

	diff_setting = 0
	diff_cond = lambda x: x < 1 or x > 3
	while diff_cond(diff_setting):
		diff_setting = int(input("Choose a difficulty: (easy: 1, medium: 2, hard: 3)\n"))
		if diff_cond(diff_setting):
			print(f"Not a difficulty: {diff_setting}")

	pygame.display.init()

	screen = pygame.display.set_mode((winx, winy))
	clock = pygame.time.Clock()

	diff = difficulties['easy']
	if diff_setting == 1:
		print("Easy difficulty")
	elif diff_setting == 2:
		diff = difficulties['medium']
		print("Medium difficulty")
	elif diff_setting == 3:
		diff = difficulties['hard']
		print("Hard difficulty")

	board = reset(diff, 0, winy//10, winx, winy)
	done = False

	timer.start()

	while not done:
		clock.tick(15)
		events = pygame.event.get()

		for e in events:
			if e.type == pygame.QUIT:
				done = True
				break

			if e.type == pygame.MOUSEBUTTONDOWN:
				mx,my = e.pos[0],e.pos[1]
				xcell = board.get_cell_from_pos(int(mx),int(my))

				res = board.update(xcell, e.button == 3)
				if res: # hit a mine
					board.reveal_mines(False)
					print("You died!")
					timer.stop()

				if board.check_win_condition():
					print("Winner!")
					render(screen, board, timer, winx)
					timer.stop()

			if e.type == pygame.KEYDOWN:
				if e.key == pygame.K_RETURN:
					timer.stop()
					board = reset(diff, 0, winy//10, winx, winy)
					timer.start()
				if e.key == pygame.K_ESCAPE:
					done = True
					break

		render(screen, board, timer, winx)

	timer.stop()
	pygame.display.quit()

if __name__ == "__main__":
	main()
