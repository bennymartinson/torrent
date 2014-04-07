#!/usr/bin/env python


from utilities import stay_alive, color
import global_vars
from gesture import DirectionSwitch, Facing, ArmSwipe, Stomp
from section import ( AirPianoSection, AirPiano2Section, 
                      TremAndHitsSection, HumanizedRepetitionSection, 
                      RhythmSection, AmericanaSection
                    )

midi = global_vars.midi
kinect = global_vars.kinect
kinect.flipped = True
events = global_vars.events


def main():
    '''AirPianoSection('start_ap', 'switch_top_lefthand')
    HumanizedRepetitionSection('long_tremolo', 'switch_top_lefthand')
    PolycrystallineSection('start_poly', 'stop_poly')
    BeatSection('start_beat', 'stop_beat')
    TopTremoloSection('start_trem', 'stop_trem')
    TremAndHitsSection('start_tremandhits', 'stop_tremandhits')'''
    
    ap = AirPianoSection()
    ap2 = AirPiano2Section()
    hr = HumanizedRepetitionSection()
    amer = AmericanaSection()
    rhythm = RhythmSection()
    th = TremAndHitsSection()
    
    DirectionSwitch().detect()
    Facing().detect()
    armswipe = ArmSwipe()
    stomp = Stomp()
    
    def stage1():
        print color('OKGREEN','STAGE 1')
        events.listen('switch_top', stage2)
        
        midi.setSustain(True)
        ap.start()
    
    def stage2():
        print color('OKGREEN','STAGE 2')
        events.unlisten('switch_top', stage2)
        events.listen('long_tremolo', stage3)
        
        midi.setSustain(True)
        ap.stop()
        ap2.start()
    
    def stage3():
        print color('OKGREEN','STAGE 3')
        events.unlisten('long_tremolo', stage3)
        armswipe.detect('arm_swipe')
        events.listen('arm_swipe', stage4)
        
        midi.setSustain(True)
        hr.start()
    
    def stage4():
        print color('OKGREEN','STAGE 4')
        events.unlisten('arm_swipe', stage4)
        armswipe.stop()
        stomp.detect()
        events.listen('stomp', stage5)
        
        midi.setSustain(False)
        amer.start()
        ap2.stop()
        hr.stop()
    
    def stage5():
        print color('OKGREEN','STAGE 5')
        events.unlisten('stomp', stage5)
        events.listen('switch_top', stage6)
        stomp.stop()
        
        midi.setSustain(True)
        rhythm.start()
        
    def stage6():
        print color('OKGREEN','STAGE 6')
        events.unlisten('switch_top', stage6)
        events.listen('stop_tremandhits', th.stop)
        
        midi.setSustain(True)
        amer.stop()
        th.start()
    
    midi.setSustain(True)
    stage1()
    stay_alive()


if __name__ == '__main__':
    main()
