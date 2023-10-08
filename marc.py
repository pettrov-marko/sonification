import cv2
import numpy as np
from audiolazy import str2midi, midi2str
from midiutil import MIDIFile
import random
import math

def Sonifier(filename):
	video_capture = cv2.VideoCapture(filename)

	print(filename)

	if not video_capture.isOpened():
		print("Error: Could not open video file.")
		exit()
		
	note_names = ['C1','C2','G2','C3','E3','G3','A3','B3','D4','E4','G4','A4','B4','D5','E5','G5','A5','B5','D6','E6','F#6','G6','A6']

	note_midis = [str2midi(n) for n in note_names]
	fpsa = 1
	fpsacomp = int(30 / fpsa) # 30 e fps-ot na videoto
	bpm = 60*fpsa
	duration_beats = 1
	duration_sec = duration_beats * 60 / bpm
	midi = MIDIFile(1)
	midi.addTempo(track = 0, time = 0, tempo = bpm)
	# Define an audio output file
	output_audio = []
	vol = []
	texture = []

	minvol = 70 #Change accordingly (VOLUME FOR DARK SCREEN)
	maxvol = 0

	color_min = -1
	color_max = 0
	max_texture = 0
	min_texture = 1000000007
	for odi in range(0,10000):
		ret, frame = video_capture.read()
		if not ret:
			break  # Break the loop when all frames are processed or audio duration is reached

		if odi % fpsacomp != 0:
			continue

		# Convert the frame to grayscale and resize if necessary
		frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
		frame_gray = cv2.resize(frame_gray, (256, 256))  # Adjust the size as needed
		# Compute luminance (brightness) of the frame
		luminance = frame_gray.astype(float)
		# Perform FFT on the luminance frame
		fft_luminance = np.fft.fft(luminance)
		fft_magnitude_luminance = np.abs(fft_luminance)
		# Perform additional FFT analysis on edges/patterns/lines (you can customize this part)
		# For example, you can use the Canny edge detection algorithm
		edges = cv2.Canny(frame_gray, 50, 150)  # Adjust parameters as needed
		fft_edges = np.fft.fft(edges)
		fft_magnitude_edges = np.abs(fft_edges)
		# Normalize the audio signals
		max_value_luminance = np.max(fft_magnitude_luminance)
		if max_value_luminance != 0:
			fft_magnitude_luminance /= max_value_luminance

		max_value_edges = np.max(fft_magnitude_edges)
		if max_value_edges != 0:
			fft_magnitude_edges /= max_value_edges

		# Extract mean color from the frame (as a single value)
		mean_color = np.mean(frame)


			
		vol.append(frame_gray.sum())
		if maxvol < vol[-1]:
			maxvol = vol[-1]

		if color_min > mean_color or color_min == -1:
			color_min = mean_color

		if color_max < mean_color:
			color_max = mean_color
			
		output_audio.append(mean_color)
			
		texture.append(fft_magnitude_edges.sum())
		max_texture = max(max_texture, texture[-1])
		min_texture = min(min_texture, texture[-1])

	oldvv = -1
	oldpp = -1

	for i in range(0, len(vol)):
		vv = int((127 - minvol)/maxvol * vol[i] + minvol)
		pp = int(22 / (color_max - color_min) * (output_audio[i] - color_min))
		tt = int(22 / (max_texture - min_texture) * (texture[i] - min_texture))
		if (vv != oldvv and oldpp != pp) or i == len(vol) - 1:
			midi.addNote(track = 0, channel = 0, time = duration_beats*i, pitch = note_midis[int(math.sqrt(pp * tt))], volume = vv , duration = 4)

		oldvv = vv
		oldpp = pp

		
	with open("download/izlez.mid", "wb") as f:
		midi.writeFile(f)

	return "izlez.mid"
