import pandas as pd
import numpy as np
from cutpath import Interpolate

class Gcode():
    def __init__(self,path,thin=3, CutUp=0.8, CutDown=0.9, interpN=500, deg=5):
        self.W = Interpolate(path,thin=thin, CutUp=CutUp, CutDown=CutDown, interpN=interpN, deg=deg)
        self.Xroot_ = None
        self.Yroot_ = None
        self.Xend_ = None
        self.Yend_ = None

    def getWingData(self, cordRoot, cordEnd):
        # Get root path
        self.W.ReadWing(cordRoot)
        self.W.Offset()
        self.W.CutOff()
        self.W.Rotate()

        self.Xroot = self.W.XCutPath
        self.Yroot = self.W.YCutPath

        # Ger root path
        self.W.ReadWing(cordEnd)
        self.W.Offset()
        self.W.CutOff()
        self.W.Rotate()

        self.Xend = self.W.XCutPath
        self.Yend = self.W.YCutPath

    def Reshape(self, bottom = 10):
        Ymin = min(min(self.Yroot), min(self.Yend)) - bottom
        self.Yroot -= Ymin
        self.Yend  -= Ymin

        Xmin = min(min(self.Xroot), min(self.Xend))
        self.Xroot -= Xmin
        self.Xend  -= Xmin


    def MakeGcode(self, feed=100, startHigh = 150):
        Xroot = list(self.Xroot)
        Xend = list(self.Xend)
        Yroot = list(self.Yroot)
        Yend = list(self.Yend)

        n = len(Xroot) + 3
        Com_G = ['G01' for _ in range(n)]
        Com_X = ['X' for _ in range(n)]
        Com_Y = ['Y' for _ in range(n)]
        Com_U = ['U' for _ in range(n)]
        Com_Z = ['Z' for _ in range(n)]
        Com_F = ['F   {}'.format(feed) for _ in range(n)]
        
        # 最初と最後の高さを調整する
        self.Xroot_ = [0, Xroot[0], *Xroot, Xroot[-1]]
        self.Xend_  = [0, Xend[0],  *Xend,  Xend[-1]]

        self.Yroot_ = [startHigh, startHigh, *Yroot, startHigh]
        self.Yend_  = [startHigh, startHigh, *Yend,  startHigh]

        # 出力の形に整える
        COM0 = [Com_G, Com_X,self.Xend_,  Com_Y,self.Yend_,  Com_U,self.Xroot_, Com_Z,self.Yroot_, Com_F] 
        COM1 = [Com_G, Com_X,self.Xroot_, Com_Y,self.Yroot_, Com_U,self.Xend_,  Com_Z,self.Yend_,  Com_F] 

        self.df0 = pd.DataFrame(COM0).T
        self.df1 = pd.DataFrame(COM1).T

    def Output(self, txtName,side=2):
        """
        side = 0 : 右翼
        side = 1 : 左翼
        side = 2 : 両翼
        """
        if side != 1:
            print(2)
            filename = txtName + 'R.txt'
            self.df0.to_csv(filename, sep=',', header=False, index=False)
            print(filename)

        if side != 0:
            filename = txtName + 'L.txt'
            self.df1.to_csv(filename, sep=',', header=False, index=False)
            print(filename)

# test
def main():
    path = 'dae21.d'
    G = Gcode(path)
    G.getWingData(800,700)
    G.Reshape()
    G.MakeGcode()
    G.Output('test')

if __name__ == '__main__':
    main()
