import time
import global_vars
import vector
from utilities import sprout, stay_alive

kinect = global_vars.kinect
events = global_vars.events

class Gesture:
    rate = 0.05
    detecting = True
    send_token = None
    
    def __init__(self, *args):
        self._setup(*args)
    
    def _setup(self):
        pass
    
    def detect(self, send_token=None):
        if send_token is None and self.send_token is not None:
            send_token = self.send_token
        sprout(self._detect_loop, send_token)
    
    def _detect_loop(self, send_token):
        while self.detecting:
            detected = False
            while not detected and self.detecting:
                time.sleep(self.rate)
                detected = self._detect()
            
            if send_token is not None:
                events.send(send_token) # Broadcast specified message
    
    def stop(self):
        self.detecting = False
    
    def _detect(self):
        """Looks for trace of gesture.  If found, return value, otherwise return False.
        
        To be overridden by descendant classes."""
        return True

class Facing(Gesture):
    facing = True
    
    def _detect(self):
        newfacing = kinect.facing
        if newfacing != self.facing:
            self.facing = newfacing
            events.send('facing_'+('front' if self.facing else 'back'))
        return False

class Switch(Gesture):
    rate = 0.01
    def __init__(self, start_token=None, stop_token=None):
        self._setup(start_token, stop_token)
    
    def _setup(self, start_token, stop_token):
        self.hand_positions = {'lefthand':[(0,0,0)],'righthand':[(0,0,0)]}
        if start_token is not None:
            events.listen(start_token, self.detect)
        if stop_token is not None:
            events.listen(stop_token, self.stop)
    
    def _detect(self):
        pos_length = int(0.25/self.rate)
        
        for hand,shoulder in ('lefthand','leftshoulder'), ('righthand','rightshoulder'):            
            shoulderpos = kinect.get_coord(shoulder)
            pos = kinect.coords[hand]
            positions = self.hand_positions[hand][-pos_length:]
            positions.append(pos)
            self.hand_positions[hand] = positions
            if (vector.Distance(positions[-1],shoulderpos) >= 400
                and vector.Distance(positions[-2],shoulderpos) < 400
                and vector.Distance(positions[0],shoulderpos) < 300):
                return vector.UnitVector(vector.Subtract(pos, shoulderpos)), hand
        return False

class DirectionSwitch(Switch):
    
    def _detect(self):
        val = Switch._detect(self)
        if val is False:
            return False
        v, hand = val
        
        for direction, compare_vector in ( ('top', (0,1,0)),
                                           ('left',(-1,-.4,0)),
                                           ('right',(1,-.4,0)) ):
            if vector.Angle(v, compare_vector) < 30:
                if direction == 'top':
                    events.send('switch_top')
                    events.send('switch_top_'+hand)
                else:
                    events.send('switch_'+direction)
        return False

class Ictus(Gesture):
    history = None
    joint = None
    stage = 0 # 1 = rebound (up), 0 = ictus, -1 = approach (down)
    avg_magnitude = 0
    magnitude = 0
    points_to_average = 3 # the number of points to average
    decay = 0.7
    
    def _setup(self, joint='lefthand'):
        self.joint = joint
        self.history = []
    
    def _detect(self):
        self.history.append(kinect.get_coord(self.joint))
        if len(self.history) < self.points_to_average+1:
            return False
        self.history = self.history[-(self.points_to_average+1):]
        
        vec = self._moving_average_vector()
        
        magnitude = vector.Magnitude(vec)
        self.magnitude = magnitude
        self.avg_magnitude = (self.avg_magnitude * self.decay) + ( magnitude * (1-self.decay))
        
        slow = magnitude < 20
        paused = magnitude < 10
        if paused:
            # if paused
            if self.stage == -1:
                self.stage = 0 # paused at ictus
                return True
            return False
        elif self.stage == 0 and vec[1] > 0: 
            # if rebounding from ictus
            self.stage = 1
            return False
        elif self.stage == 1 and vec[1] < 0 and not slow:
            # if switching from rebound to approach
            self.stage = -1
            return False
        elif self.stage == -1 and vec[1] > 0:
            #if rebounding from approach, missed ictus
            self.stage = 1
            return True
        return False
    
    def _moving_average_vector(self):
        vectors = []
        for p in range(self.points_to_average):
            vectors.append(vector.Subtract(self.history[-1-p], self.history[-2-p]))
        return vector.Average(*vectors)

