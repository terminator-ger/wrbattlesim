import numpy as np

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.constants import BLUE, RED



class UnitWidget(toga.Box):
    def __init__(self, flex, color=None, stance_desc=['Defensive', 'Offensive']):
        toga.Box.__init__(self, style=Pack(direction=ROW, flex=flex, padding_left=15))

        self.stance_desc = stance_desc
        self.count = 0                                                
        self.counter = toga.Label('0', 
                                        style=Pack(flex=0.2))

        self.btn_up   = toga.Button('+', 
                                    on_press=self.incr, 
                                    style=Pack(flex=0.15))

        self.btn_down = toga.Button('-', 
                                    on_press=self.decr, 
                                    style=Pack(flex=0.15))


        self.stance = toga.Selection(items=self.stance_desc)

        self.box_btn = toga.Box(children=[self.btn_down, self.btn_up, self.counter],
                                    style=Pack(direction=ROW)) 

        self.box_counter = toga.Box(children=[self.box_btn, self.stance],
                                    style=Pack(direction=COLUMN))

        self.add(self.box_counter)


    def get_value(self):
        return self.count
    
    def get_stance(self):
        return np.argwhere(self.stance.value == self.stance_desc)
    
    def reset(self):
        self.count = 0
        self.counter.text = self.count

    def incr(self, ref):
        self.count += 1
        self.counter.text = self.count

    def decr(self, ref):
        if self.count > 0:
            self.count -= 1
        self.counter.text = self.count

