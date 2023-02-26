"""
Simulating battles for the board game War Room
"""
import asyncio
import sys

import toga
from toga.style import Pack
from toga.style.pack import COLUMN, ROW
from toga.constants import BLUE, RED
import toga_chart
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
from wrbattlesim.config import ROW_HEIGHT

import threading
import functools
from queue import Queue




class WarRoomBattleSim(toga.App):
    def __init__(self):
        super(WarRoomBattleSim, self).__init__()

        self.config = wr20_vaniilla_options
        self.todo = None

        self.sim = Simulate(army_a=None, army_b=None)

        self.on_exit = ()#self.join_on_exit
        self.is_calculating = False

        self.has_intermediate_results = False
        self.win_loss_dist = None
        self.has_final_results = False
        self.final_results = {}
        self.stats_a_ground = None
        self.stats_b_ground = None
        self.stats_a_air = None
        self.stats_b_air = None

        self.units_a_ground = None
        self.units_b_ground = None
        self.units_a_air = None
        self.units_b_air = None
        self.win_loss_dist = None



    def startup(self):
        """
        Construct and show the Toga application.

        Usually, you would add your application to a main content box.
        We then create a main window (with a name matching the app), and
        show the main window.
        """

        # Switches
        self.battle_switch = toga.widgets.switch.Switch('Land Battle',  
                                                        value=False, 
                                                        on_change=self.switch_battle_type)#,
                                                        #style=Pack(flex=0.5))

        self.batch_cap_switch = toga.widgets.switch.Switch('Batchcap Disabled',  
                                                        value=False, 
                                                        on_change=self.switch_batch_cap)#,
                                                        #style=Pack(flex=0.5))
        self.ctrl = toga.Box(style=Pack(direction=COLUMN), 
                             children = [self.battle_switch, self.batch_cap_switch])

        # Units
        self.land = LandBattle() 
        self.sea = SeaBattle() 
        self.units_box = toga.Box(style=Pack(flex=0.8), children=[self.land])        
        self.units_box_scroll = toga.Box(children=[self.units_box])

        # Calc btn
        self.calc_btn = toga.Button("Calculate",
                                 on_press=self.calc)
                                 #style=Pack(flex=0.1))


        self.spinner = toga.ProgressBar(max=100, running=False)



        self.results = toga.Label("Battle Results", style=Pack(font_family='monospace'))
        #self.battle_results = toga.ScrollContainer(content=self.results, 
                                                    #style=Pack(flex=0.5))

        self.ui_upper = toga.ScrollContainer(content=toga.Box(children=[self.ctrl,
                                                            self.units_box_scroll],
                                                    style=Pack(direction=COLUMN)),
                                                    horizontal = False,
                                                    vertical = True,
                                                    style=Pack(flex=0.5))
                
                                                
        self.chart = toga_chart.Chart(style=Pack(flex=1),
                                        on_draw=self.draw_chart) 

        self.battle_results = toga.ScrollContainer(content=self.chart, 
                                                    style=Pack(flex=0.5))
        self.battle_results.MIN_HEIGHT = 200
        self.ui_lower = toga.Box(style=Pack(direction=COLUMN, flex=0.5), 
                                    children=[self.spinner, 
                                                self.calc_btn, 
                                                self.battle_results])


        self.main_box = toga.Box(children=[self.ui_upper, self.ui_lower],
                                    style=Pack(direction=COLUMN))

        self.main_window = toga.MainWindow(title=self.formal_name)
        self.main_window.content = self.main_box
        self.main_window.show()

    def update_plot(self, app):
        while True:
            print('redraw')
            self.chart.redraw()
            yield 1

    def unit_plot(self, ax, units, units_air):
        color = ['#f1c615', '#4c74ed', '#3fa750', '#d72c32', 'white']
        for i, (x, y) in enumerate(units):
            if i < 4:
                ax.plot(x,y, color=color[i])
                d = np.zeros(len(y))
                ax.fill_between(x, y, 
                                where=y>=d, 
                                interpolate=True, 
                                color=color[i],
                                alpha=0.5)
        #ax.get_xaxis().set_ticks(np.arange(max(x), dtype=int))
            #if i < 4:
            #    for xx,yy in zip(x,y):
            #        print(f"{x} {y} {i}")
            #        ax.bar(xx,yy, color=color[i], width=0.2)

        #for i, (x, y) in enumerate(units_air):
        #    for xx,yy in zip(x,y):
        #        ax.bar(xx+3,yy, color=color[i], width=0.2)

        #ax.get_xaxis().set_ticks([])
        #ax.get_yaxis().set_ticks([])
        #ax.spines['top'].set_visible(False)
        #ax.spines['right'].set_visible(False)
        #ax.spines['bottom'].set_visible(False)
        #ax.spines['left'].set_visible(False)
    
    def bar_plot(self, ax, data, color, labels, alpha=None):
        widths = np.asarray(data)
        starts = np.cumsum(data)
        print(starts)
        starts = np.roll(starts, shift=1)
        starts[0] = 0
        xcenters = starts + widths / 2
        if alpha is None:
            alpha = [1] * len(widths)
        for i in range(len(widths)):
            ax.barh(y=0,
                    width=widths[i], 
                    label=labels[i],
                    left=starts[i], 
                    height=1, 
                    alpha=alpha[i],
                    color=color[i])
            ax.barh(y=0,
                    width=widths[i],
                    label=labels[i],
                    left=starts[i], 
                    height=1, 
                    color='None',
                    edgecolor='black')

            #for x in bar:
            #    x.set_edgecolor('green')
            #    x.set_linewidth(20)

        for (x, c, l) in (zip(xcenters, widths, labels)):
            if c > 0:
                if not isinstance(l, str):
                    l = f"{int(l)}"
                if c > 0.1:
                    ax.text(x, 0, 
                            f"{(c*100):.0f}% - {l}", 
                            ha='center', 
                            va='center')
        return ax


    def draw_chart(self, chart, figure, *args, **kwargs):
        units_a = np.asarray(self.get_land(self.land, 'A'))
        units_b = np.asarray(self.get_land(self.land, 'B'))
        n_a = (units_a>0).sum()
        n_b = (units_b>0).sum()
        N = 1
        N = N + 2 + n_a + n_b if self.stats_a_ground is not None else N

        if self.win_loss_dist is not None:
            # using the normal matplotlib API
            ax = figure.add_subplot(N,1,1)
            labels = ['A won', 'B won', 'Draw', 'MA']
            color  = ['red', 'blue', 'gray', 'black']

            ax = self.bar_plot(ax, self.win_loss_dist, color, labels)

            #ax.legend(ncol=len(labels), 
            #                bbox_to_anchor=(0.5, 1.1),
            #                #loc='left center', 
            #                fontsize='small')
            ax.get_xaxis().set_ticks([])
            ax.get_yaxis().set_ticks([])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['bottom'].set_visible(False)
            ax.spines['left'].set_visible(False)
        
        if self.stats_a_ground is not None:
            color = ['#f1c615', '#4c74ed', '#3fa750', '#d72c32', 'white']
            idx_a = list(np.argwhere(units_a>0)[:,0])
            idx_b = list(np.argwhere(units_b>0)[:,0])
            
            for img_idx, i in enumerate(idx_a): 
 
                ax = figure.add_subplot(N,1,img_idx+3)
                stats = self.stats_a_ground[i]
                
                color_units = [color[i]] * len(stats[0])
                alpha = [a for a in stats[1]]

                self.bar_plot(ax,
                            stats[1], 
                            color_units, 
                            stats[0],
                            alpha)
                ax.get_xaxis().set_ticks([])
                ax.get_yaxis().set_ticks([])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
        

            for img_idx, i in enumerate(idx_b): 
                ax = figure.add_subplot(N,1,img_idx + 4 + n_a)
                stats = self.stats_b_ground[i]
                
                color_units = [color[i]] * len(stats[0])
                alpha = [a for a in stats[1]]
                self.bar_plot(ax,
                            stats[1], 
                            color_units, 
                            stats[0], 
                            alpha)
                ax.get_xaxis().set_ticks([])
                ax.get_yaxis().set_ticks([])
                ax.spines['top'].set_visible(False)
                ax.spines['right'].set_visible(False)
                ax.spines['bottom'].set_visible(False)
                ax.spines['left'].set_visible(False)
        
          

        figure.tight_layout()


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
        self.units_box.refresh()
        self.ui_upper.refresh()
        self.ui_upper.refresh_sublayouts()
        self.units_box_scroll.refresh_sublayouts()
        self.units_box_scroll.refresh()
        self.main_box.refresh()
        self.main_box.refresh_sublayouts()
 
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

    def calc(self, btn):
        NO_UNIT = [0,0,0,0,0]
        ALL_UNITS = [-1,-1,-1,-1,-1]

        ARMIES = {}
        self.is_calculating = True

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

        unit_count_a = np.array([ARMIES['A'].units[type].sum() for type in ['land', 'sea', 'air']]).sum()
        unit_count_b = np.array([ARMIES['B'].units[type].sum() for type in ['land', 'sea', 'air']]).sum()

 
        self.spinner.start()
        self.units_a_ground = None
        self.units_b_ground = None
        self.units_a_air = None
        self.units_b_air = None
        self.win_loss_dist = None

        if unit_count_a > 0 and unit_count_b > 0:
            self.add_background_task(Simulate(ARMIES['A'], 
                                              ARMIES['B'],
                                              self.config,
                                              CombatSystem.WarRoomV2).run_cb) 


    def join_on_exit(self, handle):
        sys.exit()


    def battle_loop(self, app):
        while True:
            if self.todo is not None:
                ret = True
                while ret:
                    print('new battle')
                    ARMIES = self.todo
                    ret, p = asyncio.run(self.sim.run_async(combat_system=CombatSystem.WarRoomV2,
                                        config=self.config,
                                        armyA=ARMIES['A'],
                                        armyB=ARMIES['B']))
                    print(p)
                    self.spinner.value = p
                    if ret:
                        self.spinner.start()
                    else:
                        self.spinner.stop()

                    self.todo = None
                    yield 0.01
            yield 0.1



def main():
    return WarRoomBattleSim()
