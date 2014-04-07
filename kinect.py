from OSC import OSCServer, OSCClient, OSCMessage
import time
from vector import Magnitude, SubVector, Distance, Area
import copy
from utilities import wait_for, sprout

X = 0
Y = 1
Z = 2

kinect_instance = None

class Kinect:
    """Manages connection to Kinect, and saves and processes coordinates"""
    
    @staticmethod
    def retrieve(joints=None, max_port=5555):
        """ Retrieves a singleton Kinect instance, and creates it if it doesn't exist. """
        global kinect_instance
        if kinect_instance is None:
            kinect_instance = Kinect(joints, max_port)
        return kinect_instance
    
    def __init__(self, joints=None, max_port=5555):
        if joints is None:
            self.joints = ['righthand', 'lefthand', 'rightfoot', 'leftfoot', 'head', 'torso']
        else:
            self.joints = joints
        
        self.coords = {k:(0.,0.,0.) for k in self.joints}
        self.prev_coords = {k:(0.,0.,0.) for k in self.joints}
        self.joint_speed = {k:False for k in self.joints}
        self.speed_piano = {'lefthand':{X:0, Y:0}, 'righthand':{X:0, Y:0}}
        self.kinect_client = OSCClient()
        self.max_client = OSCClient()
        self.server = OSCServer(('127.0.0.1', 12345))
        self.kinect_client.connect(('127.0.0.1', 12346))
        self.max_client.connect(('127.0.0.1', max_port))
        self.server.addMsgHandler('default', self.process_message)
        
        self.flipped = False
        self.speed = 0.
        self.speed_ramp = 0.
        
        sprout(self.server.serve_forever)
        sprout(self._remind_synapse)
        #sprout(self._calc_speed)
    
    def __enter__(self):
        return self
    
    def __exit__(self, _type, value, traceback):
        self.server.close()
        self.kinect_client.close()
        self.max_client.close()
    
    def process_message(self, addr, tags, data, source):
        """process data coming in from Synapse, happens about every 0.03 seconds"""
        
        if addr[-9:] == '_pos_body':
            if self.flipped:
                if addr[:5] == '/left':
                    addr = '/right' + addr[5:]
                    data[X] = -data[X]
                elif addr[:6] == '/right':
                    addr = '/left'+addr[6:]
                    data[X] = -data[X]
            self.coords[addr[1:-9]] = data
    
    def _remind_synapse(self):
        """Send Synapse an OSC message to ask it to continue polling the required joints"""
        while True:
            for track in self.joints:
                self.sendToKinect('/'+track+'_trackjointpos', 1)
            time.sleep(1)
    
    def calc_speed(self):
        """Calculate speed of movement, at 0.06 second intervals"""
        self.calculating_speed = True
        while self.calculating_speed:
            total_speed = 0.
            for joint, v in self.coords.items():
                magnitude = Magnitude(v)
                prev_magnitude = Magnitude(self.prev_coords[joint])
                speed = abs(magnitude - prev_magnitude)
                if joint in ('lefthand', 'righthand'):
                    speed_x = Distance(SubVector(self.prev_coords[joint], X), 
                                              SubVector(self.coords[joint], X))
                    speed_y = Distance(SubVector(self.prev_coords[joint], Y), 
                                              SubVector(self.coords[joint], Y))
                    self.speed_piano[joint][X] += (speed_x - self.speed_piano[joint][X]) * 0.5
                    self.speed_piano[joint][Y] += (speed_y - self.speed_piano[joint][Y]) * 0.5
                total_speed += speed
            total_speed /= len(self.coords)
            self.speed = total_speed
            self.speed_ramp = self.speed_ramp + (self.speed - self.speed_ramp) * 0.125
            self.prev_coords = copy.copy(self.coords)
            time.sleep(0.06)
    
    @property
    def area(self):
        return Area( self.coords['head'], 
                     self.coords['lefthand'], 
                     self.coords['leftfoot'], 
                     self.coords['rightfoot'], 
                     self.coords['righthand'] ) / 1000000.
        
    @property
    def facing(self):
        return self.coords['rightfoot'][X] >= self.coords['leftfoot'][X]
    
    def hand_down(self, hand):
        return self.coords[hand][Y] < 0 and self.hand_over_piano(hand)
    
    def hand_up(self, hand):
        return self.coords[hand][Y] >= 0 or not self.hand_over_piano(hand)

    def hand_over_piano(self, hand):
        return Magnitude(SubVector(self.coords[hand], Y,Z)) > 350
    
    def hand_hit(self, hand):
        """waits for a hit from the specified hand"""
        if self.hand_down(hand):
            wait_for(self.hand_up, (hand,))
        wait_for(self.hand_down, (hand,))
        
        return self.coords[hand][X]
        
    def joint_moved_x(self, prev_x, joint, hit_location):
        """used to wait for a change in joint in X dimension"""
        if self.hand_up(joint):
            return True
        if hit_location is not None and abs(hit_location - self.coords[joint][X]) < 140:
            return False
        return abs(prev_x - self.coords[joint][X]) > 70
    
    def hand_slide(self, hand, hit_location):
        x = self.coords[hand][X]
        wait_for(self.joint_moved_x, (x, hand, hit_location))
        
        if self.hand_up(hand):
            return False
        return self.coords[hand][X]
    
    def get_coord(self, joint):
        if joint == 'leftshoulder':
            return -250, 200, -50
        elif joint == 'rightshoulder':
            return 250, 200, -50
        else:
            return self.coords[joint]
    
    def sendToKinect(self, address, items):
        self._sendMsg(self.kinect_client, address, items)
    
    def sendToMax(self, address, items):
        self._sendMsg(self.max_client, address, items)
    
    @staticmethod
    def _sendMsg(client, address, items):
        m = OSCMessage()
        m.setAddress(address)
        m.append(items)
        client.send(m)
    

def poll():
    while True:
        kinect.sendToMax('/coords', kinect.coords['head'])
        kinect.sendToMax('/area', kinect.area)
        kinect.sendToMax('/speed', kinect.speed_ramp)
        kinect.sendToMax('/lhspeedx', kinect.speed_piano['lefthand'][X])
        kinect.sendToMax('/lhspeedy', kinect.speed_piano['lefthand'][Y])
        time.sleep(0.05)

if (__name__ == '__main__'):
    with Kinect() as kinect:
        sprout(poll)
        while True:
            time.sleep(1)
        
    