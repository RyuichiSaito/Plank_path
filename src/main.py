from PyQt5.QtWidgets import * 
from PyQt5 import QtCore, QtGui 
from PyQt5.QtGui import * 
from PyQt5.QtCore import *

import pandas as pd
import numpy as np
from Gcode import Gcode
import os, sys


# =====================================
#
# 以下GUIアプリ
#
# =====================================


class App(QWidget):

    def __init__(self, parent=None):
        super().__init__()

        self.initUI()

    # UI settings
    def initUI(self):
        self.resize(450, 350)
        self.move(300, 100) 
        self.widget_layout()

        self.setWindowTitle('Gawa Generator')
        self.show()

    def widget_layout(self):
        txt1 = QLabel(' 翼ファイル :')
        self.txtFolder = QLabel()
        self.txtFolder.setFrameStyle(QFrame.Box | QFrame.Plain)
        btnFolder = QPushButton(' 参照 ')
        btnFolder.clicked.connect(self.GetFile)

        txt2 = QLabel(' 翼弦長 (翼根) :')
        self.txt_Cordroot = QLineEdit()
        txt3 = QLabel(' 翼弦長 (翼端) :')
        self.txt_Cordend = QLineEdit()
        txt4 = QLabel(' プランク厚み :')
        self.txt_thin = QLineEdit()
        txt5 = QLabel(' 上面カット位置 :')
        self.txt_cutUp = QLineEdit()
        txt6 = QLabel(' 下面カット位置 :')
        self.txt_cutDown = QLineEdit()
        txt7 = QLabel(' 分割数 :')
        self.txt_divN = QLineEdit()
        txtmm1 = QLabel('[mm] ')
        txtmm2 = QLabel('[mm] ')
        txtmm3 = QLabel('[mm] ')
        txtper1 = QLabel('[%] ')
        txtper2 = QLabel('[%] ')
        txtt = QLabel(' [点] ')

        btnRun = QPushButton(' 実行 ')
        btnRun.clicked.connect(self.RunProgram)

        # ----------------
        # Setting layout
        # ----------------
        layout = QGridLayout()
        layout.setSpacing(15)

        layout.addWidget(txt1, 0,0)
        layout.addWidget(self.txtFolder, 0,1,1,3)
        layout.addWidget(btnFolder, 0,5)

        layout.addWidget(txt2,1,0)
        layout.addWidget(self.txt_Cordroot,1,1)
        layout.addWidget(txtmm1,1,3)
        layout.addWidget(txt3,1,4)
        layout.addWidget(self.txt_Cordend,1,5)
        layout.addWidget(txtmm2,1,6)

        layout.addWidget(txt5,2,0)
        layout.addWidget(self.txt_cutUp,2,1)
        layout.addWidget(txtper1,2,3)
        layout.addWidget(txt6,2,4)
        layout.addWidget(self.txt_cutDown,2,5)
        layout.addWidget(txtper2,2,6)

        layout.addWidget(txt4,3,0)
        layout.addWidget(self.txt_thin,3,1)
        layout.addWidget(txtmm3,3,3)
        layout.addWidget(txt7,3,4)
        layout.addWidget(self.txt_divN,3,5)
        layout.addWidget(txtt,3,6)

        layout.addWidget(btnRun, 4,5)

        self.setLayout(layout)

    def GetFile(self):
        # ディレクトリの選択
        self.path = QFileDialog.getOpenFileName(self,'Open file', os.getcwd())
        basename = os.path.basename(self.path[0])
        self.txtFolder.setText(basename)

    def RunProgram(self):
        path = self.txtFolder.text()
        coodRoot = float(self.txt_Cordroot.text())
        coodEnd = float(self.txt_Cordend.text())
        CutUp = 1-float(self.txt_cutUp.text())*0.01
        CutDown = 1-float(self.txt_cutDown.text())*0.01
        thin = float(self.txt_thin.text())
        divN = int(self.txt_divN.text())
        
        G = Gcode(path, thin=thin, CutUp=CutUp, CutDown=CutDown, interpN=divN)
        G.getWingData(coodRoot, coodEnd)
        G.Reshape()
        G.MakeGcode()
        G.Output('test')

def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    app = QApplication(sys.argv)
    ew = App()
    sys.exit(app.exec_())

    

if __name__ == '__main__':
    main()