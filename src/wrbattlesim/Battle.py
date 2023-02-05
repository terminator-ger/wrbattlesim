import numpy as np
import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.constants import BLUE, RED

from wrbattlesim.UnitWidget import UnitWidget

class Battle(toga.Box):
    def __init__(self):
        toga.Box.__init__(self, style=Pack(direction=COLUMN))

        self.N_UNIT_TYPES = 5
        self.N_UNITS_GROUND = 3
        self.flex = 1/(self.N_UNIT_TYPES+1)

        self.col_weights = [0.2, 0.4, 0.4]
        self.labels = []
        

        self.units = {'A' :{'land': [], 'air': [], 'sea':[]},
                      'B' :{'land': [], 'air': [], 'sea':[]}}


    def add_units(self, T:str):
        self.add(toga.Box(style=Pack(direction=ROW, flex=self.flex),
                            children=[toga.Box(style=Pack(flex=self.col_weights[0], width=50, height=50)),
                                        toga.Label("A", style=Pack(flex=self.col_weights[1], background_color=RED)),
                                        toga.Label("B", style=Pack(flex=self.col_weights[2], background_color=BLUE))]))



        for n in range(self.N_UNIT_TYPES):
            if n < self.N_UNITS_GROUND:
                self.add(toga.Box(style=Pack(direction=ROW, 
                                             flex=self.flex),
                                    children = [self.labels[n], 
                                                self.units['A'][T][n], 
                                                self.units['B'][T][n]]))

            else:
                self.add(toga.Box(style=Pack(direction=ROW, 
                                                flex=self.flex),
                                    children = [self.labels[n],
                                                self.units['A']['air'][n-self.N_UNITS_GROUND], 
                                                self.units['B']['air'][n-self.N_UNITS_GROUND]]))


class LandBattle(Battle):
    def __init__(self):
        super(LandBattle, self).__init__()
        self.N_UNIT_TYPES = 5
        self.N_UNITS_GROUND = 3
        self.flex = 1/(self.N_UNIT_TYPES+1)

        self.col_weights = [0.2, 0.4, 0.4]
        # inf 
        self.units['A']['land'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Defensive', 'Offensive']))
        self.units['B']['land'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Defensive', 'Offensive']))
        # ART
        self.units['A']['land'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Anti-Air', 'Ground']))
        self.units['B']['land'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Anti-Air', 'Ground']))
         # ARM
        self.units['A']['land'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Defensive', 'Offensive']))
        self.units['B']['land'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Defensive', 'Offensive']))
        
        # Fighter                                                       
        self.units['A']['air'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Air', 'Ground']))
        self.units['B']['air'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Air', 'Ground']))

        # Bomber
        self.units['A']['air'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Air/Ground', 'Strategic']))
        self.units['B']['air'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Air/Ground', 'Strategic']))



        self.labels = [toga.ImageView(toga.Image('./resources/yellow_ground.jpg'),style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/blue_ground.jpg')  ,style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/green_ground.jpg') ,style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/green_air.jpg')    ,style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/red_air.jpg')      ,style=Pack(flex=self.col_weights[0], width=50, height=50))]

        self.add_units(T='land')


class SeaBattle(Battle):
    def __init__(self):
        super(SeaBattle, self).__init__()
        self.N_UNIT_TYPES = 6
        self.N_UNITS_GROUND = 4
        self.flex = 1/(self.N_UNIT_TYPES+1)
        
        self.col_weights = [0.2, 0.4, 0.4]

        #sub
        self.units['A']['sea'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['-']))
        self.units['B']['sea'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['-']))
        # Cruiser
        self.units['A']['sea'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Escort', 'Offensive']))
        self.units['B']['sea'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Escort', 'Offensive']))
         # carrier
        self.units['A']['sea'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Anti-Air', 'Offensive']))
        self.units['B']['sea'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Anti-Air', 'Offensive']))
        #batttleship
        self.units['A']['sea'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Anti-Air', 'Offensive']))
        self.units['B']['sea'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Anti-Air', 'Offensive']))
        # Fighter                                                       
        self.units['A']['air'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Air', 'Ground']))
        self.units['B']['air'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Air', 'Ground']))

        # Bomber
        self.units['A']['air'].append(UnitWidget(flex=self.col_weights[1], stance_desc=['Air/Ground', 'Strategic']))
        self.units['B']['air'].append(UnitWidget(flex=self.col_weights[2], stance_desc=['Air/Ground', 'Strategic']))


        self.labels = [toga.ImageView(toga.Image('./resources/yellow_sea.jpg'),style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/blue_sea.jpg'),  style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/green_sea.jpg'), style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/red_sea.jpg'),   style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/green_air.jpg'), style=Pack(flex=self.col_weights[0], width=50, height=50)),
                       toga.ImageView(toga.Image('./resources/red_air.jpg'),   style=Pack(flex=self.col_weights[0], width=50, height=50))]
        
        self.add_units(T='sea')

