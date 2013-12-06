import sys
import os
import pygame

class Config(object):
    
    def __init__(self, config_file):
        self.config_file = config_file
        self.params = {}

    def parse(self):
        with open(self.config_file) as f:
            for line in f:
                if line[0] == ";":
                    continue;

                if len(line) >= 3:

                    parts = line.split('=', 1)
                    self.params[parts[0]] = parts[1].strip("\n")

                    val = self.params[parts[0]]

                    if val[0] == "#":
                        self.params[parts[0]] = pygame.Color(val)

                    if val == "false":
                        self.params[parts[0]] = False
                    elif val == "true":
                        self.params[parts[0]] = True
                    elif val == "none":
                        self.params[parts[0]] = None
                
