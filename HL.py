import os
import hou
from PySide2 import (QtWidgets, QtUiTools, QtGui, QtCore)
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *


class HDRILink(QtWidgets.QWidget):
    def __init__(self):
        super(HDRILink, self).__init__()

        self.scriptpath = os.path.dirname(os.path.realpath(__file__))

        pathfile = open(self.scriptpath + "/ARNO_HLtoH/Hdri_Path.txt")
        txtcon = pathfile.readline()
        pathfile.close()
        self.oripath = txtcon.replace('\\','/')
        self.proj = self.oripath
        self.transition = "0";

        #load UI file
        loader = QtUiTools.QUiLoader()
        self.ui = loader.load(self.scriptpath+"/UI.ui")

        #get UI elements
        self.setproj = self.ui.findChild(QtWidgets.QPushButton, "setproj")
        self.folderlist = self.ui.findChild(QtWidgets.QComboBox, "folderlist")
        self.scenelist = self.ui.findChild(QtWidgets.QListWidget, "scenelist")
        self.label = self.ui.findChild(QtWidgets.QLabel, "label_2")
        self.height = self.ui.findChild(QtWidgets.QSpinBox, "spinbox")


        # creat connections
        self.setproj.clicked.connect(self.setproject)
        self.folderlist.activated.connect(self.Refresh)
        self.folderlist.activated.connect(self.CreateInterface)
        self.height.valueChanged.connect(self.changeHeight)
        #layout
        mainLayout = QtWidgets.QVBoxLayout()
        mainLayout.addWidget(self.ui)

        #add widgets to layout
        self.setLayout(mainLayout)

        # creat widgets
        self.Refresh()
        self.CreateInterface()

        #set icon size
        self.scenelist.setIconSize(QSize(150,75))
        self.label.setMaximumHeight(150)
        #set height
        heightfile = open(self.scriptpath + "/ARNO_HLtoH/Height.txt")
        heightS = heightfile.readline()
        try:
            height = int(heightS)
        except ValueError:
            height = 500
        self.scenelist.setMaximumHeight(height)
        self.scenelist.setMinimumHeight(height)
        self.height.setValue(height)

        heightfile.close()

    def changeHeight(self,data):
        self.scenelist.setMaximumHeight(data)
        self.scenelist.setMinimumHeight(data)
        f = open(self.scriptpath + "/ARNO_HLtoH/Height.txt", "wt")
        f.write(str(data))
        f.close()

    def setproject(self):
        setpath = hou.ui.selectFile(title="Set Project",file_type=hou.fileType.Directory)
        newpath = os.path.dirname(setpath) +"/"

        if (newpath != "/"):
            self.proj = newpath
            f = open(self.scriptpath + "/ARNO_HLtoH/Hdri_Path.txt","wt")
            f.write(newpath)
            f.close()

        #print self.proj
        self.Refresh()
        self.CreateInterface()

    def Refresh(self):
        if self.proj != self.transition and self.proj !="":
            self.folderlist.clear()
            for folder in os.listdir(self.proj):
                self.folderlist.addItem(folder)

            self.transition = self.proj

        self.instexpath = self.proj + str(self.folderlist.currentText()) + "/Thumbnails/"
        self.texpath = self.proj + str(self.folderlist.currentText()) + "/HDRIs/"

        #print self.texpath

    def CreateInterface(self):
        self.scenelist.clear()

        try:
            for file in os.listdir(self.instexpath):
                if file.endswith('.jpg'):
                    fn = file.split(".")
                    del fn[-1]
                    name = ".".join(fn)
                    #add icon
                    instex0 = self.instexpath + file
                    jpg0 = QtGui.QPixmap(instex0).scaled(300, 150)
                    icon = QtGui.QIcon(jpg0)
                    item = QListWidgetItem(icon, "")
                    item.setText(name)
                    self.scenelist.addItem(item)

                    endfile = file

            instex1 = self.instexpath + endfile
            # print instex
            jpg1 = QtGui.QPixmap(instex1).scaled(500, 250)
            self.label.setPixmap(jpg1)
        except WindowsError:
            pass

        #connect list items to function
        self.scenelist.doubleClicked.connect(self.setTex)
        self.scenelist.clicked.connect(self.viewHdri)


    def viewHdri(self, item):
        texname = item.data()

        instex = self.instexpath + texname+".jpg"
        #print instex
        jpg = QtGui.QPixmap(instex).scaled(500, 250)
        self.label.setPixmap(jpg)

    def setTex(self,item):
        texname = item.data()

        for texture in os.listdir(self.texpath):
                j = texture.split(texname)
                if len(j)>=2:
                    texname = texture

        path = self.texpath + texname
        node = hou.selectedNodes()[0]
        gen = node.parm('env_map')
            
        if(gen == None):
            gen = node.parm('ar_light_color_texture')
 
        if (gen == None):
            gen = node.parm('A_FILENAME')
            gen.set(path)
            gen = node.parm('A_FILENAME2')
            gen.set(path)

        gen.set(path)
        
        #print "author:ARNO"
        #print "QQ:1245527422"