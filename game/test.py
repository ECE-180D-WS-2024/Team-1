import sys
import asyncio
from argparse import ArgumentParser, Namespace
import os

from puzzles import localization, wires, sequence, speech, hold, Puzzle
from util.color_calibration import calibrate
import util.ble_receiver as ble
from util.Orientation import Orientation
from util.Sequence import Sequence
from util.RGB import RGB
from util.Wires import Wire
import util.event as event

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.DirectDialog import DirectDialog
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectButton import DirectButton
from direct.stdpy.threading import Condition

from panda3d.core import TextNode, PointLight, Spotlight, NodePath, TransparencyAttrib, CardMaker, MovieTexture
from PIL import Image

class BombApp(ShowBase):
    def __init__(self, args: Namespace):
        ShowBase.__init__(self)
        self.args = args
        self.secs_remain = 180
        self.timer_light_on = False
        self.running = True
        self.mistakes_lock = Condition()
        self.mistakes = 0
        self.max_mistakes = 3
        self.solved_puzzles = set()

        # Setup assets
        self.sound_beep = self.loader.loadSfx("assets/sound/beep.mp3")
        self.sound_explode = self.loader.loadSfx("assets/sound/explode.mp3")
        self.font_ssd = self.loader.loadFont("assets/font/dseg7.ttf")
        self.font_ssd.setPixelsPerUnit(60)
        self.font_ftsg = self.loader.loadFont("assets/font/dseg14.ttf")
        self.font_ftsg.setPixelsPerUnit(60)
        self.mistake_icons = []
        for i in range(self.max_mistakes):
            icon = OnscreenImage(image='assets/texture/ui/mistake.png', pos=(-1.275 + i*0.11, 0, 0.95), scale=0.04)
            icon.setTransparency(True)
            self.mistake_icons.append(icon)

        # Setup scene
        self.bomb = self.loader.loadModel("assets/model/bomb.bam")
        self.bomb.reparentTo(self.render)
        self.bomb.setPos(0, 5.5, 0)
        self.bomb.setHpr(0, 90, 0)
        self.spotlight = Spotlight("spotlight")
        self.spotlight_np = self.render.attachNewNode(self.spotlight)
        self.spotlight_np.setPos(-4, -4, 4)
        self.spotlight_np.lookAt(self.bomb)
        self.render.setLight(self.spotlight_np)
        self.render.setShaderAuto()

        self.__setup_game_over()
        self.__setup_timer()
        self.__setup_num_displays()

        speech.init(self)
        sequence.init(self)
        wires.init(self)
        rgb_encoding = hold.init(self)

        if args.no_color_calibration:
            localization.init(self, [0, 0, 0])
        else:
            localization.init(self, calibrate())

        ble.spawn(self, rgb_encoding)
        self.__setup_controls()
        self.__setup_menu()

        # Tutorial Initialization
        self.__setup_tutorial()

    def finalizeExit(self):
        self.running = False
        sys.exit()

    def __setup_game_over(self):
        self.death_dialog = DirectDialog(frameSize=(-0.7, 0.7, -0.7, 0.7), fadeScreen=1)
        self.death_dialog_title = DirectLabel(text="BOOOOOM!", scale=0.15, pos=(0, 0, 0.4), parent=self.death_dialog)
        self.death_dialog_subtitle = DirectLabel(text="You lose!", scale=0.1, pos=(0, 0, 0), parent=self.death_dialog)
        self.death_dialog_reset_btn = DirectButton(text="Play again", scale=0.05, pos=(0, 0, -0.4), parent=self.death_dialog, command=self.start_game, frameSize=(-4, 4, -1, 1))

    def __setup_timer(self):
        timer_node = self.bomb.find("**/timer")
        self.timer_text_node = TextNode(name="timer_text")
        self.timer_text_node.setText("03:00")
        self.timer_text_node.setFont(self.font_ssd)
        self.timer_text_node.setTextColor(255, 0, 0, 1)
        timer_text_bg_node = TextNode(name="timer_text_bg")
        timer_text_bg_node.setText("88:88")
        timer_text_bg_node.setFont(self.font_ssd)
        timer_text_bg_node.setTextColor(255, 0, 0, 0.2)

        timer_text_bg_np = timer_node.attachNewNode(timer_text_bg_node)
        timer_text_bg_np.setPos(-0.1, 0.225, 0.29)
        timer_text_bg_np.setScale(0.125, 0.125, 0.2)
        timer_text_bg_np.setHpr(0, 270, 90)

        self.timer_text_np = timer_node.attachNewNode(self.timer_text_node)
        self.timer_text_np.setPos(-0.1, 0.225, 0.3)
        self.timer_text_np.setScale(0.125, 0.125, 0.2)
        self.timer_text_np.setHpr(0, 270, 90)

        self.timer_sphere_np = self.bomb.find("**/timer.led")
        timer_light_node = PointLight("timer_light")
        timer_light_node.setColor((0, 255, 0, 0))
        self.timer_light_np = self.timer_sphere_np.attachNewNode(timer_light_node)
        self.timer_light_np.setPos(0, 0, 0.5)

    def __setup_num_displays(self):
        def setup_num_display(disp_np: NodePath, puzzle_name: str, posX, posY, posZ, h, p, r) -> NodePath:
            disp_text_bg_node = TextNode(f'{puzzle_name}.disp_bg')
            disp_text_bg_node.setText("~~")
            disp_text_bg_node.setTextColor(255, 255, 255, 0.2)
            disp_text_bg_node.setFont(self.font_ftsg)
            disp_text_bg_np = disp_np.attach_new_node(disp_text_bg_node)
            disp_text_bg_np.setPos(posX, posY, posZ)
            disp_text_bg_np.setHpr(h, p, r)
            disp_text_bg_np.setScale(0.125, 0.125, 0.2)

            disp_text_node = TextNode(f'{puzzle_name}.disp')
            disp_text_node.setTextColor(255, 255, 255, 1)
            disp_text_node.setFont(self.font_ftsg)
            disp_text_np = disp_np.attach_new_node(disp_text_node)
            disp_text_np.setPos(posX, posY, posZ + 0.1)
            disp_text_np.setHpr(h, p, r)
            disp_text_np.setScale(0.125, 0.125, 0.2)

            return disp_text_node

        hold_num_np = self.bomb.find("**/hold.num")
        seq_num_np = self.bomb.find("**/seq.num")
        ss_num_np = self.bomb.find("**/ss.num")
        wire_num_np = self.bomb.find("**/wire.num")

        seq_num_text = setup_num_display(seq_num_np, 'seq', 0.1, -0.1, -0.5, 0, 90, 180)
        wire_num_text = setup_num_display(wire_num_np, 'wire', 0.1, -0.1, 0.5, 180, -90, 90)
        ss_num_text = setup_num_display(ss_num_np, 'ss', 0.1, 0.1, -0.5, 0, 90, 270)
        hold_num_text = setup_num_display(hold_num_np, 'hold', -0.1, -0.1, 0.5, 90, 270, 90)

        self.num_texts = [seq_num_text, wire_num_text, ss_num_text, hold_num_text]

    def handle_mistake(self):
        if self.mistakes < 3:
            self.mistake_icons[self.mistakes].show()
            self.mistakes += 1
            self.mistakes_lock.notify_all()
        if self.mistakes == 3:
            self.explode_bomb()

    def solve_puzzle(self, puzzle: Puzzle):
        if puzzle != Puzzle.SPEECH:
            speech.display_puzzle_hex(self, puzzle)
        self.solved_puzzles.add(puzzle)

        if len(self.solved_puzzles) == 5:
            self.task_blink_colon.remove()
            self.task_decr_time.remove()
            self.task_blink_timer_light.remove()

    def is_solved(self, puzzle: Puzzle):
        return puzzle in self.solved_puzzles

    def __setup_controls(self):
        self.accept('heartbeat', self.set_time)
        self.accept(event.encode('orientation', Orientation.LOCALIZATION), localization.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.SPEECH), speech.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.WIRES), wires.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.SEQUENCING), sequence.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.CLOCK), hold.focus, extraArgs=[self])

        self.accept(event.encode('sequence', Sequence.TOP_LEFT), sequence.push, extraArgs=[self, Sequence.TOP_LEFT])
        self.accept(event.encode('sequence', Sequence.TOP_RIGHT), sequence.push, extraArgs=[self, Sequence.TOP_RIGHT])
        self.accept(event.encode('sequence', Sequence.BOTTOM_LEFT), sequence.push, extraArgs=[self, Sequence.BOTTOM_LEFT])
        self.accept(event.encode('sequence', Sequence.BOTTOM_RIGHT), sequence.push, extraArgs=[self, Sequence.BOTTOM_RIGHT])

        self.accept(event.ROTATE_BOMB_LEFT, self.rotate_bomb_feet, extraArgs=[90])
        self.accept(event.ROTATE_BOMB_RIGHT, self.rotate_bomb_feet, extraArgs=[-90])

        self.accept(event.encode('wire', Color.RED), wires.cut, extraArgs=[Color.RED])
        self.accept(event.encode('wire', Color.GREEN), wires.cut, extraArgs=[Color.GREEN])
        self.accept(event.encode('wire', Color.BLUE), wires.cut, extraArgs=[Color.BLUE])

    def __setup_menu(self):
        self.menu_frame = DirectFrame(frameSize=(-0.5, 0.5, -0.3, 0.3), frameColor=(0, 0, 0, 0.5))
        self.start_game_btn = DirectButton(text="Start Game", scale=0.1, pos=(0, 0, 0.1), parent=self.menu_frame, command=self.start_game)
        self.start_tutorial_btn = DirectButton(text="Tutorial", scale=0.1, pos=(0, 0, -0.1), parent=self.menu_frame, command=self.start_tutorial)

    def start_game(self):
        self.menu_frame.hide()
        self.mistakes = 0
        self.secs_remain = 180
        self.solved_puzzles = set()
        for icon in self.mistake_icons:
            icon.hide()
        taskMgr.add(self.task_blink_colon, "blink_colon")
        taskMgr.add(self.task_decr_time, "decr_time")
        taskMgr.add(self.task_blink_timer_light, "blink_timer_light")

    def start_tutorial(self):
        self.menu_frame.hide()
        self.__setup_tutorial()

    def __setup_tutorial(self):
        self.tutorial_frame = DirectFrame(frameSize=(-0.8, 0.8, -0.6, 0.6), frameColor=(0, 0, 0, 0.5))
        self.tutorial_title = DirectLabel(text="Tutorial", scale=0.1, pos=(0, 0, 0.5), parent=self.tutorial_frame)
        self.tutorial_text = DirectLabel(text="Welcome to the bomb defusal tutorial!", scale=0.05, pos=(0, 0, 0.3), parent=self.tutorial_frame)
        self.tutorial_image = OnscreenImage(image='assets/texture/ui/tutorial.png', pos=(0, 0, 0), scale=0.4, parent=self.tutorial_frame)
        self.tutorial_back_btn = DirectButton(text="Back", scale=0.1, pos=(-0.7, 0, -0.5), parent=self.tutorial_frame, command=self.__back_to_menu)

    def __back_to_menu(self):
        self.tutorial_frame.hide()
        self.menu_frame.show()

    def rotate_bomb_feet(self, angle):
        h, p, r = self.bomb.getHpr()
        self.bomb.setHpr(h + angle, p, r)

    def explode_bomb(self):
        self.sound_explode.play()
        self.death_dialog.show()

    def task_blink_colon(self, task):
        self.timer_light_on = not self.timer_light_on
        self.timer_text_node.setText(f'{self.secs_remain // 60:02}:{self.secs_remain % 60:02}' if self.timer_light_on else f'{self.secs_remain // 60:02} {self.secs_remain % 60:02}')
        task.delayTime = 0.5
        return task.again

    def task_decr_time(self, task):
        self.secs_remain -= 1
        self.timer_text_node.setText(f'{self.secs_remain // 60:02}:{self.secs_remain % 60:02}')
        if self.secs_remain <= 0:
            self.explode_bomb()
            return task.done
        task.delayTime = 1
        return task.again

    def task_blink_timer_light(self, task):
        self.timer_light_on = not self.timer_light_on
        self.timer_light_np.setColor((1, 0, 0, 1) if self.timer_light_on else (0, 0, 0, 1))
        task.delayTime = 0.5
        return task.again
    
def main():
    parser = ArgumentParser(prog="Bomb goes boom")
    parser.add_argument('--no-color-calibration', action='store_true')
    parser.add_argument('--no-noise-calibration', action='store_true')
    parser.add_argument('--keyboard-input', action='store_true')
    args = parser.parse_args()

    app = BombApp(args=args)
    app.run()

if __name__ == '__main__':
    main()