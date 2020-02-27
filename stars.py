#-*- coding: utf-8 -*-
'''Control keys:
	'Q' or ESC: 	Close window and exit
	'Enter':		Switch to Full screen mode
	'R'    :		Start/Stop Record every 4th frame to the video file
'''

import cv2
import numpy as np
from math import sin, sqrt, pi

DEBUG = False

class Star:
	def __genstar01__(self, R):
		self.fi = 2*pi*np.random.random()
		r = R * np.random.random()
		self.x = r * sin(self.fi)
		self.y = r * sin(self.fi + pi/2)
	def __genstar02__(self, W, H):
		maxx = 3*W // 4
		maxy = 3*H // 4
		randx = (np.random.randint(maxx) + np.random.randint(maxx)) >> 1
		randy = (np.random.randint(maxy) + np.random.randint(maxy)) >> 1
		self.y  = float(H // 8 + randy)
		self.y -= H//2
		self.x  = float(W // 8 + randx)
		self.x -= W//2
		self.fi = -np.arctan2(self.y, self.x) + pi/2
	def __init__(self, W, H):
		# self.__genstar01__(2*min(w, h)/5)
		self.__genstar02__(W, H)
		self.xi = pi*np.random.random()/3 + pi/6	# pi/3 == 2*pi/6 == pi/2 - pi/6; pi/3 + pi/6 == 3*pi/6 == pi/2
		self.speed = (np.random.random() + 0.25) / 5
		colsh = 2*np.random.random()/3
		R = min(255, max(128, int(300*sin(pi*colsh))))
		G = min(255, max(128, int(300*sin(pi*(colsh + 1/3)))))
		B = min(255, max(128, int(300*sin(pi*(colsh - 1/3)))))
		self.color =  (B, G, R)
		self.color2 = (2*B//3, 2*G//3, 2*R//3)
		self.color3 = (B >> 2, G >> 2, R >> 2)
	def Move(self):
		self.x += sin(self.xi) * self.speed * sin(self.fi)
		self.y += sin(self.xi) * self.speed * sin(self.fi + pi/2)
		self.speed += self.speed / 350

class Screen:
	Caption 		= "Through the Universe"
	videofilename	= 'Stars.avi'
	videocodec 		= 'MJPG'
	FPS      		= 30
	frames			= 0
	width  			= 960
	height 			= 540
	totalstars	 	= 350
	FullScreen   	= 0
	CaptureVideo 	= False
	def __init__(self):
		self.screen = np.zeros((self.height, self.width, 3), dtype="uint8")
		self.stars = []
		self.fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
		for i in range(self.totalstars):
			self.stars.append(Star(self.width, self.height))
	def Move(self):
		for i in range(len(self.stars)):
			self.stars[i].Move()
			x = self.stars[i].x + self.width/2
			y = self.stars[i].y + self.height/2
			if 	((x > self.width-1) or (y > self.height-1) or (x < 1) or (y < 1)):
				self.stars[i] = Star(self.width, self.height)
	def DrawStars(self):
		self.screen = np.zeros((self.height, self.width, 3), dtype="uint8")
		for star in self.stars:
			x = int(star.x + self.width/2)
			y = int(star.y + self.height/2)
			if star.speed < 0.15:
				self.screen[y,x] = star.color3
			elif star.speed < 0.25:
				self.screen[y,x] = star.color2
			elif star.speed < 0.5:
				self.screen[y,x] = star.color
			elif star.speed > 0.75:
				self.screen[y-1,x-1:x+2] = [star.color3, star.color2, star.color3]
				self.screen[y,  x-1:x+2] = [star.color2, star.color, star.color2]
				self.screen[y+1,x-1:x+2] = [star.color3, star.color2, star.color3]
			elif star.speed > 0.5:
				self.screen[y-1,x] = star.color3
				self.screen[y,x-1:x+2] = [star.color3, star.color, star.color3]
				self.screen[y+1,x] = star.color3
	def SwitchToFullScreen(self):
		# self.FullScreen = (self.FullScreen + 1) % 3
		self.FullScreen = (self.FullScreen + 1) % 2
	def StartStopRecord(self):
		self.CaptureVideo = not self.CaptureVideo
		if self.CaptureVideo:
			if DEBUG: print("+++ Start Record video to file:", self.videofilename)
			self.video = cv2.VideoWriter(self.videofilename, self.fourcc, float(self.FPS), (self.width, self.height))
		else:
			if DEBUG: print("+++ Stop Record video")
			self.video.release()
	def Show(self):
		self.DrawStars()
		if self.FullScreen == 0:		# original window size
			cv2.namedWindow(self.Caption, cv2.WINDOW_NORMAL)
			cv2.setWindowProperty(self.Caption,cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
			cv2.resizeWindow(self.Caption, self.width, self.height)	
		#~ elif self.FullScreen == 1:		# double window size
			#~ cv2.namedWindow(self.Caption, cv2.WINDOW_NORMAL)
			#~ cv2.setWindowProperty(self.Caption,cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_NORMAL)
			#~ cv2.resizeWindow(self.Caption, 2*self.width, 2*self.height)	# original scale # double scale
		else:							# fillscreen
			cv2.namedWindow(self.Caption, cv2.WINDOW_NORMAL)
			cv2.setWindowProperty(self.Caption,cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)						
		cv2.imshow(self.Caption, self.screen)
		if self.CaptureVideo: # Record each 4th frame
			self.frames += 1
			if self.frames & 3 == 0:
				self.video.write(self.screen)
			


screen = Screen()
while True:
	screen.Move()
	screen.Show()
	key = cv2.waitKey(1) & 0xFF
	if  key | 0x20 == ord('q') or key == 27: 	# 'q' or 'Q ' or 'ESC'
		break
	if  key | 0x20 == ord('r'): 				# 'r' -> RecordVideo
		screen.StartStopRecord()
	elif key == 13:								# Enter key
		screen.SwitchToFullScreen()
cv2.destroyAllWindows()	

