import toga
from toga.style import Pack
from toga.style.pack import ROW
from wrbattlesim.config import ROW_HEIGHT
import pdb
import numpy as np
import os
import io
from toga.platform import get_platform_factory
from PIL import Image
from PIL import ImageFont
from PIL import ImageDraw 
import pathlib
from matplotlib import font_manager

class Dice(toga.Box):
    def __init__(self, img):
        super().__init__(self, style=Pack(height=ROW_HEIGHT//2, width=ROW_HEIGHT))
        print('init')
        #self.factory = get_platform_factory()
         
        #self.img = plt.imread(os.path.join(self.factory.paths.app, img))
        self.img = Image.open(os.path.join(self.factory.paths.app, img))

        #self.img = np.zeros((12,12))
        #self.img_w_labels = toga.ImageView(toga.Image(img))
        self.image_view = toga.ImageView(style=Pack(flex=1))
        self.add(self.image_view)
        self.fontsize = None
        cwd = pathlib.Path(__file__)
        cwd = os.path.split(cwd)[0]
        self.fontset =  os.path.join(cwd, 'resources/Verdana.ttf')
        self.update(0)
    
    def update(self, num:int) -> None:
        img = self.img.copy()
        draw = ImageDraw.Draw(img)

        if self.fontsize is None:
            img_fraction = 0.95
            fontsize = 12
            font = ImageFont.truetype(self.fontset, fontsize)
            while font.getsize("20")[0] < img_fraction*img.size[0]:
                # iterate until the text size is just larger than the criteria
                fontsize += 1
                font = ImageFont.truetype(self.fontset, fontsize)
            fontsize -= 1
            self.fontsize = fontsize

        font = ImageFont.truetype(self.fontset, self.fontsize)
        # draw.text((x, y),"Sample Text",(r,g,b))
        draw.text((5, 7), f"{num}",(0,0,0),font=font)

        with io.BytesIO() as output:
            img.save(output, format="png")
            self.image_view.image = toga.images.Image(data=output.getvalue())
   

class DiceInfo(toga.Box):
    def __init__(self):
        super().__init__(self, style=Pack(direction=ROW))
        self.air    = Dice(f'resources{os.sep}air.png')
        self.ground = Dice(f'resources{os.sep}land.png')
        self.add(self.air)
        self.add(self.ground)
    
    def update(self, dice_air: int, dice_ground: int) -> None:
        self.air.update(dice_air)
        self.ground.update(dice_ground)


class DiceInfoTest(toga.App):
    def __init__(self):
        super(DiceInfoTest, self).__init__()
        pass

    def startup(self):
        self.di = Dice('./resources/air.png')
        self.main_window = toga.MainWindow(title=self.formal_name)
        self.btn = toga.Button('Plot', on_press=self.di.update(0))
        main_box = toga.Box(children=[self.btn, self.di])
        self.main_window.content = main_box
        self.main_window.show()

def main():
    return DiceInfoTest()