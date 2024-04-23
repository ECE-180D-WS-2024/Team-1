from PyQt5 import QtOpenGL
from PyQt5 import QtGui

from OpenGL import GL
from OpenGL import GLU
from OpenGL.arrays import vbo

import numpy as np

class GLWidget(QtOpenGL.QGLWidget):
    def __init__(self, parent=None):
        self.parent = parent
        QtOpenGL.QGLWidget.__init__(self, parent)

    def initializeGL(self):
        self.qglClearColor(QtGui.QColor(0, 0, 255))
        GL.glEnable(GL.GL_DEPTH_TEST)

        self.initGeometry()

        self.rotX = 0.0
        self.rotY = 0.0
        self.rotZ = 0.0

    def setRotX(self, val):
        self.rotX = val

    def setRotY(self, val):
        self.rotY = val

    def setRotZ(self, val):
        self.rotZ = val

    def resizeGL(self, width, height):
        GL.glViewport(0, 0, width, height)
        GL.glMatrixMode(GL.GL_PROJECTION)
        GL.glLoadIdentity()
        aspect = width / float(height)

        GLU.gluPerspective(45, aspect, 1.0, 100.0)
        GL.glMatrixMode(GL.GL_MODELVIEW)

    def paintGL(self):
        GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

        # push a new matrix to the matrix stack
        GL.glPushMatrix()
        
        # push some transformation matrices to the matrix stack
        GL.glTranslate(0.0, 0.0, -50.0)
        GL.glScale(20.0, 20.0, 20.0)
        GL.glRotate(self.rotX, 1.0, 0.0, 0.0)
        GL.glRotate(self.rotY, 0.0, 1.0, 0.0)
        GL.glRotate(self.rotZ, 0.0, 0.0, 1.0)
        GL.glTranslate(-0.5, -0.5, -0.5)

        # Render the cube 
        GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        GL.glEnableClientState(GL.GL_COLOR_ARRAY)

        # specify self.vertVBO is the array to point the vertex pointer to
        GL.glVertexPointer(3, GL.GL_FLOAT, 0, self.vertVBO)
        # specify self.colorVBO is the array to point the color pointer to
        GL.glColorPointer(3, GL.GL_FLOAT, 0, self.colorVBO)

        # render the faces using the face indices specified in cubeIdxArray
        GL.glDrawElements(GL.GL_QUADS, len(self.cubeIdxArray), GL.GL_UNSIGNED_INT, self.cubeIdxArray)

        GL.glDisableClientState(GL.GL_VERTEX_ARRAY)
        GL.glDisableClientState(GL.GL_COLOR_ARRAY)

        # leave only the identity transformation on the stack
        GL.glPopMatrix()

    def initGeometry(self):
        # create array for vertex positions of cube relative to origin (bottom left corner?)
        self.cubeVtxArray = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 1.0, 1.0],
                [0.0, 1.0, 1.0]
            ]
        )
        self.vertVBO = vbo.VBO(np.reshape(self.cubeVtxArray, (1, -1)).astype(np.float32))
        self.vertVBO.bind() # bind vbo to gpu

        # create array for colors at each vertex (formatted as r,g,b?)
        self.cubeClrArray = np.array(
            [
                [0.0, 0.0, 0.0],
                [1.0, 0.0, 0.0],
                [1.0, 1.0, 0.0],
                [0.0, 1.0, 0.0],
                [0.0, 0.0, 1.0],
                [1.0, 0.0, 1.0],
                [1.0, 1.0, 1.0],
                [0.0, 1.0, 1.0]
            ]
        )
        self.colorVBO = vbo.VBO(np.reshape(self.cubeClrArray, (1, -1)).astype(np.float32))
        self.colorVBO.bind()


        self.cubeIdxArray = np.array(
            [0, 1, 2, 3, \
             3, 2, 6, 7, \
             1, 0, 4, 5, \
             2, 1, 5, 6, \
             0, 3, 7, 4, \
             7, 6, 5, 4]
        )