import json
import dateutil.parser
from datetime import datetime
# from bson import json_util


# TODO move this into a standard datatype.



def date_handler(obj):
    return obj.isoformat() if hasattr(obj, 'isoformat') else obj
 
def object_hook(obj):
  if 'date' in obj:
    obj['date'] = dateutil.parser.parse(obj['date']) 
  return obj
 
# print json.dumps(data, default=date_handler)

class Data(object):
    '''The json dictionary container that holds the all of the song data.'''
    def __init__(self, filename, fcn=list):
        self.filename = filename
        self.fcn = fcn
    
    def __iter__(self):
        for item in self.data:
            yield item
    
    def insert(self, index, item):
      self.data.insert(index, item)
    
    def __enter__(self, *args, **kwargs):
        try:
            self.data = json.load(open(self.filename),
                                  object_hook=object_hook)
        except Exception as e:
            print e
            print ' Failed to load: {}'.format(self.filename)
            self.data = self.fcn()
        return self
    
    def __exit__(self, *args, **kwargs):
        json.dump(self.data, 
                  open(self.filename,'w'),
                  default=date_handler,
                  indent=2)