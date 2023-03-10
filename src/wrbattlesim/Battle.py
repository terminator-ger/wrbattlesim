import numpy as np
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.constants import BLUE, RED

from wrbattlesim.UnitWidget import UnitWidget
from wrbattlesim.ArmyInfoWidget import ArmyInfoWidget
from wrbattlesim.config import *

class Battle(toga.Box):
    def __init__(self):
        super().__init__(self, style=Pack(direction=COLUMN))
        self.N_UNIT_TYPES = 5
        self.N_UNITS_GROUND = 3
        self.flex = 1/(self.N_UNIT_TYPES+1)

        self.col_weights = [0.2, 0.4, 0.4]
        self.labels = []
        
        self.dummy_label = toga.ImageView()

        self.units = {'A' :{'land': [], 'air': [], 'sea':[]},
                      'B' :{'land': [], 'air': [], 'sea':[]}}
        
        self.info_red = ArmyInfoWidget(flex=self.col_weights[1],
                                                        color='red',
                                                        desc='RedFor')
        self.info_blue = ArmyInfoWidget(flex=self.col_weights[2],
                                                        color='blue',
                                                        desc='BlueFor')
        self.parent_app = None

    def add_units(self, T:str):
        print(self.labels[0])
        self.add(toga.Box(style=Pack(direction=ROW,
                                    flex=self.flex,
                                    height=ROW_HEIGHT),
                            children=[self.dummy_label,
                                        self.info_red, 
                                        self.info_blue]))
                                        
        for n in range(self.N_UNIT_TYPES):
            if n < self.N_UNITS_GROUND:
                self.add(toga.Box(style=Pack(direction=ROW, 
                                             flex=self.flex,
                                             height=ROW_HEIGHT),
                                    children = [self.labels[n], 
                                                self.units['A'][T][n], 
                                                self.units['B'][T][n]]))

            else:
                self.add(toga.Box(style=Pack(direction=ROW, 
                                                flex=self.flex, 
                                                height=ROW_HEIGHT),
                                    children = [self.labels[n],
                                                self.units['A']['air'][n-self.N_UNITS_GROUND], 
                                                self.units['B']['air'][n-self.N_UNITS_GROUND]]))


class LandBattle(Battle):
    def __init__(self, parent_app):
        #super(LandBattle, self).__init__(parent=parent)
        super().__init__()
        self.N_UNIT_TYPES = 5
        self.N_UNITS_GROUND = 3
        self.flex = 1/(self.N_UNIT_TYPES+1)

        self.col_weights = [0.2, 0.4, 0.4]
        self.parent_app = parent_app
        # inf 
        self.units['A']['land'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Defensive', 'Offensive'], padding_right=25))
        self.units['B']['land'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Defensive', 'Offensive'], padding_bottom=0))
        # ART
        self.units['A']['land'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Anti-Air', 'Ground'], padding_right=25))
        self.units['B']['land'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Anti-Air', 'Ground'], padding_bottom=0))
         # ARM
        self.units['A']['land'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Defensive', 'Offensive'], padding_right=25))
        self.units['B']['land'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Defensive', 'Offensive'], padding_bottom=0))
        
        # Fighter                                                       
        self.units['A']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Air', 'Ground'], padding_right=25))
        self.units['B']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Air', 'Ground'], padding_bottom=5))

        # Bomber
        self.units['A']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Strategic', 'Air/Ground'], padding_right=25))
        self.units['B']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Strategic', 'Air/Ground'], padding_bottom=0))



        self.labels = [toga.ImageView(toga.Image('./resources/yellow_ground.jpg'),style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/blue_ground.jpg')  ,style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/green_ground.jpg') ,style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/green_air.jpg')    ,style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/red_air.jpg')      ,style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT))]
        self.dummy_label = toga.ImageView(toga.Image('./resources/ground_dummy.png')      ,style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT))

        self.add_units(T='land')


class SeaBattle(Battle):
    def __init__(self, parent_app):
        #super(SeaBattle, self).__init__(parent=parent)
        super().__init__()
        self.N_UNIT_TYPES = 6
        self.N_UNITS_GROUND = 4
        self.flex = 1/(self.N_UNIT_TYPES+1)
        
        self.col_weights = [0.2, 0.4, 0.4]
        self.parent_app = parent_app

        #sub
        self.units['A']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['-'], padding_right=25))
        self.units['B']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['-'], padding_bottom=5))
        # Cruiser
        self.units['A']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Escort', 'Offensive'], padding_right=25))
        self.units['B']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Escort', 'Offensive'], padding_bottom=5))
         # carrier
        self.units['A']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Anti-Air', 'Offensive'], padding_right=25))
        self.units['B']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Anti-Air', 'Offensive'], padding_bottom=5))
        #batttleship
        self.units['A']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Anti-Air', 'Offensive'], padding_right=25))
        self.units['B']['sea'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Anti-Air', 'Offensive'], padding_bottom=5))
        # Fighter                                parent_app=self.parent_app,                        
        self.units['A']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Air', 'Ground'], padding_right=25))
        self.units['B']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Air', 'Ground'], padding_bottom=5))

        # Bomber
        self.units['A']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[1], stance_desc=['Air/Ground', 'Strategic'],padding_right=25))
        self.units['B']['air'].append(UnitWidget(parent_app=self.parent_app, flex=self.col_weights[2], stance_desc=['Air/Ground', 'Strategic'], padding_bottom=5))


        self.labels = [toga.ImageView(toga.Image('./resources/yellow_sea.jpg'),style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/blue_sea.jpg'),  style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/green_sea.jpg'), style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/red_sea.jpg'),   style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/green_air.jpg'), style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT)),
                       toga.ImageView(toga.Image('./resources/red_air.jpg'),   style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT))]
        self.dummy_label = toga.ImageView(toga.Image('./resources/sea_dummy.png')      ,style=Pack(flex=self.col_weights[0], width=50, height=ROW_HEIGHT))
        
        self.add_units(T='sea')

