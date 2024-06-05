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
        """
          Setup state
        """
        self.args = args
        self.secs_remain = 180
        self.timer_light_on = False
        self.running = True
        # Create a mutex for mistakes variable for compatibility with speech's multithreaded nature
        self.mistakes_lock = Condition()
        self.mistakes = 0
        self.max_mistakes = 3
        self.solved_puzzles = set()

        # Setup assets
        self.sound_beep = self.loader.loadSfx("assets/sound/beep.mp3")
        self.sound_explode = self.loader.loadSfx("assets/sound/explode.mp3")

        self.font_ssd = self.loader.loadFont("assets/font/dseg7.ttf")
        self.font_ssd.setPixelsPerUnit(60)

        # fourteen segment display font
        self.font_ftsg = self.loader.loadFont("assets/font/dseg14.ttf")
        self.font_ftsg.setPixelsPerUnit(60)

        # Menu initialization
        self.bomb = None
        self.death_dialog = None
        self.mistake_icons = None
        self.__start_menu()

        # Tutorial Initialization
        cm = CardMaker('popupBackground')
        cm.setFrame(-1, 1, -1, 1)
        self.popupBackground = aspect2d.attachNewNode(cm.generate())
        self.popupBackground.setColor(0, 0, 0, 1)
        self.popupBackground.setScale(1.25, 1.25, 0.75)
        self.popupBackground.setPos(0, 0, 0)
        self.popupBackground.setTransparency(TransparencyAttrib.MAlpha)

        # Tutorial toggle button
        self.popupButton = DirectButton(text=("Show Tutorial"), scale=0.075, pos=(1, 0, 0.8), command=self.togglePopup)
        
        # Text for each page
        self.currentPage = 0
        self.pages = [
            "Welcome to Bomb Goes Boom! This is a cooperative, 2-player game designed to foster teamwork!",
            "Before continuing, make sure that the manual player has the bomb defusal manual open.",
            "Also, note that the defusal player is not allowed to see the bomb manual, and the manual player is not allowed to see the bomb.",
            "Now, we'll go through examples so that you, the defusal player, know all the controls for our game.",
            "Firstly, to SWITCH BETWEEN GAMES, rotate the bomb to a different side. Doing this will also rotate the GUI to the corresponding side.",
            "Rotate this side up to activate the WIRE CUTTING GAME. In the WIRE CUTTING GAME, there are 6 buttons that correspond to the wires on the GUI. After working with your partner, push a button to cut a wire you think is correct.",
            "Rotate this side up to activate the SEQUENCING GAME. In the SEQUENCING GAME, there are 4 symbols displayed. After working with your partner, press the 4 buttons in the order you think is correct.",
            "Rotate this side up to activate the SIMON SAYS GAME. Also, make sure that the green side of the bomb is facing the defusing player's computer camera. ==>",
            "In the SIMON SAYS GAME, your goal is to move the green side of the bomb around the edges of the screen in a correct sequence. After working with your partner, slide the bomb in the order you think is correct.",
            "Rotate this side up to activate the LED TIMER GAME. In the LED TIMER GAME, your goal is to press the button at the right time. After working with your partner, press and release the button at times you think are correct.",
            "Rotate this side up to activate the BINARY SPEECH GAME. In the BINARY SPEECH GAME, a big-endian number is displayed on the GUI. After working with your partner, speak a code word into the mic that you think is correct.",
            "Once all 5 games are completed, the bomb will defuse automatically. If the bomb defuses before the timer ends, you win!"
        ]

        # Main tutorial text node
        self.popupTextNode = TextNode('popupTextNode')
        self.popupTextNode.setWordwrap(35)
        self.popupTextNode.setAlign(TextNode.ACenter)
        self.popupTextNodePath = aspect2d.attachNewNode(self.popupTextNode)
        self.popupTextNodePath.setScale(0.07)
        self.popupTextNodePath.setPos(0, 0, -0.4)
        
        # Navigation buttons
        self.prevButton = DirectButton(text=("Prev", "Prev", "Prev", "Prev"), scale=0.05,
                                       pos=(-0.3, 0, -0.7), command=self.prevPage)
        self.prevButton.setTransparency(True)
        
        self.nextButton = DirectButton(text=("Next", "Next", "Next", "Next"), scale=0.05,
                                       pos=(0.3, 0, -0.7), command=self.nextPage)
        self.nextButton.setTransparency(True)

        # Tutorial page number display
        self.pageNumberNode = TextNode('pageNumberNode')
        self.pageNumberNode.setAlign(TextNode.ACenter)
        self.pageNumberNodePath = aspect2d.attachNewNode(self.pageNumberNode)
        self.pageNumberNodePath.setScale(0.07)
        self.pageNumberNodePath.setPos(0, 0, -0.7)

        # Tutorial images
        self.tutorialImage1 = OnscreenImage(image='assets/images/bomb.png', pos=(0, 0, 0.2), scale=(0.5, 1, 0.5))
        self.tutorialImage1.setTransparency(TransparencyAttrib.MAlpha)
        self.tutorialImage1.hide()

        self.tutorialImage2 = OnscreenImage(image='assets/images/bomb.png', pos=(0.5, 0, 0.2), scale=(0.5, 1, 0.5))
        self.tutorialImage2.setTransparency(TransparencyAttrib.MAlpha)
        self.tutorialImage2.hide()

        self.max_double_image_width = 0.5
        self.max_double_image_height = 0.5
        self.max_single_image_width = 0.8
        self.max_single_image_height = 0.45

        # Tutorial videos
        self.tutorial_video_texture = None
        self.tutorial_video_card = None

        self.popupVisible = False
        self.hidePopup()

    def finalizeExit(self):
        self.running = False
        sys.exit()

    def __setup_game_over(self):
        self.death_dialog = DirectDialog(frameSize=(-0.7, 0.7, -0.7, 0.7),
                                         fadeScreen=1)
        self.death_dialog_title = DirectLabel(text="BOOOOOM!",
                                              scale=0.15,
                                              pos = (0, 0, 0.4),
                                              parent=self.death_dialog)
        self.death_dialog_subtitle = DirectLabel(text="You lose!",
                                              scale=0.1,
                                              pos = (0, 0, 0),
                                              parent=self.death_dialog)
        self.death_dialog_reset_btn = DirectButton(text="Play again",
                                                   scale=0.05,
                                                   pos = (0, 0, -0.4),
                                                   parent=self.death_dialog,
                                                   command=self.__start_menu,
                                                   frameSize=(-4, 4, -1, 1))
        
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
        def setup_num_display(disp_np: NodePath, puzzle_name: str, posX, posY, posZ, h, p ,r) -> NodePath:
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
            self.__start_menu()
    
    def is_solved(self, puzzle: Puzzle):
        return puzzle in self.solved_puzzles

    def __setup_controls(self):
        self.accept('heartbeat', self.set_time)

        self.accept(event.encode('orientation', Orientation.LOCALIZATION), localization.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.SPEECH), speech.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.WIRES), wires.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.SEQUENCING), sequence.focus, extraArgs=[self])
        self.accept(event.encode('orientation', Orientation.CLOCK), hold.focus, extraArgs=[self])

        self.accept(event.encode('sequence', Sequence.TOP_LEFT), sequence.press_btn, extraArgs=[self, (0, 0), (0.200018, 1.04975, 0.193841)])
        self.accept(event.encode('sequence', Sequence.TOP_RIGHT), sequence.press_btn, extraArgs=[self, (0, 1), (-0.199982, 1.04975, 0.193841)])
        self.accept(event.encode('sequence', Sequence.BOTTOM_LEFT), sequence.press_btn, extraArgs=[self, (1, 0), (0.200018, 1.04975, -0.206159)])
        self.accept(event.encode('sequence', Sequence.BOTTOM_RIGHT), sequence.press_btn, extraArgs=[self, (1, 1), (-0.199982, 1.04975, -0.206159)])

        self.accept(event.encode('rgb', RGB.PRESSED), hold.push_button, extraArgs=[self])
        self.accept(event.encode('rgb', RGB.NOT_PRESSED), hold.release_button, extraArgs=[self])

        self.accept(event.encode('wire', Wire.WIRE_1), wires.cut_wire, extraArgs=[self, 1])
        self.accept(event.encode('wire', Wire.WIRE_2), wires.cut_wire, extraArgs=[self, 2])
        self.accept(event.encode('wire', Wire.WIRE_3), wires.cut_wire, extraArgs=[self, 3])
        self.accept(event.encode('wire', Wire.WIRE_4), wires.cut_wire, extraArgs=[self, 4])
        self.accept(event.encode('wire', Wire.WIRE_5), wires.cut_wire, extraArgs=[self, 5])
        self.accept(event.encode('wire', Wire.WIRE_6), wires.cut_wire, extraArgs=[self, 6])

        if self.args.keyboard_input:
            for i in range(1, 7):
                self.accept(f'{i}', wires.cut_wire, extraArgs=[self, i])

            self.accept('q', localization.focus, extraArgs=[self])
            self.accept('w', speech.focus, extraArgs=[self])
            self.accept('e', wires.focus, extraArgs=[self])
            self.accept('a', sequence.focus, extraArgs=[self])
            self.accept('s', hold.focus, extraArgs=[self])

            self.accept('i', sequence.press_btn, extraArgs=[self, (0, 0)])
            self.accept('o', sequence.press_btn, extraArgs=[self, (0, 1)])
            self.accept('k', sequence.press_btn, extraArgs=[self, (1, 0)])
            self.accept('l', sequence.press_btn, extraArgs=[self, (1, 1)])

            self.accept('space', hold.push_button, extraArgs=[self])
            self.accept('space_up', hold.release_button, extraArgs=[self])

    def rotate_bomb_feet(self):
        self.bomb.hprInterval(0.25, (0, -90, 0)).start()
        self.focused = None
        pass

    def blink_colon(self, task: Task):
        curr_text = self.timer_text_node.getText()
        self.timer_text_node.setText(curr_text.replace(':', ' '))
        task.delayTime = 1
        return task.again

    def set_time(self, time):
        self.secs_remain = time
        if self.secs_remain == 0:
            self.explode_bomb()
        mins = self.secs_remain // 60
        secs = self.secs_remain - (mins * 60)
        mins_str = str(mins).zfill(2)
        secs_str = str(secs).zfill(2)
        self.timer_text_node.setText(f'{mins_str}:{secs_str}')
    
    def blink_timer_light(self, task: Task):
        if not self.timer_light_on:
            self.timer_sphere_np.setLight(self.timer_light_np)
            self.timer_light_on = True
            self.sound_beep.play()
            task.delayTime = 0.5
        else:
            self.timer_sphere_np.setLightOff(self.timer_light_np)
            self.timer_light_on = False
            task.delayTime = 0.5
        return task.again
    
    def start_game(self):
        self.death_dialog.hide()
        self.running = True
        self.taskMgr.add(self.blink_colon, "blink_colon", delay=0.5)
        self.taskMgr.add(self.blink_timer_light, "blink_light", delay=1)
        self.mistakes = 0
        self.solved_puzzles = set()
        for icon in self.mistake_icons:
            icon.hide()

        wires.generate_puzzle(self)
        sequence.generate_puzzle(self)
        localization.generate_puzzle()
        self.messenger.send('hw_reset')

    def explode_bomb(self):
        self.sound_explode.play()
        self.taskMgr.remove("blink_colon")
        self.taskMgr.remove("blink_light")
        self.death_dialog.show()
    
    # Tutorial methods
    #
    # Updates content at each page of tutorial
    def updateText(self):
        self.popupTextNode.setText(self.pages[self.currentPage])
        self.prevButton.show() if self.currentPage > 0 else self.prevButton.hide()
        self.nextButton.show() if self.currentPage < len(self.pages) - 1 else self.nextButton.hide()

        if self.currentPage < 4 or self.currentPage == 11:
            self.stopTutorialVideo()
            if self.currentPage == 0 or self.currentPage == 3:
                image_path1 = 'assets/images/bomb.png'
            elif self.currentPage == 1:
                image_path1 = 'assets/images/bomb_manual.png'
            elif self.currentPage == 2:
                image_path1 = 'assets/images/concept_refresher.png'
            elif self.currentPage == 11:
                image_path1 = 'assets/images/checkboxes.png'
            self.tutorialImage1.setImage(image_path1)
            self.tutorialImage1.setPos(0, 0, 0.2)
            self.adjust_image_aspect(self.tutorialImage1, image_path1, self.max_single_image_width, self.max_single_image_height)
            self.tutorialImage1.show()
            self.tutorialImage2.hide()
        elif self.currentPage == 4:
            self.tutorialImage1.hide()
            self.tutorialImage2.hide()
            self.playTutorialVideo('assets/videos/bomb_rotation.mp4')
        else:
            self.tutorialImage1.setPos(-0.5, 0, 0.2)
            image_path1 = ""
            image_path2 = ""

            if self.currentPage == 5:
                image_path1 = 'assets/images/bomb_wires.png'
                image_path2 = 'assets/images/gui_wires.png'
            elif self.currentPage == 6:
                image_path1 = 'assets/images/bomb_sequence.png'
                image_path2 = 'assets/images/gui_sequence.png'
            elif self.currentPage == 7:
                image_path1 = 'assets/images/bomb_localization1.png'
                image_path2 = 'assets/images/gui_localization.png'
            elif self.currentPage == 8:
                image_path1 = 'assets/images/bomb_localization2.png'
                image_path2 = 'assets/images/gui_localization.png'
            elif self.currentPage == 9:
                image_path1 = 'assets/images/bomb_arduino1.png'
                image_path2 = 'assets/images/gui_timer.png'
            elif self.currentPage == 10:
                image_path1 = 'assets/images/bomb_speech.png'
                image_path2 = 'assets/images/gui_speech.png'            

            if image_path1:
                self.tutorialImage1.setImage(image_path1)
                self.adjust_image_aspect(self.tutorialImage1, image_path1, self.max_double_image_width, self.max_double_image_height)
            if image_path2:
                self.tutorialImage2.setImage(image_path2)
                self.adjust_image_aspect(self.tutorialImage2, image_path2, self.max_double_image_width, self.max_double_image_height)

            self.tutorialImage1.show()
            self.tutorialImage2.show()
            self.stopTutorialVideo()

        self.updatePageNumber()

        
    def updatePageNumber(self):
        # Update page number text
        self.pageNumberNode.setText(f"{self.currentPage + 1}/{len(self.pages)}")

    def prevPage(self):
        # Move to previous page
        if self.currentPage > 0:
            self.currentPage -= 1
        self.updateText()
        
    def nextPage(self):
        # Move to next page
        if self.currentPage < len(self.pages) - 1:
            self.currentPage += 1
        self.updateText()
    
    def togglePopup(self):
        if self.popupVisible:
            self.hidePopup()
        else:
            self.showPopup()
    
    def showPopup(self):
        self.popupBackground.show()
        self.popupTextNodePath.show()
        self.prevButton.show()
        self.nextButton.show()
        self.pageNumberNodePath.show()
        self.updateText()
        self.popupVisible = True
        self.popupButton["text"] = "Hide Tutorial"

    def hidePopup(self):
        self.popupBackground.hide()
        self.popupTextNodePath.hide()
        self.prevButton.hide()
        self.nextButton.hide()
        self.pageNumberNodePath.hide()
        self.tutorialImage1.hide()
        self.tutorialImage2.hide()
        self.stopTutorialVideo()
        self.popupVisible = False
        self.popupButton["text"] = "Show Tutorial"
    
    # Method to play the tutorial video
    def playTutorialVideo(self, video_path):
        self.stopTutorialVideo()  # Stop any currently playing video

        # Load the movie texture
        self.tutorial_video_texture = MovieTexture("tutorial_video")
        success = self.tutorial_video_texture.read(video_path)

        if not success:
            print(f"Failed to load video: {video_path}")
            return

        cm = CardMaker('videoCard')
        cm.setFrame(-0.75, 0.75, -0.75, 0.75)
        self.tutorial_video_card = aspect2d.attachNewNode(cm.generate())
        self.tutorial_video_card.setTexture(self.tutorial_video_texture)
        self.tutorial_video_card.setPos(0.2, 0, 0.2)
        self.tutorial_video_card.setScale(0.69, 0.69, 0.69)
        self.tutorial_video_card.setTransparency(TransparencyAttrib.MAlpha)

        self.tutorial_video_texture.setLoop(True)
        self.tutorial_video_texture.play()

    # Method to stop the tutorial video
    def stopTutorialVideo(self):
        if self.tutorial_video_texture:
            self.tutorial_video_texture.stop()
        if self.tutorial_video_card:
            self.tutorial_video_card.removeNode()
        self.tutorial_video_texture = None
        self.tutorial_video_card = None

    # Method to adjust image aspect ratios
    def adjust_image_aspect(self, image, image_path, max_width, max_height):
        with Image.open(image_path) as img:
            width, height = img.size
        aspect_ratio = width / height

        if width > height:
            scale_width = min(max_width, max_height * aspect_ratio)
            scale_height = scale_width / aspect_ratio
        else:
            scale_height = min(max_height, max_width / aspect_ratio)
            scale_width = scale_height * aspect_ratio

        image.setScale(scale_width, 1, scale_height)
    
    # Initializes bomb on click
    def __play_handler(self):
        self.mistake_icons = []
        for i in range(self.max_mistakes):
            icon = OnscreenImage(image='assets/texture/ui/mistake.png', 
                                 pos = (-1.275 + i*0.11, 0, 0.95),
                                 scale = 0.04)
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

        # Setup post-processed components
        self.__setup_timer()
        self.__setup_num_displays()
        
        speech.init(self)
        sequence.init(self)
        wires.init(self)
        rgb_encoding = hold.init(self)

        if self.args.no_color_calibration:
            localization.init(self, [0,0,0])            
        else:
            localization.init(self, calibrate())

        # Create task chain for input handling
        # Allocate two threads: one thread is used to communicate with Arduino, 
        #   other thread is used to pass messages to the message bus
        ble.spawn(self, rgb_encoding)

        self.__setup_controls() 
        self.start_game()

        self.playButton.hide()

    # Creates menu on initialization and on game reset
    def __start_menu(self):
        # Play button initialization
        self.playButton = DirectButton(text=("Play"), scale=0.2, pos=(0, 0, 0), command=self.__play_handler)

        # Clear previous game content if it existed
        if self.bomb is not None:
            self.bomb.removeNode()
        if self.death_dialog is not None:
            self.death_dialog.hide()
        self.running = False
        self.mistakes = 0
        self.solved_puzzles = set()
        if self.mistake_icons is not None:
            for icon in self.mistake_icons:
                icon.hide()


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