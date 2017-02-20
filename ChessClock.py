import sys
import os
from Tkinter import *
import math
import threading 


#_Getch is credited to Danny Yoo, who posted a general solution 
# to ActiveState on Friday, June 21, 2002 http://code.activestate.com/recipes/134892/
class _Getch:
    """Gets a single character from standard input.  Does not echo to the
screen."""
    def __init__(self):
        try:
            self.impl = _GetchWindows()
        except ImportError:
            self.impl = _GetchUnix()

    def __call__(self): return self.impl()


class _GetchUnix:
    def __init__(self):
        import tty, sys

    def __call__(self):
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch


class _GetchWindows:
    def __init__(self):
        import msvcrt

    def __call__(self):
        import msvcrt
        return msvcrt.getch()


'''
PlayerHeader Class: a class to represent player information, and to 
	interface on setup. 
'''
class PlayerHeader:
	Font              = 'Garamond'
	PrimaryFontSize   = 50
	SecondaryFontSize = 20
	NonErrorColor     = 'DeepSkyBlue3'
	ErrorColor        = 'firebrick2'

	WelcomeMessage             = "Welcome to ChessClock with Python \nTkinter! Please Enter Player's name in the box \n below and tap Enter."
	LenZeroErrorMessage        = "Sorry, name must be at least 1  \n character long. Please try again."
	OverLenErrorMessage        = "Sorry, name must be less than 30\n characters long. Please try again."
	GoodNameMessage            = "Great! Now enter Time in \n the format (minutes:seconds)."
	BadFormatMessage           = "Sorry, you must enter Time in the\n format (minutes:seconds). Please try again."
	BadMinuteFormatMessage     = "Sorry, you must enter a number for\n minutes. Please try again."
	BadSecondFormatMessage     = "Sorry, you must enter a number for\n seconds. Please try again."
	BadMinuteRangeMessage      = "Sorry, you must enter a positive \n value for minutes. Please try again."
	BadSecondRangeMessage      = "Sorry, you must enter a value between\n 0 and 59 for seconds. Please try again."


	def __init__(self, parent, player):
		self.Player = player
		if player == 'white':
			self.Opposite = 'black'
		else:
			self.Opposite = 'white'

		self.NameDisplay = Label(parent, font = (PlayerHeader.Font, PlayerHeader.PrimaryFontSize, 'bold'), 
			fg = self.Opposite, bg = self.Player)
		self.NameDisplay.pack(fill=BOTH, expand=1)

		self.ClockDisplay = Label(parent, font = (PlayerHeader.Font, PlayerHeader.PrimaryFontSize, 'bold'),
			fg = self.Opposite, bg = self.Player)
		self.ClockDisplay.pack(fill=BOTH, expand=1)

		self.MessageDisplay = Label(parent, font = (PlayerHeader.Font, PlayerHeader.SecondaryFontSize, 'bold'),
			fg = PlayerHeader.NonErrorColor, bg = self.Player)
		self.MessageDisplay.config(text = PlayerHeader.WelcomeMessage)
		self.MessageDisplay.pack(fill=BOTH,expand=1)

	def SetMessage(self, message):
		self.MessageDisplay.config(text = message)

	def SetMessageColor(self, color):
		self.MessageDisplay.config(fg = color)

	def SetName(self, name):
		self.NameDisplay.config(text = name) 

	def TimeStamp(self, microseconds):
		secs, microsecs = divmod(microseconds, 1000000)
		mins, secs = divmod(secs, 60)
		timeformat = "{:01d}:{:02d}:{:06d}".format(mins, secs, microsecs)
		return timeformat

	def SetClock(self, timestamp):
		self.ClockDisplay.config(text = timestamp)

    
