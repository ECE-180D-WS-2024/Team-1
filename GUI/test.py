from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode
from direct.gui.DirectButton import DirectButton


class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        
        # Create a text node
        self.popupTextNode = TextNode('popupTextNode')
        self.popupTextNode.setText("Popup Text!")
        self.popupTextNode.setTextColor(1, 0, 0, 1)  # Red color
        self.popupTextNode.setAlign(TextNode.ACenter)  # Center align
        self.popupTextNode.setFrameColor(0, 0, 1, 1)  # White border color
        self.popupTextNode.setFrameLineWidth(2)  # Border width
        self.popupTextNode.setFrameAsMargin(0.2, 0.2, 0.1, 0.1)

        self.popupTextNode.setCardColor(1, 1, 0.5, 1)
        self.popupTextNode.setCardAsMargin(0.2, 0.2, 0.1, 0.1)
        self.popupTextNode.setCardDecal(True)
        
        # Create a text node path
        self.popupTextNodePath = aspect2d.attachNewNode(self.popupTextNode)
        self.popupTextNodePath.setScale(0.1)
        self.popupTextNodePath.setPos(0, 0, 0.5)  # Position the text above the center
        
        # Create a button to close the popup
        self.closeButton = DirectButton(text=("X", "X", "X", "X"), scale=0.05,
                                        pos=(0.35, 0, 0.45), command=self.removePopupText)
        self.closeButton.setTransparency(True)

    def removePopupText(self):
        self.popupTextNodePath.removeNode()  # Remove the text node path
        self.closeButton.destroy()  # Destroy the close button

app = MyApp()
app.run()