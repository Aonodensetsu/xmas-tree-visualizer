# fix for running via left click
import os
os.chdir(os.path.dirname(os.path.realpath(__file__)))

# import required libraries
import tkinter
import matplotlib as mpl
mpl.use('TkAgg', force=True)
import matplotlib.pyplot as plot

# import effect file
import tree_effect
# create shared variables
x_values = []
y_values = []
z_values = []


# create visualizer
def gui():
	if not draw_gui:
		return
	# measure screen size and dpi
	screen_measurer = tkinter.Tk()
	dpi = screen_measurer.winfo_fpixels('1i')
	screen_height = screen_measurer.winfo_screenheight()
	# compute a sensible size for the visualizer
	top = int(0.05 * screen_height)
	height = int(0.8 * screen_height)
	left = 100
	width = int(0.9 * height)
	screen_measurer.update()
	screen_measurer.destroy()
	# create window
	mpl.rcParams['toolbar'] = 'None'
	window = plot.figure(num='Christmas Tree Visualiser')
	# move and resize window
	window.canvas.manager.window.wm_geometry(f'+{left}+{top}')
	window.set_size_inches(width / dpi, height / dpi)
	# listen to closing
	window.canvas.mpl_connect('close_event', lambda e: plot.close(window))
	# create 3d plot
	graph = window.add_subplot(111, projection='3d')
	# set preferences (labels)
	graph.view_init(elev=15, azim=5)
	graph.set_xlabel('X')
	graph.set_xlim3d(-1, 1)
	graph.set_xticks([-1, 1])
	graph.set_ylabel('Y')
	graph.set_ylim3d(-1, 1)
	graph.set_yticks([-1, 1])
	graph.set_zlabel('Z')
	graph.set_zlim3d(0, max(z_values))
	graph.set_zticks([0, max(z_values)])
	# plot wires connecting leds
	graph.plot(x_values, y_values, z_values, color=(0, 0, 0, 0.07))
	# set correct aspect ratio
	graph.set_box_aspect([ub - lb for lb, ub in (getattr(graph, f'get_{a}lim')() for a in 'xyz')])
	plot.tight_layout()
	return graph


# update plot
def draw(graph, colors):
	# if the window was closed, don't draw
	# will still create the csv if this happens
	if not plot.fignum_exists(1):
		return
	# clear the previous frame
	for dot in plot.gca().collections:
		dot.remove()
	# plot current values
	graph.scatter3D(x_values, y_values, z_values, c=colors, cmap='rgb')
	plot.draw()
	# limit to 30 fps
	plot.pause(1/30)


# internally uses normalized rgb, write 0-255 to csv
def denormalize_rgb(rgb):
	for i, v in enumerate(rgb):
		for j, w in enumerate(v):
			rgb[i][j] = round(255*w)
	return rgb


def main():
	# read GIFT coordinates
	global x_values
	global y_values
	global z_values
	with open('coordinates.csv', mode='r', encoding='utf-8-sig') as csv_f:
		lines = csv_f.readlines()
		for i in range(len(lines)):
			line = lines[i].split(',')
			x_values.append(float(line[0]))
			y_values.append(float(line[1]))
			z_values.append(float(line[2]))
	# concatenate coordinates to send to effect
	positions = [{'x': x_values[i], 'y': y_values[i], 'z': z_values[i]} for i, v in enumerate(x_values)]

	# create the csv with the header string
	# the string if very long, so construct it programmatically
	with open('tree_effect.csv', mode='w') as effect_file:
		string = 'FRAME_ID'
		for i in range(500):
			for j in range(3):
				color = 'R' if j % 3 == 0 else 'G' if j % 3 == 1 else 'B'
				string += f',{color}_{i}'
		effect_file.write(f'{string}\n')
	# initialize the gui
	graph_r = gui()
	# get frames
	frame = 1
	frame_max = tree_effect.frame_max()
	# initialize empty storage
	storage = None
	# start playback and create effect csv
	# if interrupted will not corrupt csv and will produce a valid file
	# albeit cut in the middle (it updates the file once per frame)
	with open('tree_effect.csv', mode='a') as effect_file:
		while frame <= frame_max:
			storage, colors = tree_effect.effect(storage, positions, frame)
			draw(graph_r, colors)
			# create csv string for each frame
			string = f'{frame-1}'
			for led in denormalize_rgb(colors):
				for rgb in led:
					string += f',{rgb}'
			effect_file.write(f'{string}\n')
			frame += 1
	# notify that the csv is complete
	# continue visualizing until the visualizer is closed
	graph_r.text(0, 0, max(z_values) + 0.5, s='created csv', ha='center', size=16)
	while plot.fignum_exists(1):
		if not frame <= frame_max:
			frame = 1
		storage, colors = tree_effect.effect(storage, positions, frame)
		draw(graph_r, colors)
		frame += 1


if __name__ == '__main__':
	draw_gui = 1
	main()