'''
AnalogueClock class: a window displaying a traditional analogue clock, 
in addition to a digital clock at the top of the window with microsecond
resolution. This represents one half of the total chess clock.  
'''
class AnalogueClock:
	ClockRadius = 300
	Offset = 10
	CircleStart = Offset
	CircleEnd = 600 + Offset
	ClockWidth = 5

	FiveSec_IR = 250
	FiveSec_OR = 300
	FiveSec_Arc = 360/12
	FiveSec_Width = 5

	OneSec_IR = 280
	OneSec_OR = 300
	OneSec_Arc = 360/60
	OneSec_Width = 3

	MilliSec_IR = 280
	MilliSec_OR = 300
	MilliSec_Arc = 360/600
	MilliSec_Width = 1

	CanvasWidth = 600 + Offset*2
	CanvasHeight = 600 + Offset*2

	def __init__(self, parent, player):
		if player == 'white':
			self.Opposite = 'black'
		else:
			self.Opposite = 'white'
		self.Player = player
		self.CanvasBox = Canvas(parent, width = AnalogueClock.CanvasWidth, height = AnalogueClock.CanvasHeight)
		self.CanvasBox.pack()

		self.MinuteHand = self.CanvasBox.create_line(AnalogueClock.ClockRadius + AnalogueClock.Offset, AnalogueClock.ClockRadius + AnalogueClock.Offset, 0,0, fill = 'red', width = 5)
		self.MinuteAngle = 0
		self.SecondHand = self.CanvasBox.create_line(AnalogueClock.ClockRadius + AnalogueClock.Offset, AnalogueClock.ClockRadius + AnalogueClock.Offset, 0, 0, fill = 'red', width = 5)
		self.SecondAngle = 0


	#Draw the circular border 
	def DrawClock(self):
		self.CanvasBox.create_oval(AnalogueClock.CircleStart, AnalogueClock.CircleStart,
			                       AnalogueClock.CircleEnd, AnalogueClock.CircleEnd,
			                       fill = self.Player, outline = self.Opposite, width = AnalogueClock.ClockWidth)

	#Draw ticks around the edges 
	def DrawTicks(self):
		for i in range(600):
			if (i%50) != 0:
				tickAngle   = i * AnalogueClock.OneSec_Arc
				innerRadius = AnalogueClock.OneSec_IR
				outerRadius = AnalogueClock.OneSec_OR
				width       = AnalogueClock.OneSec_Width
			elif (i%10) != 0:
				tickAngle   = i * AnalogueClock.MilliSec_Arc
				innerRadius = AnalogueClock.MilliSec_IR
				outerRadius = AnalogueClock.MilliSec_OR
				width       = AnalogueClock.MilliSec_Width
			else: 
				tickAngle   = i * AnalogueClock.FiveSec_Arc
				innerRadius = AnalogueClock.FiveSec_IR
				outerRadius = AnalogueClock.FiveSec_OR
				width       = AnalogueClock.FiveSec_Width

			innerX = innerRadius * math.sin(math.radians(tickAngle)) + outerRadius + AnalogueClock.Offset
			innerY = innerRadius * math.sin(math.radians(90 - tickAngle)) + outerRadius + AnalogueClock.Offset
			
			outerX = outerRadius * math.sin(math.radians(tickAngle)) + outerRadius + AnalogueClock.Offset
			outerY = outerRadius * math.sin(math.radians(90 - tickAngle)) + outerRadius + AnalogueClock.Offset

			self.CanvasBox.create_line(innerX, innerY, outerX, outerY, fill = self.Opposite, width = width)

	def DrawMinuteHand(self, microseconds):
		minutes = microseconds/60000000
		self.MinuteAngle = minutes * 360/60
		x = AnalogueClock.ClockRadius*0.6*(1 - math.sin(math.radians(self.MinuteAngle))) + AnalogueClock.Offset
		y = AnalogueClock.ClockRadius*0.6*(1 + math.sin(math.radians(90 - self.MinuteAngle))) + AnalogueClock.Offset
		self.CanvasBox.coords(self.MinuteHand, (AnalogueClock.ClockRadius + AnalogueClock.Offset, AnalogueClock.ClockRadius + AnalogueClock.Offset, x,y))

	def DrawSecondHand(self, microseconds):
		seconds = microseconds/1000000.0
		self.SecondAngle = seconds * 360/60
		x = AnalogueClock.ClockRadius*(1 - math.sin(math.radians(self.SecondAngle))) + AnalogueClock.Offset
		y = AnalogueClock.ClockRadius*(1 + math.sin(math.radians(90 - self.MinuteAngle))) + AnalogueClock.Offset
		self.CanvasBox.coords(self.SecondHand, (AnalogueClock.ClockRadius + AnalogueClock.Offset, AnalogueClock.ClockRadius + AnalogueClock.Offset, x, y))


