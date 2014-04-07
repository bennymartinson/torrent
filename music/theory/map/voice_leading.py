from harmony_map import HarmonyMap
from line_map import LineMap

class VoiceLeading:
    harmony = None
    line_maps = None
    
    def __init__(self, harmony_map=None, line_maps=None):
        if harmony_map is None:
            harmony_map = HarmonyMap()
        if line_maps is None:
            line_maps = []
        self.harmony_map = harmony_map
        self.line_maps = line_maps
        
    def pick(self):
        self.harmony_map.set_items(self.harmony)
        for lm in self.line_maps:
            lm.current_harmony = self.harmony_map
        
        # go through all lines and pick notes for this harmony
        choices = []
        for lm in self.line_maps:
            choices.append(lm.pick())
        self.harmony_map.prev_picks = []
        
        return choices