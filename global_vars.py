import time
from kinect import Kinect, X, Y, Z
from midi_interface import MidiInterface
from utilities import sprout, scale_constrain
from events import Events

key = 60
beat = 0.125
kinect = Kinect.retrieve()
midi = MidiInterface.retrieve()
min_piano_dur = 0.15
min_piano_up = 0.05
events = Events.retrieve()