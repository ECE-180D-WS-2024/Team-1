import sys
from argparse import ArgumentParser, Namespace

from puzzles import localization, wires, sequence, speech, hold, Puzzle
from util.color_calibration import calibrate
import util.ble_receiver as ble
from util.Orientation import Orientation
from util.Sequence import Sequence
from util.RGB import RGB
import util.event as event

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from direct.gui.OnscreenImage import OnscreenImage
from direct.stdpy.threading import Condition
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenImage import OnscreenImage

from panda3d.core import TextNode, PointLight, Spotlight, NodePath, TransparencyAttrib, CardMaker

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

        self.font_ssd = self.loader.loadFont("assets/font/dseg7.ttf")
        self.font_ssd.setPixelsPerUnit(60)

        # fourteen segment display font
        self.font_ftsg = self.loader.loadFont("assets/font/dseg14.ttf")
        self.font_ftsg.setPixelsPerUnit(60)

        self.mistake_icons = []
        for i in range(self.max_mistakes):
            icon = OnscreenImage(image='assets/texture/ui/mistake.png', 
                                 pos = (-1.275 + i*0.11, 0, 0.95),
                                 scale = 0.04)
            icon.setTransparency(True)
            icon.hide()
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

        # Setup post-processed components
        self.__setup_timer()
        self.__setup_num_displays()
        
        speech.init(self)
        sequence.init(self)
        wires.init(self)
        rgb_encoding = hold.init(self)

        if args.no_color_calibration:
            localization.init(self, [0,0,0])            
        else:
            localization.init(self, calibrate())

        # Create task chain for input handling
        # Allocate two threads: one thread is used to communicate with Arduino, 
        #   other thread is used to pass messages to the message bus
        ble.spawn(self, rgb_encoding)

        self.__setup_controls() 

        # Tutorial Initialization
        
        # Tutorial background
        cm = CardMaker('popupBackground')
        cm.setFrame(-1, 1, -1, 1)
        self.popupBackground = aspect2d.attachNewNode(cm.generate())
        self.popupBackground.setColor(0, 0, 0, 1)
        self.popupBackground.setScale(1.25, 1.25, 0.75)
        self.popupBackground.setPos(0, 0, 0)
        self.popupBackground.setTransparency(TransparencyAttrib.MAlpha)
        self.popupBackground.hide()

        # Tutorial toggle button
        self.popupButton = DirectButton(text=("Show Tutorial"), scale=0.1, pos=(0.8, 0, 0.8), command=self.togglePopup)
        
        # Text for each page
        self.currentPage = 0
        self.pages = [
            "Welcome to Bomb Goes Boom! This is a cooperative, 2-player game designed to foster teamwork!",
            "Before continuing, make sure that the manual player has the bomb defusal manual open.",
            "Now, we'll go through examples so that you, the defusal player, know how all the controls for our game.",
            "Before starting the game, place the bomb upright so the side with the timer is facing up. The GUI should show the corresponding page.",
            "To start the game, press the button that is underneath the timer. This should start the timer both on the bomb and on the GUI.",
            "Now that the timer has started, your are ready to play some games!",
            "In the WIRE CUTTING GAME, your goal is to cut the correct wire. Carefully observe the wires displayed on the GUI, then relay that information to your teammate. They will then give you instructions on the correct button to press.",
            "In the SEQUENCING GAME, your goal is enter four symbols in the correct order. Carefully observe what symbols appear on the GUI, and relay that information to your teammate. They will give you instructions on what order to press the buttons in.",
            "In the SIMON SAYS GAME, your goal is to move the bomb around the screen in a correct sequence. Observe what colors appear on the GUI, and relay that information to the manual player. They will give instructions on how to move the bomb.",
            "In the BINARY SPEECH GAME, your goal is speak a correct code word into the microphone. Relay the big-endian number, to the manual player, and they will give instructions on what to say in the microphone.",
            "After the main four games are completed, you can move on to the final game, the DEFUSAL GAME.",
            "In the DEFUSAL GAME, your goal is to defuse the bomb at the correct time. Get instructions from the manual player on when you are allowed to defuse the bomb.",
            "To SWITCH BETWEEN GAMES, rotate the bomb to a different side. Doing this will also rotate the GUI to the corresponding side.",
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
        self.tutorialImage1 = OnscreenImage(image='tutorial_images/bomb.png', pos=(0, 0, 0.2), scale=(0.5, 1, 0.5))
        self.tutorialImage1.setTransparency(TransparencyAttrib.MAlpha)
        self.tutorialImage1.hide()

        self.tutorialImage2 = OnscreenImage(image='tutorial_images/bomb.png', pos=(0.5, 0, 0.2), scale=(0.5, 1, 0.5))
        self.tutorialImage2.setTransparency(TransparencyAttrib.MAlpha)
        self.tutorialImage2.hide()

        self.popupVisible = False
        self.hidePopup() 

    def finalizeExit(self):
        self.running = False
        sys.exit()

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

        self.task_blink_colon = self.taskMgr.add(self.blink_colon, "blink_colon", delay=0.5)
        self.task_blink_timer_light = self.taskMgr.add(self.blink_timer_light, "blink_light", delay=1)

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

        self.accept(event.encode('sequence', Sequence.TOP_LEFT), sequence.press_btn, extraArgs=[self, (0, 0), (0.200018, 1.04975, 0.193841)])
        self.accept(event.encode('sequence', Sequence.TOP_RIGHT), sequence.press_btn, extraArgs=[self, (0, 1), (-0.199982, 1.04975, 0.193841)])
        self.accept(event.encode('sequence', Sequence.BOTTOM_LEFT), sequence.press_btn, extraArgs=[self, (1, 0), (0.200018, 1.04975, -0.206159)])
        self.accept(event.encode('sequence', Sequence.BOTTOM_RIGHT), sequence.press_btn, extraArgs=[self, (1, 1), (-0.199982, 1.04975, -0.206159)])

        self.accept(event.encode('rgb', RGB.PRESSED), hold.push_button, extraArgs=[self])
        self.accept(event.encode('rgb', RGB.NOT_PRESSED), hold.release_button, extraArgs=[self])

        for i in range(7):
            self.accept(event.encode('wires', i), wires.cut_wire, extraArgs=[self, i])

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
    
    def explode_bomb(self):
        self.finalizeExit()
    
    # Tutorial methods
    def updateText(self):
        # Set text based on current page
        self.popupTextNode.setText(self.pages[self.currentPage])
        # Show or hide buttons based on current page
        self.prevButton.show() if self.currentPage > 0 else self.prevButton.hide()
        self.nextButton.show() if self.currentPage < len(self.pages) - 1 else self.nextButton.hide()
        # Set image based on current page
        if self.currentPage < 3:
            self.tutorialImage1.setImage('tutorial_images/bomb.png')
            self.tutorialImage1.setPos(0, 0, 0.2)  # Center the image
            self.tutorialImage1.show()
            self.tutorialImage2.hide()
        else:
            self.tutorialImage1.setPos(-0.5, 0, 0.2)  # Move to the left
            if self.currentPage == 3 or self.currentPage == 10 or self.currentPage == 11 or self.currentPage == 12:
                self.tutorialImage1.setImage('tutorial_images/bomb_arduino1.png')
                self.tutorialImage2.setImage('tutorial_images/gui_timer.png')
            elif self.currentPage == 4:
                self.tutorialImage1.setImage('tutorial_images/bomb_start_button.png')
                self.tutorialImage2.setImage('tutorial_images/gui_timer.png')
            elif self.currentPage == 6:
                self.tutorialImage1.setImage('tutorial_images/bomb_wires.png')
                self.tutorialImage2.setImage('tutorial_images/gui_wires.png')
            elif self.currentPage == 7:
                self.tutorialImage1.setImage('tutorial_images/bomb_sequence.png')
                self.tutorialImage2.setImage('tutorial_images/gui_sequence.png')
            elif self.currentPage == 8:
                self.tutorialImage1.setImage('tutorial_images/bomb_localization.png')
                self.tutorialImage2.setImage('tutorial_images/gui_localization.png')
            elif self.currentPage == 9:
                self.tutorialImage1.setImage('tutorial_images/bomb_speech.png')
                self.tutorialImage2.setImage('tutorial_images/gui_speech.png')
                                    
            self.tutorialImage1.show()
            self.tutorialImage2.show()

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
        self.popupVisible = False
        self.popupButton["text"] = "Show Tutorial"

def main():
    parser = ArgumentParser(prog="Bomb goes boom")
    parser.add_argument('--no-color-calibration', action='store_true')
    parser.add_argument('--no-noise-calibration', action='store_true')
    args = parser.parse_args()

    app = BombApp(args=args)
    app.run()

if __name__ == '__main__':
    main()