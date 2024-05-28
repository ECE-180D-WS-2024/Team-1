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
        
        # Create a text node that displays main popup content
        self.popupTextNode = TextNode('popupTextNode')
        self.popupTextNode.setWordwrap(20)  # Set word wrap to fit text within a certain width
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

        # Text node that displays the current page number
        self.pageNumberNode = TextNode('pageNumberNode')
        self.pageNumberNode.setAlign(TextNode.ACenter)
        self.pageNumberNodePath = aspect2d.attachNewNode(self.pageNumberNode)
        self.pageNumberNodePath.setScale(0.07)
        self.pageNumberNodePath.setPos(0, 0, -0.6)  # Position the page number below the buttons
        
        # Initial update of text and buttons
        self.updateText()

    def updateText(self):
        # Set text based on current page
        self.popupTextNode.setText(self.pages[self.currentPage])
        # Show or hide buttons based on current page
        self.prevButton.show() if self.currentPage > 0 else self.prevButton.hide()
        self.nextButton.show() if self.currentPage < len(self.pages) - 1 else self.nextButton.hide()
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

app = MyApp()
app.run()