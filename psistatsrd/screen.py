class Screen(object):
    
    def __init__(self, id, config):
        self.id = id
        self.config = config
        self._background_color = None

    @property
    def background_color(self):

        if self._background_color is not None:
            return self._background_color

        conf_id = "screen.%s.background_color" % self.id
        if conf_id in self.config:
            try:
                colors = self.config[conf_id].split(",",3)
                colors = [int(x) for x in colors]
                
                if len(colors) < 3:
                    raise TypeError()
                return tuple(colors)
            except:
                print "ERROR - Background color for screen %s invalid format" % self.id
        else:
            return (0,0,0)

s = Screen("foo", {"screen.foo.background_color": "244,144,44"})
print s.background_color 
