import numpy as np

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.constants import BLUE, RED



class UnitWidget(toga.Box):
    def __init__(self, flex, color=None, stance_desc=['Defensive', 'Offensive'], padding_bottom=0, padding_right=0):
        toga.Box.__init__(self, style=Pack(direction=COLUMN, flex=flex, padding_left=15, padding_right=padding_right, padding_bottom=padding_bottom))

        self.stance_desc = stance_desc
        self.count = 0                                                
        self.counter = toga.Label('0', style=Pack(width=20, height=25, padding_left=15, padding_right=5))

        self.btn_up   = toga.Button('+', 
                                    on_press=self.incr, 
                                    style=Pack( width=50, height=25,))

        self.btn_down = toga.Button('-', 
                                    on_press=self.decr, 
                                    style=Pack(width=50, height=25,))
        self.btn_reset = toga.Button('0', 
                                    on_press=self.reset, 
                                    style=Pack(width=30, height=25,))



        self.stance = toga.Selection(items=self.stance_desc, style=Pack(width=120, height=25))

        self.box_btn = toga.Box(children=[self.btn_down, self.counter, self.btn_up],#, self.btn_reset],
                                    style=Pack(direction=ROW, height=25, width=120)) 
        #self.box_stance = toga.Box(children=[self.stance],
        #                            style=Pack(direction=ROW, height=25, width=120))

        #self.box_counter = toga.Box(children=[ self.box_btn, self.box_stance],
        #                            style=Pack(direction=COLUMN))
        self.add(self.box_btn)
        self.add(self.stance)

        #self.add(self.box_counter)


    def get_value(self):
        return self.count
    
    def get_stance(self):
        return np.argwhere(self.stance.value == self.stance_desc)
    
    def reset(self, ref):
        self.count = 0
        self.counter.text = str(self.count)

    def incr(self, ref):
        self.count += 1
        self.counter.text = str(self.count)

    def decr(self, ref):
        if self.count > 0:
            self.count -= 1
        self.counter.text = str(self.count)

