from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode
from direct.gui.DirectButton import DirectButton

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Initialize page index
        self.currentPage = 0
        
        # Create text for each page
        self.pages = [
            "Welcome to Bomb Goes Boom! This is a cooperative, 2-player game designed to foster teamwork!",
            "Before continuing, make sure that the manual player has the bomb defusal manual open.",
            "Now, we'll go through example games so you, the defusal player, know how all the controls for our game."
        ]
        
        # Create a text node
        self.popupTextNode = TextNode('popupTextNode')
        self.popupTextNode.setWordwrap(20)  # Set word wrap to fit text within a certain width
        self.updateText()
        
        # Create a text node path
        self.popupTextNodePath = aspect2d.attachNewNode(self.popupTextNode)
        self.popupTextNodePath.setScale(0.07)  # Adjusted scale to fit text on screen
        self.popupTextNodePath.setPos(-0.4, 0, 0)  # Position the text above the center
        
        # Create buttons for navigation
        self.prevButton = DirectButton(text=("Prev", "Prev", "Prev", "Prev"), scale=0.05,
                                       pos=(-0.35, 0, -0.5), command=self.prevPage)
        self.prevButton.setTransparency(True)
        
        self.nextButton = DirectButton(text=("Next", "Next", "Next", "Next"), scale=0.05,
                                       pos=(0.35, 0, -0.5), command=self.nextPage)
        self.nextButton.setTransparency(True)

    def updateText(self):
        # Set text based on current page
        self.popupTextNode.setText(self.pages[self.currentPage])
        
    def prevPage(self):
        # Move to previous page
        self.currentPage = (self.currentPage - 1) % len(self.pages)
        self.updateText()
        
    def nextPage(self):
        # Move to next page
        self.currentPage = (self.currentPage + 1) % len(self.pages)
        self.updateText()

app = MyApp()
app.run()