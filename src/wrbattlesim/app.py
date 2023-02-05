"""
Simulating battles for the board game War Room
"""
import asyncio
import sys

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.constants import BLUE, RED
import functools
import contextvars

from enum import Enum
import threading
import multiprocessing as mp
import aioprocessing as ap

from wrdice.util import *
from wrdice.config import wr20_vaniilla_options
from wrdice.Army import Army
from wrdice.Simulate import Simulate, Simulator, start_sim

from wrbattlesim.Battle import SeaBattle, LandBattle

import threading
import functools
from queue import Queue




class WarRoomBattleSim(toga.App):
    def __init__(self):
        super(WarRoomBattleSim, self).__init__()

        self.config = wr20_vaniilla_options

        #self.q_in = ap.AioSimpleQueue()
        #self.q_out = ap.AioSimpleQueue()
        #self.q_in = mp.SimpleQueue()
        #self.q_out= mp.SimpleQueue()
        self.q_in = Queue()
        self.q_out= Queue()

        '''
        self.sim_proc = ap.AioProcess(target=start_sim, 
                                        args=(self.q_out, 
                                              self.q_in))
        '''

        self.sim_proc = threading.Thread(target=start_sim,
                                        args=(self.q_out, 
                                              self.q_in))
        self.sim_proc.start()

        self.add_background_task(self.eval) 
        self.on_exit = self.join_on_exit

    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """
        self.battle_switch = toga.widgets.switch.Switch('Land Battle',  
                                                        value=False, 
                                                        on_change=self.switch_battle_type,
                                                        style=Pack(flex=0.1))

        self.batch_cap_switch = toga.widgets.switch.Switch('Batchcap Disabled',  
                                                        value=False, 
                                                        on_change=self.switch_batch_cap,
                                                        style=Pack(flex=0.1))
        self.ctrl = toga.Box(style=Pack(direction=ROW), 
                             children = [self.battle_switch, self.batch_cap_switch])

        self.land = LandBattle() 
        self.sea = SeaBattle() 

        self.calc_btn = toga.Button("Calculate",
                                 on_press=self.calc,
                                 style=Pack(flex=0.1))


        self.units_box = toga.Box(style=Pack(flex=0.8), children=[self.land])        
        #self.units_box_scroll = toga.ScrollContainer(content=self.units_box)
        self.units_box_scroll = toga.Box(children=[self.units_box])
        self.spinner = toga.ProgressBar(max=None, running=False)


        self.ui_upper = toga.Box(children=[self.ctrl, self.units_box_scroll, self.calc_btn, self.spinner],
                                    style=Pack(direction=COLUMN, flex=0.5))


        self.results = toga.Label("Battle Results")
        self.battle_results = toga.Box(children=[self.results],
                                        style=Pack(flex=0.5))
        #self.ui_lower = toga.ScrollContainer(style=Pack(flex=0.5), content=self.battle_results) 
        self.ui_lower = toga.Box(style=Pack(flex=0.5), children=[self.battle_results]) 

        self.main_box = toga.Box(children=[self.ui_upper, self.ui_lower],
                                    style=Pack(direction=COLUMN))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def reset_units(self):
        for army in ['A', 'B']:
            for type in ['land', 'air']:
                for unit in self.land.units[army][type]:
                    unit.reset()

        for army in ['A', 'B']:
            for type in ['sea', 'air']:
                for unit in self.sea.units[army][type]:
                    unit.reset()


    def switch_batch_cap(self, btn):
        if btn.value:
            btn.text = 'Batchcap Enabled'
            self.config['batch_cap'] = True
        else:
            btn.text = 'Batchcap Disabled'
            self.config['batch_cap'] = False

    def switch_battle_type(self, btn):
        self.reset_units()
        if btn.value:
            btn.text = 'Sea Battle'
            self.units_box.add(self.sea)
            self.units_box.remove(self.land)
        else:
            btn.text = 'Land Battle'
            self.units_box.remove(self.sea)
            self.units_box.add(self.land)
 
    def get_sea(self, battle, army:str):
        return [battle.units[army]['sea'][0].get_value(),
                battle.units[army]['sea'][1].get_value(),
                battle.units[army]['sea'][2].get_value(),
                battle.units[army]['sea'][3].get_value(),
                0]


    def get_land(self, battle, army:str):
        return [battle.units[army]['land'][0].get_value(),
                battle.units[army]['land'][1].get_value(),
                battle.units[army]['land'][2].get_value(),
                0,0]

    def get_air(self, battle, army:str):
        return [0, 0, 
                battle.units[army]['air'][0].get_value(),
                battle.units[army]['air'][1].get_value(), 
                0]

    def get_stances(self, battle, army, type):
        stances_def = []
        stances_off = []
        if type == 'land':
            for idx in range(3):
                s = battle.units[army][type][idx].get_stance()
                if s == 0:
                    stances_def.append(-1)
                    stances_off.append(0)
                else:
                    stances_def.append(0)
                    stances_off.append(-1)
            for _ in range(2):
                stances_def.append(0)
                stances_off.append(0)
        elif type == 'air':
            for _ in range(2):
                stances_def.append(0)
                stances_off.append(0)
            for idx in range(2):
                s = battle.units[army][type][idx].get_stance()
                if s == 0:
                    stances_def.append(-1)
                    stances_off.append(0)
                else:
                    stances_def.append(0)
                    stances_off.append(-1)
            stances_def.append(0)
            stances_off.append(0)
        elif type == 'sea':
            for idx in range(4):
                s = battle.units[army][type][idx].get_stance()
                if s == 0:
                    stances_def.append(-1)
                    stances_off.append(0)
                else:
                    stances_def.append(0)
                    stances_off.append(-1)
            stances_def.append(0)
            stances_off.append(0)
 
        print(f'Stances for {army} - {type} : {stances_def}{stances_off}')
        return [stances_def, stances_off]

    async def calc(self, btn):
        NO_UNIT = [0,0,0,0,0]
        ALL_UNITS = [-1,-1,-1,-1,-1]

        ARMIES = {}

        if self.battle_switch.value == False:
            for army in ['A', 'B']:
                ARMIES[army] = Army(units_land = self.get_land(self.land, army),
                            units_air =  self.get_air(self.land, army),
                            units_sea =  NO_UNIT,
                            options = self.config)

                ARMIES[army].apply_stance(stance_land = self.get_stances(self.land, army, 'land'),
                                            stance_air = self.get_stances(self.land, army, 'air'),
                                            stance_sea = [NO_UNIT,      NO_UNIT])
        else:
            for army in ['A', 'B']:
                ARMIES[army] = Army(units_land = NO_UNIT,
                            units_air =  self.get_air(self.sea, army),
                            units_sea =  self.get_sea(self.sea, army),
                            options = self.config)

                ARMIES[army].apply_stance(stance_land = [NO_UNIT,  NO_UNIT],
                                        stance_air = self.get_stances(self.sea, army, 'air'),
                                        stance_sea = self.get_stances(self.sea, army, 'sea'))

        #self.q_out.coro_put([CombatSystem.WarRoomV2,
        self.q_out.put([CombatSystem.WarRoomV2,
                                self.config,
                                ARMIES['A'],
                                ARMIES['B']])

        print('msg')
        #msg = await self.q_in.coro_get()

        #print('blubb')

        #if msg:
        #    self.tasks.task_done()
        #    print('finished simulation')
        #    self.battle_results.remove(self.results)
        #    self.results = toga.Label(msg, style=Pack(font_family='monospace'))
        #    self.battle_results.add(self.results)

    def join_on_exit(self, handle):
        print('fin')
        self.q_out.put('EXIT')
        self.sim_proc.join()
        sys.exit()

    def eval(self, app):
        while True:
            print('sleep')
            if self.q_in.empty():
                yield 1
            else:
                msg = self.q_in.get()
                print('finished simulation')
                self.battle_results.remove(self.results)
                self.results = toga.Label(msg, style=Pack(font_family='monospace'))
                self.battle_results.add(self.results)
                yield 1


def main():
    return WarRoomBattleSim()
