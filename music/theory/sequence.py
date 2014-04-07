""" keeps track of sequence of items of specific durations """
from copy import copy
class Sequence:
    items = []
    
    def __init__(self, items=[]):
        self.items = items
    
    def append(self, item, length):
        self.items.append((item, length))
    
    def prepend(self, item, length):
        self.items.prepend((item, length))
    
    def insert(self, position, item, length, method='split'):
        """Insert item into stream at specified position.
        
        "method" can be set to 'replace', 'split', or 'overwrite'."""
        
        if method == 'replace':
            index = self.get_index_at_position(position)
            self.items[index] = item, length
        elif method == 'split':
            self.delete_range(position, position) #0 length of range, splits
            index = self.get_index_at_position(position)
            self.items.insert(index, (item, length))
        elif method == 'overwrite':
            self.delete_range(position, position+length)
            index = self.get_index_at_position(position)
            self.items.insert(index, (item, length))
            pass
        return self
    
    def insertAtIndex(self, index, item, length):
        self.items.insert(index, (item, length))
        
    def get_position_at_index(self, index):
        index = min(index, len(self.items))
        return sum([self.items[i][1] for i in range(index)])
    
    def get_index_at_position(self, position):
        '''Get index of item that exists at specified position.'''
        i = 0
        counter = 0
        position = max(position, 0)
        for (_, length) in self.items:
            counter += length
            if position < counter:
                return i
            i += 1
        return None
    
    def get_item_at_position(self, position):
        index = self.get_index_at_position(position)
        if index is None:
            return None
        return self.items[index]
        
    def get_bounds_at_index(self, index):
        if (index >= len(self.items)):
            return None
        pos = self.get_position_at_index(index)
        return pos, pos+self.items[index][1]
    
    def delete_range(self, start, end):
        i = -1
        items_copy = copy(self.items)
        for item, _ in self.items:
            i += 1
            if i >= len(self.items):
                break
            bounds = self.get_bounds_at_index(i)
            if bounds[1] < start:
                continue
            if bounds[0] > end:
                break
            
            if start > bounds[0] and end < bounds[1]:
                items_copy[i] = (item, max(0, start - bounds[0]))
                i+=1
                items_copy.insert(i, (item, max(0, bounds[1] - end)))
            if bounds[0] > start:
                items_copy[i] = (item, max(0, bounds[1] - end))
            elif bounds[1] < end:
                items_copy[i] = (item, max(0, start - bounds[0]))
        self.items = filter(lambda x: x[1]!=0, items_copy)
        return self
        
if (__name__ == '__main__'):
    st = Sequence([('a',1), ('b',2), ('c',2), ('d',1)])
    print st.insert(2, 'f', 3, 'overwrite').items