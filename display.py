#!/usr/bin/env python
# -*- coding: utf-8 -*-
 
import os
from cluster import getDomColor
from PySide import QtCore, QtGui

NUM_COLOR = 7
NUM_DIST = 7

lcolor = [ 0 for i in xrange(NUM_DIST) ]
listcolors = [ lcolor for i in xrange(NUM_COLOR) ]
cluster_status = [ 0 for i in xrange(NUM_COLOR) ]
dist_status = [ 0 for i in xrange(NUM_DIST) ]
dist = [1, 5, 10, 20, 30, 40, 50 ]
 
class ImageViewer( QtGui.QWidget ):
    def __init__(self):
        super(ImageViewer, self).__init__()
        self.setWindowTitle('Dominant Colors Viewer')
        
        self.model = QtGui.QComboBox()
        self.model.addItems(['Color models','RGB', 'CIE*Lab'])
        
        self.combo = QtGui.QComboBox()
        self.combo.addItems(['Number of clusters','1', '2', '3', '4', '5', '6', '7'])
        
        self.distbox = QtGui.QComboBox()
        self.distbox.addItems(['Min distance','1','5','10','20','30','40','50'])
        
        self.model.currentIndexChanged.connect( self.modChanged )
        self.combo.currentIndexChanged.connect( self.clsChanged )
        self.distbox.currentIndexChanged.connect( self.dstChanged )
        
        self.currentMod = 0
        self.currentCls = 0
        self.currentDst = 0
        
        self.imageLabel = QtGui.QLabel()
        self.imageLabel.setBackgroundRole(QtGui.QPalette.Base)
        self.button = QtGui.QPushButton('open')
        self.button.clicked.connect(self.open)
        self.palette = ColorPalette()
 
        layout = QtGui.QVBoxLayout()
        layout.addWidget( self.model )
        layout.addWidget( self.combo )
        layout.addWidget( self.distbox )
        layout.addWidget(self.imageLabel)
        layout.addWidget(self.button)
        layout.addWidget(self.palette)
        self.setLayout(layout)
        self.resize(450, 450)
 
    def open(self):
        (path, type) = QtGui.QFileDialog.getOpenFileName(self, "Open File")
        if path:
            self.path = path
            self.analysis()
    
    def modChanged( self, index ):
        self.currentMod = index
        self.analysis()
        
    def clsChanged( self, index ):
        self.currentCls = index
        self.analysis()
    
    def dstChanged( self, index ):
        self.currentDst = index
        self.analysis()
            
    # extract dominant colors        
    def analysis( self ):
        if not self.path:
            return
        image = QtGui.QImage(self.path)
        self.imageLabel.setPixmap(QtGui.QPixmap.fromImage(image).scaledToWidth(500))
        # get dominant colors palette
        
        modIdx = self.currentMod
        clsIdx = self.currentCls
        dstIdx = self.currentDst

        #print clsIdx, dstIdx, cluster_status[ clsIdx ], dist_status[ dstIdx ], listcolors[ clsIdx ][ dstIdx ]
        
        # if choose parameter again, not necessary to repeat calculation
        #if cluster_status[ clsIdx ] == 0 or dist_status[ dstIdx ] == 0:
        #    listcolors[ clsIdx ][ dstIdx ] = getDomColor( self.path, clsIdx + 1, dist[ dstIdx ] )
        #    if cluster_status[ clsIdx ] == 0:
        #        cluster_status[ clsIdx ] = 1 
        #    if dist_status[ dstIdx ] == 0:
        #        dist_status[ dstIdx ] = 1
        colors = []
        if clsIdx > 0 and dstIdx > 0 and modIdx > 0 :
            colors = getDomColor( self.path, clsIdx, dist[ dstIdx - 1], modIdx )
        self.palette.setColors( colors )
        
class ColorPalette( QtGui.QPushButton ):
    def __init__( self ):
        super( self.__class__, self).__init__()
        self.setSizePolicy( QtGui.QSizePolicy(QtGui.QSizePolicy.Fixed, 
                            QtGui.QSizePolicy.Fixed, 
                            QtGui.QSizePolicy.PushButton))
        self.colors = [(0, 0, 0)] * NUM_COLOR
        return
        
    def sizeHint( self ):
        return QtCore.QSize( 500, 100 )
    
    def setColors( self, colors ):
        self.colors = colors
        self.update()
        return
        
    def paintEvent( self, e ):
        pt = QtGui.QPainter()
        pt.begin( self )
        w = h = 60
        for i, color in enumerate( self.colors ):
            x = ( w + 5 ) * i + 3
            y = 10
            pt.setBrush( QtGui.QColor(*color) )
            pt.drawRect( x, y, w, h )
        
        pt.end()
        return
         
if __name__ == '__main__':
    import sys
    app = QtGui.QApplication(sys.argv)
    iv = ImageViewer()
    iv.show()
    sys.exit(app.exec_())