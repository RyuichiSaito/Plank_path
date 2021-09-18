import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import shapely.geometry as shp
from scipy.interpolate import UnivariateSpline
import datetime,time
from scipy import interpolate

class CVTwing():
# ===================
#  convert dat file to ndarray for wingprofile
#
# ===================
    def __init__(self,path,thin=3):
        self.path = path
        self.thin = thin
        self.wing = None
        self.wingOffset = None

    def ReadWing(self,Cord):
        df = pd.read_table(self.path,names=['x','y'],delim_whitespace=True,skiprows=2)

        # ---------------------
        #　Pandas to numpy.array
        # 例 : d+03 →　10^3　
        # ---------------------
        wing = []
        for i in range (df.shape[0]):
            cur = []
            for j in range(df.shape[1]):
                wing_d = df.iloc[i][j]

                wingInt = float(wing_d[:-4])
                tenE = int(wing_d[-3:])
                wing_d = wingInt * Cord * 10**tenE

                cur.append(wing_d)
            wing.append(cur)
        
        self.wing = np.array(wing)

    def Offset(self):
        # =====================
        # 翼型をオフセットする
        # 
        # thin :　オフセット量
        #
        # =====================
        afpoly = shp.Polygon(self.wing)
        afpolyOff = afpoly.buffer(-self.thin)  # Inward offset

        # Turn polygon points into numpy arrays for plotting
        afpolypts = np.array(afpoly.exterior)
        self.wingOffset = np.array(afpolyOff.exterior)

class Interpolate(CVTwing):
    # =====================
    # 翼型をスプライン曲線で補完する
    # 
    # 翼型を必要な部分のみに変更する
    #
    # =====================
    def __init__(self, path, thin=3, CutUp=0.8, CutDown=0.9, interpN=500, deg=5):
        super().__init__(path,thin=thin)
        self.CutUp = CutUp
        self.CutDown = CutDown
        self.interpN = interpN
        self.WingOutside = None
        self.WingInside = None
        self.XCutPath = None
        self.YCutPath = None
        self.deg = deg

    def CutOff(self):

        def CutWing(wing, wingMax):
            # 回転行列
            t = np.deg2rad(2)
            R = np.array([[np.cos(t), -np.sin(t)],[np.sin(t),  np.cos(t)]])
            wing = np.dot(R, wing.T).T

            n = list(wing[:,0]).index(max(wing[:,0]))
            X_up, X_down = wing[:n+1,0], wing[n+1:,0]
            Y_up, Y_down = wing[:n+1,1], wing[n+1:,1]
            
            wingMaxTop = max(wing[:,0])
            fitUp = interpolate.interp1d(X_up, Y_up, kind="cubic")
            fitDown = interpolate.interp1d(X_down, Y_down, kind="cubic")
            
            Xup = np.linspace(wingMax*self.CutUp ,max(X_up), self.interpN)
            Xdown = np.linspace(wingMax*self.CutDown ,max(X_down), self.interpN)
            
            Yup = fitUp(Xup)
            Ydown = fitDown(Xdown)
            
            Xres = np.concatenate([Xup,Xdown[::-1]])
            Yres = np.concatenate([Yup,Ydown[::-1]])
            #print(len(Xres), len(Yres))
            return Xres, Yres

        wing = self.wing
        wingOffset = self.wingOffset
        wingMax = max(wing[:,0])

        X,Y  = CutWing(wing, wingMax)
        XI,YI = CutWing(wingOffset, wingMax)

        self.XCutPath = np.concatenate([X,XI[::-1]])
        self.YCutPath = np.concatenate([Y,YI[::-1]])

        self.WingOutside = [X,Y]
        self.WingInside = [XI,YI]

    def Rotate(self):
        rad = np.deg2rad(self.deg)
        R = np.array([[np.cos(rad), -np.sin(rad)],[np.sin(rad),  np.cos(rad)]])

        wing = R @ [self.XCutPath, self.YCutPath]
        
        self.XCutPath = wing[:,0]
        self.YCutPath = wing[:,1]

# test
def main():
    path = 'dae21.d'
    cord = 800
    W = Interpolate(path)
    W.ReadWing(cord)
    W.Offset()
    W.CutOff()
    print(len(W.XCutPath))

    W.ReadWing(700)
    W.Offset()
    W.CutOff()
    print(len(W.XCutPath))

if __name__ == '__main__':
    main()