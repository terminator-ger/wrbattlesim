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
from wrbattlesim.config import ROW_HEIGHT

import matplotlib
import matplotlib.pyplot as plt
import io

import threading
import functools
from queue import Queue
import matplotlib.gridspec as gridspec




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
        self.ARMIES = {}



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
        self.land = LandBattle(self) 
        self.sea = SeaBattle(self) 
        self.units_box = toga.Box(style=Pack(flex=0.8), children=[self.land])        

        # Calc btn
        self.calc_btn = toga.Button("Calculate",
                                 on_press=self.calc)


        self.spinner = toga.ProgressBar(max=100, running=False)
       
        self.ui_upper = toga.ScrollContainer(content=toga.Box(children=[self.ctrl,
                                                            self.units_box],
                                                    style=Pack(direction=COLUMN)),
                                                    horizontal = False,
                                                    vertical = True,
                                                    style=Pack(flex=0.5))        
               
        self.chart = toga.ImageView(style=Pack(flex=1))                                 

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
        self.update_armries()
        self.main_window.show()


    def bar_plot(self, ax, data, color, labels, y=0, alpha=None):
        data = np.append(data, 0)
        widths = np.asarray(data)
        starts = np.cumsum(data)
        starts = np.roll(starts, shift=1)
        starts[0] = 0
        starts[-1]=1
        xcenters = starts + widths / 2
        labels = np.append(labels, 0)

        if alpha is None:
            alpha = [1] * len(widths)

        alpha.append(0)
        color.append('black')
        #print(f"widths: {widths}")
        #print(f"starts: {starts}")
        for i in range(len(widths)):
            #print(widths[i])
            ax.barh(y=y,
                    width=widths[i], 
                    label=labels[i],
                    left=starts[i], 
                    height=1, 
                    alpha=alpha[i],
                    color=color[i])
            
            ax.barh(y=y,
                    width=widths[i],
                    label=labels[i],
                    left=starts[i], 
                    height=1, 
                    color='None',
                    edgecolor='black')


        for (x, c, l) in (zip(xcenters, widths, labels)):
            if c > 0:
                if not isinstance(l, str):
                    l = f"{int(l)}"
                if c > 0.1:
                    ax.text(x, y, 
                            f"{(c*100):.0f}% - {l}", 
                            ha='center', 
                            va='center',
                            fontsize='x-large')

        ax.get_xaxis().set_ticks([])
        ax.get_yaxis().set_ticks([])
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        ax.spines['bottom'].set_visible(False)
        ax.spines['left'].set_visible(False)
        #ax.set_aspect('auto', anchor='E')

        return ax

    def rescale_alpha(self, arr, rmin=0, rmax=1, tmin=0.5, tmax=1):
        return [(x-rmin)/(rmax-rmin) * (tmax-tmin) + tmin for x in arr]


    def draw_chart(self):

        if self.battle_switch.value == False:
            units_a = np.asarray(self.get_land(self.land, 'A'))
            units_a_air = np.asarray(self.get_air(self.land, 'A'))
            units_b = np.asarray(self.get_land(self.land, 'B'))
            units_b_air = np.asarray(self.get_air(self.land, 'B'))
        else:
            units_a = np.asarray(self.get_sea(self.sea, 'A'))
            units_a_air = np.asarray(self.get_air(self.sea, 'A'))
            units_b = np.asarray(self.get_sea(self.sea, 'B'))
            units_b_air = np.asarray(self.get_air(self.sea, 'B'))

        n_a = np.any(units_a>0).sum() 
        n_aair = np.any(units_a_air>0).sum()
        n_b = np.any(units_b>0).sum() 
        n_bair = np.any(units_b_air>0).sum()
        N = 1 if self.stats_a_ground is None else 1 + n_a + n_aair + n_b + n_bair
        #N = N + 2 + n_a + n_b + n_aair + n_bair if self.stats_a_ground is not None else N
        plt.close() 
        #fig, axs = plt.subplots(N)
        #my_dpi = self.main_window.dpi
        #width,height = self.main_window.size
        #plt.figure(figsize=(width/my_dpi, 800/my_dpi), dpi=my_dpi)
        plt.figure()
        #plt.figure(figsize = (16,4))
        gs1 = gridspec.GridSpec(N,1)
        gs1.update(wspace=0.05, hspace=0.05)
        plt_idx = 0 

        if self.win_loss_dist is not None:
            # using the normal matplotlib API
            #ax = figure.add_subplot(N,1,1)
            labels = ['A won', 'B won', 'Draw', 'MA']
            color  = ['red', 'blue', 'gray', 'black']
            #ax = axs[plt_idx] if not isinstance(axs, matplotlib.axes.Axes) else axs
            ax = plt.subplot(gs1[plt_idx])
            ax = self.bar_plot(ax, self.win_loss_dist, color, labels, y=0)

        if self.stats_a_ground is not None:
            color = ['#f1c615', '#4c74ed', '#3fa750', '#d72c32', 'white']
            idx_a = list(np.argwhere(units_a>0)[:,0])
            idx_b = list(np.argwhere(units_b>0)[:,0])
            idx_a_air = list(np.argwhere(units_a_air>0)[:,0])
            idx_b_air = list(np.argwhere(units_b_air>0)[:,0])
            axs_idx = 1

            for img_idx, i in enumerate(idx_a): 
                #ax = figure.add_subplot(N, 1, img_idx+3)
                stats = self.stats_a_ground[i]
                color_units = [color[i]] * len(stats[0])
                alpha = self.rescale_alpha([a for a in stats[1]])
                ax = plt.subplot(gs1[axs_idx])
                self.bar_plot(ax, stats[1], color_units, stats[0], y=img_idx, alpha=alpha)
                ax.set_facecolor('indianred')

            axs_idx = axs_idx + 1 if n_a > 0 else axs_idx
        
            for img_idx, i in enumerate(idx_a_air): 
                #ax = figure.add_subplot(N,1,img_idx+n_a+3)
                stats = self.stats_a_air[i]
                color_units = [color[i]] * len(stats[0])
                alpha = self.rescale_alpha([a for a in stats[1]])
                ax = plt.subplot(gs1[axs_idx])
                self.bar_plot(ax, stats[1], color_units, stats[0], y=img_idx, alpha=alpha)
                ax.set_facecolor('indianred')
            
            axs_idx = axs_idx + 1 if n_aair > 0 else axs_idx
 
            for img_idx, i in enumerate(idx_b): 
                #ax = figure.add_subplot(N,1,img_idx + 4 + n_a + n_aair)
                stats = self.stats_b_ground[i]
                color_units = [color[i]] * len(stats[0])
                alpha = self.rescale_alpha([a for a in stats[1]])
                ax = plt.subplot(gs1[axs_idx])
                self.bar_plot(ax, stats[1], color_units, stats[0], y=img_idx, alpha=alpha)
                ax.set_facecolor('cornflowerblue')
            
            axs_idx = axs_idx + 1 if n_b > 0 else axs_idx
            
            for img_idx, i in enumerate(idx_b_air): 
                #ax = figure.add_subplot(N,1,img_idx + 4 + n_a + n_aair + n_b)
                stats = self.stats_b_air[i]
                color_units = [color[i]] * len(stats[0])
                alpha = self.rescale_alpha([a for a in stats[1]])
                ax = plt.subplot(gs1[axs_idx])
                self.bar_plot(ax, stats[1], color_units, stats[0], y=img_idx, alpha=alpha)
                ax.set_facecolor('cornflowerblue')

        #fig.subplots_adjust(wspace=0, hspace=0)
        #fig.tight_layout()
        f = io.BytesIO()
        plt.savefig(f, format="png", bbox_inches='tight')#, transparent=True)
        self.chart.image = toga.images.Image(data=f.getvalue())


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
        #self.units_box_scroll.refresh_sublayouts()
        #self.units_box_scroll.refresh()
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
 
        #print(f'Stances for {army} - {type} : {stances_def}{stances_off}')
        return [stances_def, stances_off]

    def update_armries(self):
        NO_UNIT = [0,0,0,0,0]
        ALL_UNITS = [-1,-1,-1,-1,-1]

        self.is_calculating = True

        if self.battle_switch.value == False:
            for army in ['A', 'B']:
                self.ARMIES[army] = Army(units_land = self.get_land(self.land, army),
                            units_air =  self.get_air(self.land, army),
                            units_sea =  NO_UNIT,
                            options = self.config)

                self.ARMIES[army].apply_stance(stance_land = self.get_stances(self.land, army, 'land'),
                                            stance_air = self.get_stances(self.land, army, 'air'),
                                            stance_sea = [NO_UNIT,      NO_UNIT])
            self.land.info_red.update(self.ARMIES['A'].n_dice_air, 
                                         self.ARMIES['A'].n_dice_ground)
            self.land.info_blue.update(self.ARMIES['B'].n_dice_air, 
                                         self.ARMIES['B'].n_dice_ground)


        else:
            for army in ['A', 'B']:
                self.ARMIES[army] = Army(units_land = NO_UNIT,
                            units_air =  self.get_air(self.sea, army),
                            units_sea =  self.get_sea(self.sea, army),
                            options = self.config)

                self.ARMIES[army].apply_stance(stance_land = [NO_UNIT,  NO_UNIT],
                                        stance_air = self.get_stances(self.sea, army, 'air'),
                                        stance_sea = self.get_stances(self.sea, army, 'sea'))
            self.sea.info_red.update(self.ARMIES['A'].n_dice_air, 
                                         self.ARMIES['A'].n_dice_ground)
            self.sea.info_blue.update(self.ARMIES['B'].n_dice_air, 
                                         self.ARMIES['B'].n_dice_ground)




    def calc(self, btn):
        self.update_armries()
        #NO_UNIT = [0,0,0,0,0]
        #ALL_UNITS = [-1,-1,-1,-1,-1]

        #ARMIES = {}
        #self.is_calculating = True

        #if self.battle_switch.value == False:
        #    for army in ['A', 'B']:
        #        ARMIES[army] = Army(units_land = self.get_land(self.land, army),
        #                    units_air =  self.get_air(self.land, army),
        #                    units_sea =  NO_UNIT,
        #                    options = self.config)

        #        ARMIES[army].apply_stance(stance_land = self.get_stances(self.land, army, 'land'),
        #                                    stance_air = self.get_stances(self.land, army, 'air'),
        #                                    stance_sea = [NO_UNIT,      NO_UNIT])
        #else:
        #    for army in ['A', 'B']:
        #        ARMIES[army] = Army(units_land = NO_UNIT,
        #                    units_air =  self.get_air(self.sea, army),
        #                    units_sea =  self.get_sea(self.sea, army),
        #                    options = self.config)

        #        ARMIES[army].apply_stance(stance_land = [NO_UNIT,  NO_UNIT],
        #                                stance_air = self.get_stances(self.sea, army, 'air'),
        #                                stance_sea = self.get_stances(self.sea, army, 'sea'))

        unit_count_a = np.array([self.ARMIES['A'].units[type].sum() for type in ['land', 'sea', 'air']]).sum()
        unit_count_b = np.array([self.ARMIES['B'].units[type].sum() for type in ['land', 'sea', 'air']]).sum()

 
        self.spinner.start()
        self.units_a_ground = None
        self.units_b_ground = None
        self.units_a_air = None
        self.units_b_air = None
        self.win_loss_dist = None
        self.stats_a_air = None
        self.stats_b_air = None
        self.stats_a_ground = None
        self.stats_b_ground = None

        if unit_count_a > 0 and unit_count_b > 0:
            self.add_background_task(Simulate(self.ARMIES['A'], 
                                              self.ARMIES['B'],
                                              self.config,
                                              CombatSystem.WarRoomV2).run_cb) 


    def join_on_exit(self, handle):
        sys.exit()


    def battle_loop(self, app):
        while True:
            if self.todo is not None:
                ret = True
                while ret:
                    #print('new battle')
                    ARMIES = self.todo
                    ret, p = asyncio.run(self.sim.run_async(combat_system=CombatSystem.WarRoomV2,
                                        config=self.config,
                                        armyA=ARMIES['A'],
                                        armyB=ARMIES['B']))
                    #print(p)
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
