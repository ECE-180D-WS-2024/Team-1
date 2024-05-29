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
            "Game 1"
        ]
        
        # Create a text node that displays main popup content
        self.popupTextNode = TextNode('popupTextNode')
        self.popupTextNode.setWordwrap(20)  # Set word wrap to fit text within a certain width
        self.popupTextNode.setAlign(TextNode.ACenter)  # Center align the text
        self.popupTextNodePath = aspect2d.attachNewNode(self.popupTextNode)
        self.popupTextNodePath.setScale(0.07)  # Adjusted scale to fit text on screen
        self.popupTextNodePath.setPos(0, 0, -0.4)  # Center the text horizontally and position towards the bottom
        
        # Create buttons for navigation
        self.prevButton = DirectButton(text=("Prev", "Prev", "Prev", "Prev"), scale=0.05,
                                       pos=(-0.3, 0, -0.65), command=self.prevPage)
        self.prevButton.setTransparency(True)
        
        self.nextButton = DirectButton(text=("Next", "Next", "Next", "Next"), scale=0.05,
                                       pos=(0.3, 0, -0.65), command=self.nextPage)
        self.nextButton.setTransparency(True)

        # Text node that displays the current page number
        self.pageNumberNode = TextNode('pageNumberNode')
        self.pageNumberNode.setAlign(TextNode.ACenter)
        self.pageNumberNodePath = aspect2d.attachNewNode(self.pageNumberNode)
        self.pageNumberNodePath.setScale(0.07)
        self.pageNumberNodePath.setPos(0, 0, -0.7)  # Center the page number horizontally and position it below the buttons

        # Single image for tutorial pages, initialized with a placeholder image
        self.tutorialImage = OnscreenImage(image='tutorial_images/bomb.png', pos=(0, 0, 0.2), scale=(0.5, 1, 0.5))
        self.tutorialImage.setTransparency(TransparencyAttrib.MAlpha)
        self.tutorialImage.hide()

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
            self.tutorialImage.setImage('tutorial_images/bomb.png')
        else:
            self.tutorialImage.setImage('tutorial_images/mario.png')
        self.tutorialImage.show()
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
        self.tutorialImage.hide()
        self.popupVisible = False
        self.popupButton["text"] = "Show Tutorial"

app = MyApp()
app.run()
