import rtmidi
import time
import random
import threading
import sys
from utilities import sprout


class MidiPlayer:
    midiout = rtmidi.RtMidiOut()
    channel = 1
    sustain = False
    notesOn = {}
    device = 'MIDISPORT 2x2 Port A'
    device2 = 'USB-MIDI'
    
    def __init__(self, channel=1):
        self.promptPort()
        self.channel = channel
        
    def promptPort(self):
        ports = range(self.midiout.getPortCount())
        names = []
        for i in ports:
            names.append(self.midiout.getPortName(i))
            if self.midiout.getPortName(i) == self.device:
                print "Connected to the device {}.".format(self.device)
                self.midiout.openPort(i)
                return
        for i in ports:
            if self.midiout.getPortName(i) == self.device2:
                print "Connected to the device {}.".format(self.device2)
                self.midiout.openPort(i)
                return
        print "The device {} was not found.".format(self.device)
        if len(names) == 0:
            print "No other instruments are open.  Quitting program now."
            sys.exit()
        else:
            "The following instruments were found:",
            for i, name in enumerate(names):
                print "{0}: {1}".format(i, name)
            port = raw_input("Please type of the number of the port you'd like to open.")
            self.midiout.openPort(int(port))
    
    def note(self, pitch=60, dur=1, velocity=80, layer=0):
        if pitch in self.notesOn and self.notesOn[pitch]['layer'] > layer:
            return
        elif pitch in self.notesOn:
            self.notesOn[pitch]['timer'].cancel()
            self.noteOff(pitch, layer)
            timer = threading.Timer(0.1, self.note, (pitch,dur,velocity,layer))
            timer.start()
            return
        
        
        message = rtmidi.MidiMessage.noteOn(self.channel, 0, velocity)
        message.setNoteNumber(pitch)
        self.midiout.sendMessage(message)
        timer = threading.Timer(dur, self.noteOff, (pitch,layer))
        timer.start()
        self.notesOn[pitch] = {'layer':layer, 'timer':timer}
        
    
    def noteOff(self, pitch, layer=0):
        if pitch in self.notesOn and self.notesOn[pitch]['layer'] <= layer:
            if pitch not in self.notesOn:
                return
            del self.notesOn[pitch]
            message = rtmidi.MidiMessage.noteOff(self.channel, 0)
            message.setNoteNumber(pitch)
            self.midiout.sendMessage(message)
    
    def controllerEvent(self, event_type, value):
        message = rtmidi.MidiMessage.controllerEvent(self.channel, event_type, value)
        self.midiout.sendMessage(message)
    
    def setSustain(self, value):
        self.sustain = value
        if value:
            self.controllerEvent(64, 127)
        else:
            self.controllerEvent(64, 0)

if (__name__ == '__main__'):
    player = MidiPlayer(1)
    for i in range(0, 100):
        pitch = random.randint(60, 80)
        player.note(pitch, 0.1, 80)
        time.sleep(0.125)