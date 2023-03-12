import numpy as np

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.constants import BLUE, RED

from wrbattlesim.config import ROW_HEIGHT, BTN_SIZE
from wrbattlesim.DiceInfo import DiceInfo

class ArmyInfoWidget(toga.Box):
    def __init__(self, flex, 
                        color=None, 
                        desc='Red-For',
                        padding_bottom=0, 
                        padding_right=0):
        toga.Box.__init__(self, style=Pack(direction=COLUMN, 
                                            flex=flex, 
                                            height=ROW_HEIGHT,
                                            padding_left=5, 
                                            padding_right=padding_right, 
                                            padding_bottom=padding_bottom))

        self.label = toga.Label(desc, style=Pack(height=ROW_HEIGHT//2, 
                                                    padding_left=10, 
                                                    padding_top=10,
                                                    background_color=color))


        
        self.dice_info = DiceInfo()

        self.box_btn = toga.Box(children=[self.label],
                                    style=Pack(direction=ROW, 
                                                height=ROW_HEIGHT//2))
                                                #width=100)) 


        self.add(self.box_btn)
        self.add(self.dice_info)

    def update(self, vs_air, vs_ground):
        self.dice_info.update(vs_air, vs_ground)