class ArmSwipe(Gesture):
    """Looks for both arms to swipe across body outward"""
    history = None
    state = 0
    statestart = 0
    max_dur = 0.5
    send_token = 'arm_swipe'
    def setup(self):
        self.history = []
    
    def _detect(self):
        lefthand = kinect.get_coord('lefthand')
        leftshoulder = kinect.get_coord('leftshoulder')
        righthand = kinect.get_coord('righthand')
        rightshoulder = kinect.get_coord('rightshoulder')
        if rightshoulder[0]-lefthand[0] < 0 and leftshoulder[0]-righthand[0] > 0:
            self.state = 1
            self.statestart = time.time()
        elif self.state == 1:
            if time.time() - self.statestart > self.max_dur:
                print 'not fast enough'
                self.state = 0
            elif righthand[0] - lefthand[0] > 1000:
                self.state = 0 #reset
                return True
        return False

class Stomp(Gesture):
    stage = 0
    send_token = 'stomp'
    
    def _detect(self):
        leftfoot = kinect.get_coord('leftfoot')
        rightfoot = kinect.get_coord('rightfoot')
        
        difference = abs(leftfoot[1]-rightfoot[1])
        if self.stage == 0 and difference > 400:
            self.stage = 1
        elif self.stage == 1 and difference < 50:
            self.stage = 0
            return True
        return False
            

smoothness_instance = None
class Smoothness():
    """Calculate smoothness coefficient for the motion of both hands."""
    
    rate = 0.06
    sample_limit = 20
    prev_displacement = {'lefthand':(0,0,0), 'righthand':(0,0,0)}
    prev_position = {'lefthand':None, 'righthand':None}
    accelerations = {'lefthand':[], 'righthand':[]}
    velocities = {'lefthand':[], 'righthand':[]}
    
    @staticmethod
    def retrieve():
        """ Retrieves a singleton Smoothness instance, and creates it if it doesn't exist. """
        global smoothness_instance
        if smoothness_instance is None:
            smoothness_instance = Smoothness()
        return smoothness_instance
    
    def __init__(self):
        sprout(self.collect)
    
    def collect(self):
        """Sprouted function, collecting samples in the background."""
        self.prev_position = {'lefthand':kinect.get_coord('lefthand'), 
                     'righthand':kinect.get_coord('righthand')}
        
        while True:
            for hand in 'lefthand','righthand':
                position = kinect.get_coord(hand)
                displacement = vector.Subtract(position, self.prev_position[hand])
                acceleration = vector.Distance(displacement, self.prev_displacement[hand])
                self.prev_position[hand] = position
                self.prev_displacement[hand] = displacement
                # We square the acceleration so the variance is exaggerated
                self.accelerations[hand].append(acceleration**2) 
                
                # Limit to latest self.sample_limit samples
                self.accelerations[hand] = self.accelerations[hand][-self.sample_limit:] 
                self.velocities[hand].append(vector.Magnitude(displacement))
                self.velocities[hand] = self.velocities[hand][-self.sample_limit:]
            time.sleep(self.rate)
          
    def value(self, hand):
        """Returns average of the last self.sample_limit samples."""
        return sum(self.accelerations[hand]) / (sum(self.velocities[hand])+.1)

if __name__ == '__main__':
    s = Stomp()
    s.detect('stomp')
    while True:
        time.sleep(2)
    