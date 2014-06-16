import json


class Data(object):
    '''The json dictionary container that holds the all of the song data.'''
    def __init__(self, filename, fcn=list):
        self.filename = filename
        self.fcn = fcn
    
    def __iter__(self):
        for item in self.data:
            yield item
    
    def __enter__(self, *args, **kwargs):
        try:
            self.data = json.load(open(self.filename))
        except Exception as e:
            print e
            print ' Failed to load: {}'.format(self.filename)
            self.data = self.fcn()
        return self
    
    def __exit__(self, *args, **kwargs):
        json.dump(self.data, 
                  open(self.filename,'w'),
                  indent=2)