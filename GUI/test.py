from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode, TransparencyAttrib
from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenImage import OnscreenImage

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

        self.popupButton = DirectButton(text=("Show Tutorial"), scale=0.1, pos=(0.8, 0, 0.8), command=self.togglePopup)
        
        # Initialize page index
        self.currentPage = 0
        
        # Create text for each page
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
        
        # Create a text node that displays main popup content
        self.popupTextNode = TextNode('popupTextNode')
        self.popupTextNode.setWordwrap(35)  # Set word wrap to fit text within a certain width
        self.popupTextNode.setAlign(TextNode.ACenter)  # Center align the text
        self.popupTextNodePath = aspect2d.attachNewNode(self.popupTextNode)
        self.popupTextNodePath.setScale(0.07)  # Adjusted scale to fit text on screen
        self.popupTextNodePath.setPos(0, 0, -0.4)  # Center the text horizontally and position towards the bottom
        
        # Create buttons for navigation
        self.prevButton = DirectButton(text=("Prev", "Prev", "Prev", "Prev"), scale=0.05,
                                       pos=(-0.3, 0, -0.7), command=self.prevPage)
        self.prevButton.setTransparency(True)
        
        self.nextButton = DirectButton(text=("Next", "Next", "Next", "Next"), scale=0.05,
                                       pos=(0.3, 0, -0.7), command=self.nextPage)
        self.nextButton.setTransparency(True)

        # Text node that displays the current page number
        self.pageNumberNode = TextNode('pageNumberNode')
        self.pageNumberNode.setAlign(TextNode.ACenter)
        self.pageNumberNodePath = aspect2d.attachNewNode(self.pageNumberNode)
        self.pageNumberNodePath.setScale(0.07)
        self.pageNumberNodePath.setPos(0, 0, -0.7)  # Center the page number horizontally and position it below the buttons

        # Single image for tutorial pages, initialized with a placeholder image
        self.tutorialImage1 = OnscreenImage(image='tutorial_images/bomb.png', pos=(0, 0, 0.2), scale=(0.5, 1, 0.5))
        self.tutorialImage1.setTransparency(TransparencyAttrib.MAlpha)
        self.tutorialImage1.hide()

        self.tutorialImage2 = OnscreenImage(image='tutorial_images/mario.png', pos=(0.5, 0, 0.2), scale=(0.5, 1, 0.5))
        self.tutorialImage2.setTransparency(TransparencyAttrib.MAlpha)
        self.tutorialImage2.hide()

        self.popupVisible = False
        self.hidePopup()

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
        self.popupTextNodePath.show()
        self.prevButton.show()
        self.nextButton.show()
        self.pageNumberNodePath.show()
        self.updateText()
        self.popupVisible = True
        self.popupButton["text"] = "Hide Tutorial"

    def hidePopup(self):
        self.popupTextNodePath.hide()
        self.prevButton.hide()
        self.nextButton.hide()
        self.pageNumberNodePath.hide()
        self.tutorialImage1.hide()
        self.tutorialImage2.hide()
        self.popupVisible = False
        self.popupButton["text"] = "Show Tutorial"

app = MyApp()
app.run()