'''
Player class: a class to represent the Window of a player (black or white). 
Messages are set at the top of the window, and information about whether 
it's currently the player's turn is maintained. 
'''
class Player:
	Font = 'Garamond'
	ButtonWidth       = 20
	ButtonNameString  = "Set Name"
	ButtonTimeString  = "Set Time"
	EntryWidth        = 50
	Microsecond_Conversion  = 1.0/1000000
	Microseconds_per_Minute = 60000000
	Microseconds_per_Second = 1000000
	Turn = 'white'
	def __init__(self, player):
		self.Master = Tk()
		self.Header = PlayerHeader(self.Master, player)
		self.Header.SetMessage(PlayerHeader.WelcomeMessage)
		self.Clock  = AnalogueClock(self.Master, player)
		self.Player = player
		if(self.Player == 'white'):
			self.Opposite = 'black'
		else:
			self.Opposite = 'white'

		self.EntryBox = Entry(self.Master, fg=self.Opposite, bg = self.Player, width = Player.EntryWidth)
		self.EntryBox.pack()
		self.EntryBox.focus_set()
		self.EntryBox.bind('<Return>', self.GetName)


		self.ButtonBox = Button(self.Master, width=Player.ButtonWidth, text=Player.ButtonNameString, command = self.GetName)
		self.ButtonBox.pack()
		self.Microseconds = 0
		self.Master.mainloop()


	def ClearEntry(self):
		self.EntryBox.delete(0,'end')

	def SetButtonCommand(self, new_command):
		self.ButtonBox.config(command = new_command)

	# On Game Setup, accept the person's name
	def GetName(self, event):
		string_entry = self.EntryBox.get()
		if len(string_entry) == 0:
			self.Header.SetMessageColor(PlayerHeader.ErrorColor)
			self.Header.SetMessage(PlayerHeader.LenZeroErrorMessage)
			return
		elif len(string_entry) > 30:
			self.Header.SetMessageColor(PlayerHeader.ErrorColor)
			self.Header.SetMessage(PlayerHeader.OverLenErrorMessage)
			return
		else:
			self.Header.SetName(string_entry)
			self.ClearEntry()
			self.EntryBox.bind('<Return>', self.GetTime)
			self.ButtonBox.config(text = Player.ButtonTimeString)
			self.SetButtonCommand(self.GetTime)
			self.Header.SetMessageColor(PlayerHeader.NonErrorColor)
			self.Header.SetMessage(PlayerHeader.GoodNameMessage)

	#On Game Setup, accept a new time 
	def GetTime(self, event):
		timelist = self.EntryBox.get().split(':')
		if len(timelist) != 2:
			self.Header.SetMessageColor(PlayerHeader.ErrorColor)
			self.Header.SetMessage(PlayerHeader.BadFormatMessage)

		try:
			Minutes = int(timelist[0])
		except ValueError as ex:
			self.Header.SetMessageColor(PlayerHeader.ErrorColor)
			self.Header.SetMessage(PlayerHeater.BadMinuteFormatMessage)
			return

		if Minutes < 0:
			self.Header.SetMessageColor(PlayerHeader.ErrorColor)
			self.Header.SetMessage(PlayerHeader.BadMinuteRangeMessage)
			return

		try:
			Seconds = int(timelist[1])
		except ValueError as ex:
			self.Header.SetMessageColor(PlayerHeader.ErrorColor)
			self.Header.SetMessage(PlayerHeader.BadSecondFormatMessage)
			return

		if Seconds < 0 or Seconds > 59:
			self.Header.SetMessageColor(PlayerHeader.ErrorColor)
			self.Header.SetMessage(PlayerHeader.BadSecondRangeMessage)
			return

		self.Header.MessageDisplay.pack_forget()
		self.ButtonBox.pack_forget()
		self.EntryBox.pack_forget()
		self.Microseconds = Minutes*Player.Microseconds_per_Minute + Seconds * Player.Microseconds_per_Second
		self.Clock.DrawMinuteHand(self.Microseconds)
		self.Clock.DrawSecondHand(self.Microseconds)
		self.Clock.DrawClock()
		self.Clock.DrawTicks()
		self.SetDigitalClock()
		self.SetSecondHand()
		self.SetMinuteHand()
    	
	#Set the digital clock
	def SetDigitalClock(self):
		if Player.Turn == self.Player:
			timestamp = self.Header.TimeStamp(self.Microseconds)
			self.Header.SetClock(timestamp)
		self.Header.ClockDisplay.after(10, self.SetDigitalClock)

	#Set the analogue clock 
	def SetSecondHand(self):
		if Player.Turn == self.Player:
			Angle = (((self.Microseconds*Player.Microsecond_Conversion)%60)/60)*360 + 180
			self.Clock.SecondAngle = Angle
			self.Clock.DrawSecondHand(self.Microseconds)
		self.Clock.CanvasBox.after(10, self.SetSecondHand)

	def SetMinuteHand(self):
		if Player.Turn == self.Player:
			minutes, micros = divmod(self.Microseconds, Player.Microseconds_per_Minute)
			Angle = minutes * 360/60 
			self.Clock.MinuteAngle = Angle
			self.Clock.DrawMinuteHand(self.Microseconds)
		self.Clock.CanvasBox.after(10, self.SetMinuteHand)

	#To be called when self.Microseconds is updated. 
	def Tick(self):
		self.SetDigitalClock()
		self.SetSecondHand()
		self.SetMinuteHand()

'''
ChessClock class: a wrapper class for the entire GUI. 
'''
class ChessClock:
	def __init__ (self):
		self.Turn = 'white'
		self.WhitePlayer = Player('white')
		self.BlackPlayer = Player('black')
		self.Alarm = False


'''
Switch thread: a Thread to be running in the backround 
which is listening for keyboard taps on any key of the keyboard. 
When a key is tapped, the current player's clock is paused 
and the other player's clock is started. 
'''
def Switch(clock):
	global Exit
	while clock.WhitePlayer.Microseconds > 0 and clock.BlackPlayer.Microseconds > 0:
		inkey = _Getch()
		k = inkey()
		if k == "C":
			Exit = 1
			sys.exit(0)
		elif k:
			if Player.Turn == 'white':
				Player.Turn = 'black'
			else:
				Player.Turn = 'white'



def main():
	clock = ChessClock()
	thread1 = threading.Thread(target=Switch, args=(clock,))
	thread1.start()

if __name__ == "__main__":
	main();




   






















