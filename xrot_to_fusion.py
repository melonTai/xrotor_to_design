#Author-fujita yuki
#Description-xrotor(プロペラ設計ソフト)のrestartfileから図面を自動生成するスクリプト。\nfusion360上のUIからパラメータを入力できるようにしている。

import adsk.core, adsk.fusion, traceback, math, os

_app = None
_ui  = None
_rowNumber = 0
_scale = 10
class PropDesign():
    def __init__(self):

        # リブのオフセット(バルサの場合、外皮の厚み分)[mm]
        self.rib_offset = 1
        # 設計ファイル読み込み(xrotorのrestartfile)
        self.filename = r"restartfile"
        # サブ翼型のdatファイルパス(ペラ根本、ペラ端で使用)
        self.sub_foil_path = r"subfoil.dat"
        # メイン翼型のdatファイルパス(ペラ中央で使用)
        self.main_foil_path = r"mainfoil.dat"
        # ハブ半径[mm]
        self.rib_start = 133
        # リブ間[mm](リブ厚を無視して)
        self.rib_interval = 30
        # 桁位置
        self.rib_center = 0.25
        # 後縁サポート材(書き換えなくて大丈夫)
        self.rib_rear = -50
        # 桁支持具の間隔(リブ何個ごとに作るか)
        self.keta_interval = 11
        # 混合比
        self.airfoil_mix_ratio = [100,95,90,85,80,75,70,65,60,55,50,45,40,35,30,25,20,15,10,10,20,30,40,50,60,70,80,90,100,100,100,100,100]
        # 混合するリブ番号
        self.airfoil_mix_number = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,30,31,32,33,34,35,36,37,38,39,40,41,42,43]
        # 桁のテーパー比
        self.tepa = 0.00772#0.00991453
        # 上のテーパー比のとき、桁を回転中心まで伸ばした時の回転中心における桁径
        self.hole_center = 16.60992#17.34837607
        #冶具
        # 桁穴中心の高さ[mm]
        self.keta_hei = 80
        # 冶具幅[mm]
        self.zig_wid = 160
        # フレーム高さ[mm]
        self.frame_hei = 80

        self.XDAT_U=[0.0002,0.0003,0.0004,0.0005,0.0006,0.0007,0.0008,0.0009,0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.52, 0.54, 0.56, 0.58, 0.6, 0.62, 0.64, 0.66, 0.68, 0.7, 0.72, 0.74, 0.76, 0.78, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 0.98,1.0]

        self.XDAT_D=[1.0, 0.98, 0.96, 0.94, 0.92, 0.9, 0.88, 0.86, 0.84, 0.82, 0.8, 0.78, 0.76, 0.74, 0.72, 0.7, 0.68, 0.66, 0.64, 0.62, 0.6, 0.58, 0.56, 0.54, 0.52, 0.5, 0.49, 0.48, 0.47, 0.46, 0.45, 0.44, 0.43, 0.42, 0.41, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.3, 0.29, 0.28, 0.27, 0.26, 0.25, 0.24, 0.23, 0.22, 0.21, 0.2, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01,0.009,0.008,0.007,0.006,0.005,0.004,0.003,0.002,0.001,0.0009,0.0008,0.0007,0.0006,0.0005,0.0004,0.0003,0.0002, 0.0]

        self.check = [True, False, False, False, True, True]

    def linear(self,xs, ys, xn):
        """
            内分する関数(xs昇順)

            Params
            ------
            xs : float list
                翼型のx座標(昇順)
            ys : float list
                翼型のy座標
            xn : float
                内分点

            Returns
            -------
            float
                xnで内分した時のyの値。内分不可の時は、ys[0]。
                また、翼型の前縁または後縁にあたるx座標が、引数に渡されたときは、0
        """
        if(xn == 0.0 or xn == 1.0):
            return 0.0
        for i in range(len(xs)-1):
            if(xs[i] < xn and xn < xs[i+1]):
                return ((xs[i+1] - xn) * ys[i] + (xn - xs[i]) * ys[i+1]) / (xs[i+1] - xs[i])
            if(xs[i] == xn):
                return ys[i]
        print('none data')
        return ys[0]


    def linear_reverse(self,xs, ys, xn):
        """
            内分する関数(xs降順)

            Params
            ------
            xs : float list
                翼型のx座標(降順)
            ys : float list
                翼型のy座標
            xn : float
                内分点

            Returns
            -------
            float
                xnで内分した時のyの値。内分不可の時は、ys[0]。
                また、翼型の前縁または後縁にあたるx座標が、引数に渡されたときは、0
        """
        if(xn == 0.0 or xn == 1.0):
            return 0.0
        for i in range(len(xs)-1):
            if(xs[i] > xn and xn > xs[i+1]):
                #線形補完(内分している)
                return ((xs[i+1] - xn) * ys[i] + (xn - xs[i]) * ys[i+1]) / (xs[i+1] - xs[i])
            if(xs[i] == xn):
                return ys[i]
        print('none data reverse')
        return ys[0]

    def shape_dat(self,datlist):
        """
            翼型の座標位置をXDAT_U、XDAT_Dに揃える関数

            Params
            ------
            datlist : list
                [[x1,y1],[x2,y2],...]

            Returns
            -------
            list
                [[XDAT_D[0],newy[0]],[XDAT_D[1],newy[1]],
                ...,[XDAT_D[-1],newy[m],[XDAT_U[0],newy[m+1]],[XDAT_U[1],newy[m+2]],
                ...,[XDAT_U[-1],newy[-1]]]
        """
        datlist_shaped = []
        datlist_x = [dat[0] for dat in datlist]
        datlist_y = [dat[1] for dat in datlist]
        for x in self.XDAT_D:

            datlist_shaped.append([x,self.linear_reverse(datlist_x, datlist_y,x)])
        for x in self.XDAT_U:
            datlist_shaped.append([x,self.linear(datlist_x, datlist_y,x)])
        return datlist_shaped

    def interpolate_dat(self,datlist_shaped_list, propotions):
        """
            翼型を混合する関数
            Params
            ------
            datlist_list : float list
                混合する翼型の座標リスト
                shape_datを通すこと
                [
                    [   # 翼型1の座標
                        [x11, y11],
                        [x12, y12],
                        ...
                    ],
                    [   # 翼型2の座標
                        [x21, y21],
                        [x22, y22],
                        ...
                    ],
                    ...
                ]

            propotions : float list
                各翼型の混合比率(百分率)
                例:
                    翼型1:翼型2:翼型3 = 0.2 : 0.3 : 0.5
                    で混合するとき引数は
                    [0.2, 0.3, 0.5]
                混合比率の合計は1になるよう注意

            Returns
            -------
                float list
                混合した翼型の座標
                [[newx1,newy1],[newx2,newy2],...]
        """
        datlist_new_y = [0]*len(datlist_shaped_list[0])
        datlist_new_x = [dat[0] for dat in datlist_shaped_list[0]]
        for datlist_shaped, p in zip(datlist_shaped_list, propotions):
            datlist_new_y = [dat[1]*p + dat_new_y for dat, dat_new_y in zip(datlist_shaped,datlist_new_y)]
        datlist_new = [[dat_new_x,dat_new_y] for dat_new_x, dat_new_y in zip(datlist_new_x, datlist_new_y)]

        return datlist_new

    def cross(self,a,b):
        """
        二次元ベクトルの外積の大きさを求める
        Params
        ------
        a,b : float list
            size must be 2
            [x,y]

        Returns
        -------
        float
            aとbの外積の大きさ
        """
        return a[0]*b[1] - a[1]*b[0]
    def inner_product(self,a,b):
        """
        二次元ベクトルの内積を行う関数
        Params
        ------
        a,b :float list
            size must be 2
            [x,y]

        Returns
        -------
        float
            aとbの内積
        """
        return a[0]*b[0] + a[1]*b[1]

    def isInner(self,ps,p):
        """
            pがpsで定められる座標群の内側にいるか判定する関数

            Params
            ------
            ps : float list
                [[x1,y1],[x2,y2],]
            p : float list
                [x,y]
            Returns
            -------
            bool
                内側にいたらTrue
                その他False
        """
        total_degree = 0
        for i in range(len(ps)-2):
            a = [ps[i][0] - p[0], ps[i][1] - p[1]]
            b = [ps[i+1][0] - p[0], ps[i+1][1] - p[1]]
            sin = self.cross(a,b)
            cos = self.inner_product(a,b)
            tan = math.atan2(sin,cos)
            total_degree += math.degrees(tan)
        return total_degree > 358 and total_degree < 362
    def isCross(self,p1, p2, q1, q2):
        """
        p1とp2を結ぶ線分とq1とq2を結ぶ線分が交差しているかを確認する関数

        Params
        ------
        p1, p2, q1, q2 : float list
            [x, y]

        Returns
        -------
        bool
            交差していたらTrue
            交差していなければFalse
        """
        ta = (q1[0] - q2[0]) * (p1[1] - q1[1]) + (q1[1] - q2[1]) * (q1[0] - p1[0])
        tb = (q1[0] - q2[0]) * (p2[1] - q1[1]) + (q1[1] - q2[1]) * (q1[0] - p2[0])
        tc = (p1[0] - p2[0]) * (q1[1] - p1[1]) + (p1[1] - p2[1]) * (p1[0] - q1[0])
        td = (p1[0] - p2[0]) * (q2[1] - p1[1]) + (p1[1] - p2[1]) * (p1[0] - q2[0])
        return tc * td < 0 and ta * tb < 0

    def getCross(self,p1, p2, p3, p4):
        """
        p1とp2を結ぶ線分とp3とp4を結ぶ線分の交点を得る関数

        Params
        ------
        p1, p2, p3, p4 : float list
            [x, y]

        Returns
        -------
        float list
            交点座標
            [x, y]
        """
        a = [p2[0] - p1[0], p2[1] - p1[1]]
        b = [p4[0] - p3[0], p4[1] - p3[1]]

        return [p1[0] + a[0] * self.cross(b,[p3[0]-p1[0],p3[1]-p1[1]])/self.cross(b, a) , p1[1] + a[1] * self.cross(b,[p3[0]-p1[0],p3[1]-p1[1]])/self.cross(b, a)]

    def removeCross(self,ps):
        """
        psに与えられた翼型から交差を除去する関数
        ※offsetをかける際に交差が起こるため

        Params
        ------
        ps : float list
            [[x1, y1],[x2, y2],...]
        Returns
        -------
        float list
            交差が除かれた翼型座標
            [[newx1, newy1],[newx2, newy2],...]
        """
        def _removeCross(ps):
            if len(ps) < 5:
                return ps
            length = len(ps)
            for i in range(3, length - 2):
                for j in range(0, i - 1):
                    if self.isCross(ps[i], ps[i+1], ps[j], ps[j+1]):
                        c = self.getCross(ps[i], ps[i+1], ps[j], ps[j+1])
                        if j < 20:
                            del ps[i:]
                            del ps[:j+1]
                            ps.append(c)
                        if len(ps)/3  < i and i < len(ps)*2/3:
                            del ps[j+1:i+1]
                            ps.insert(j+1,c)
                        return ps, True

            return ps, False
        result = _removeCross(ps)
        while result[1]:
            result = _removeCross(result[0])
        return result[0]

    def getCenterThickness(self,airfoil, c):#中心線のy座標を求める
        """
        airfoilに与えられた翼型の中心線についてcに与えられたx座標に対応するy座標を得る

        Params
        ------
        airfoil : float list
            翼型の座標
            [[x1,y1],[x2,y2],...]
        c : float
            知りたいx座標(0 < c < 1)
        Returns
        -------
        float
            cに対応するy座標
        """
        p = []
        for i in range(len(airfoil) - 2):
            if (airfoil[i][0] < c and c < airfoil[i+1][0]) or (airfoil[i+1][0] < c and c < airfoil[i][0]):
                m = (c - airfoil[i][0]) / (airfoil[i+1][0] - airfoil[i][0])
                p.append(airfoil[i][1] * (1 - m) + airfoil[i+1][1] * m)
            elif (airfoil[i][0] == c):
                p.append(airfoil[i][1])
        if len(p) == 2:
            return (p[0] + p[1]) / 2.0
        else:
            return 0

    def isDepressed(self,c, p, v1, v2):
        v = [v2[0]-v1[0],v2[1]-v1[1]]
        d1 = math.sqrt((c[0]-p[0])**2 + (c[1]-p[1])**2)
        d2 = math.sqrt((c[0]-(p[0]+v[0]))**2 + (c[1]-(p[1]+v[1]))**2)
        if d1 > d2:
            return True
        else:
            return False

    def getFromY(self,ps, ty):
        """
        psに与えられた座標群について、tyに与えられるy座標から対応するx座標を得る関数

        Params
        ------
        ps : float list
            翼型座標
            [[x1, y1], [x2, y2], ...]
        ty : float
            知りたいy座標

        Returns
        -------
        float
            tyに対応するx座標
        """
        p = []
        for i in range(len(ps) - 1):
            if (ps[i][1] < ty and ty < ps[i+1][1]) or (ps[i+1][1] < ty and ty < ps[i][1]):
                m = (ty - ps[i][1]) / (ps[i+1][1] - ps[i][1])
                p.append([ps[i][0] * (1 - m) + ps[i+1][0] * m, ps[i][1] * (1 - m) + ps[i+1][1] * m])
            elif ps[i][1] == ty:
                p.append(ps[i][0],ps[i][1])
        return p

    def getMaxY(self,ps):
        """
        psに与えられる座標群の中から最も大きなy座標を求める関数

        Params
        ------
        ps : float list
            座標群
            [[x1, y1],[x2, y2],...]

        Returns
        -------
        float
            最も大きなy座標
        """
        m = ps[0][1]
        for p in ps:
            if m < p[1]:
                m = p[1]
        return m

    def getMinY(self,ps):
        """
        psに与えられる座標群の中から最も大きなy座標を求める関数

        Params
        ------
        ps : float list
            座標群
            [[x1, y1],[x2, y2],...]

        Returns
        -------
        float
            最も大きなy座標
        """
        m = ps[0][1]
        for p in ps:
            if m > p[1]:
                m = p[1]
        return m

    def delete_out_dat(self,pb,pa):
        """
        paの座標群のからpbより外側にはみ出している座標を取り除く関数
        Params
        ------
        pb,pa : float list
            [[x1,y1],[x2,y2],...]

        Returns
        -------
        float
            はみ出した座標が取り除かれた座標群
        """
        def _delete_out_dat(pb,pa):
            for i in range(len(pa)):
                if self.isInner(pb, pa[i]) == False:
                    del pa[i]
                    return pa, True
            return pa, False
        result = _delete_out_dat(pb,pa)
        while result[1]:
            result = _delete_out_dat(pb,result[0])
        return result[0]

    def delete_in_dat(self,pb,pa):
        """
        paの座標群からpbより内側の座標を取り除く関数
        Params
        ------
        pb,pa : float list
            [[x1,y1],[x2,y2],...]

        Returns
        -------
        float
            内側の座標が取り除かれた座標群
        """
        def _delete_in_dat(pb,pa):
            for i in range(len(pa)):
                if self.isInner(pb, pa[i]):
                    del pa[i]
                    return pa, True
            return pa, False
        result = _delete_in_dat(pb,pa)
        while result[1]:
            result = _delete_in_dat(pb,result[0])
        return result[0]

    def offsetPoly(self,ps, offset):
        """
        psに与えられた座標から形成される多角形をoffset[mm]に指定された値だけ内側にオフセットをかける関数

        Params
        ------
        ps : float list
            座標群
            [[x1, y1],[x2, y2],...]
        offset : float
            オフセットの大きさ
            単位[mm]

        Returns
        float list
            オフセットがかけられた座標群
        """
        v = []
        for i in range(1, len(ps)):
            kx = ps[i-1][0] - ps[i][0]
            ky = ps[i-1][1] - ps[i][1]
            if kx == 0 and ky == 0:
                continue
            k = 1.0 / math.sqrt(kx**2 + ky**2)
            v.append([kx * k, ky * k])
        r = []

        for i in range(len(v)-2, -2, -1):
            if (v[i+1][0]*v[i][1]-v[i+1][1]*v[i][0]) == 0:
                if v[i][0] < 0:
                    r.append([offset*(v[i][0]*math.cos(math.pi/2) - v[i][1]*math.sin(math.pi/2))+ps[i][0],\
                    offset*(v[i][0]*math.sin(math.pi/2) + math.cos(math.pi/2))+ps[i][1]])
                else:
                    r.append([-offset*(v[i][0]*math.cos(math.pi/2) - v[i][1]*math.sin(math.pi/2))+ps[i][0],\
                    -offset*(v[i][0]*math.sin(math.pi/2) + math.cos(math.pi/2))+ps[i][1]])
            else:
                k = offset / (v[i+1][0]*v[i][1] - v[i+1][1]*v[i][0])
                newpoint = [(v[i+1][0] - v[i][0]) * k + ps[i][0], (v[i+1][1] - v[i][1]) * k + ps[i][1]]
                r.append(newpoint)
        if offset > 0:
            return self.removeCross(r)
        else:
            return r

    def set_scale(self,ps,scale):
        return [[p[0] / scale, p[1] / scale] for p in ps]

    def build(self):
        global _app, _ui, _scale

        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        doc = _app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
        design = _app.activeProduct

        # Get the root component of the active design.
        rootComp = design.rootComponent

        # Set styles of progress dialog.
        progressDialog = _ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True

        f=open(self.filename)
        fd = f.read()
        f.close()
        lines = fd.split('\n')
        blade_radius = 1000 * float(lines[5].split()[0])# 半径を設計ファイルから取得
        #print("blade_radius",blade_radius)
        design_data_r = []
        design_data_c = []
        design_data_rot = []
        skip = 9 + int(lines[9].split()[0])*10 + 6
        for line in lines[skip:]:
            d = line.split()
            if(len(d) == 4):
                design_data_r.append(float(d[0]) * blade_radius)
                design_data_c.append(float(d[1]) * blade_radius)
                design_data_rot.append(float(d[2])*math.pi/180)

        f=open(self.sub_foil_path)
        ad = f.read()
        f.close()
        lines = ad.split('\n')
        _sub_foil = []
        for line in lines[1:]:
            d = line.split()
            if(len(d) == 2):
                _sub_foil.append([float(d[0]), float(d[1])])
        sub_foil = self.shape_dat(_sub_foil)

        f=open(self.main_foil_path)
        ad = f.read()
        f.close()
        lines = ad.split('\n')
        _main_foil = []
        for line in lines[1:]:
            d = line.split()
            if(len(d) == 2):
                _main_foil.append([float(d[0]), float(d[1])])
        main_foil = self.shape_dat(_main_foil)

        output_rib_data = ""
        x = self.rib_start
        rot_offset = (-design_data_rot[0] - design_data_rot[-1] + math.pi) / 2
        rib_number = 0
        last_rearR = -1
        last_rearL = -1

        # Show dialog
        progressDialog.show('Progress Dialog', 'Percentage: %p, Current Value: %v, Total steps: %m', 0, int((blade_radius-self.rib_start)/self.rib_interval), 1)

        line_rib_collections = []
        line_rib_hole_collections = []
        line_rib_leadingmarker_collections = []
        line_jig_collections = []
        line_rear1_collections = []
        line_rear2_collections = []
        line_beamsup_collections = []
        line_tenon_collections = []
        line_mortise_collections = []
        sketch_rib_collections = []
        sketch_rib_hole_collections = []
        sketch_rib_leadingmarker_collections = []
        sketch_jig_collections = []
        sketch_rear1_collections = []
        sketch_rear2_collections = []
        sketch_beamsup_collections = []
        sketch_tenon_collections = []
        sketch_mortise_collections = []


        while x < blade_radius:
            # If progress dialog is cancelled, stop drawing.
            if progressDialog.wasCancelled:
                break
            # chord
            cmod = self.linear(design_data_r, design_data_c, x)
            # pitch
            rot = -self.linear(design_data_r, design_data_rot, x) - rot_offset
            # beam hole
            hole = self.hole_center-self.tepa*x

            # interpolate airfoil
            airfoil_data = []
            if rib_number in self.airfoil_mix_number:
                mix = self.airfoil_mix_ratio[self.airfoil_mix_number.index(rib_number)] / 100
            else:
                mix = 0
            #print(mix)
            #mix = 0
            airfoil_data = self.interpolate_dat([sub_foil,main_foil],[mix,1-mix])
            rib_center_camber = self.getCenterThickness(airfoil_data, self.rib_center)

            # rotate and expand airfoil
            airfoil_poly = []
            rear_airfoil_poly = []
            #print(self.rib_center)
            for p in airfoil_data:
                px = (p[0] - self.rib_center) * cmod
                py = (p[1] - rib_center_camber) * cmod
                nx = px * math.cos(rot) - py * math.sin(rot) + x
                ny = px * math.sin(rot) + py * math.cos(rot)
                airfoil_poly.append([nx, ny])

            # apply offset
            _rib_poly = self.offsetPoly(airfoil_poly, self.rib_offset)
            rib_poly = airfoil_poly

            # delete illegal point
            rib_poly = self.delete_out_dat(airfoil_poly, _rib_poly)

            # scale
            rib_poly_cm = self.set_scale(rib_poly, _scale)

            if self.check[0]:
                # draw rib
                sketch_rib_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                sketch_rib = sketch_rib_collections[-1]
                sketch_rib.name = 'rib{}'.format(rib_number)
                line_rib_collections.append(sketch_rib.sketchCurves.sketchLines)
                line_rib_collection = line_rib_collections[-1]

                line = line_rib_collection.addByTwoPoints(\
                    adsk.core.Point3D.create(rib_poly_cm[0][0], rib_poly_cm[0][1], 0), \
                    adsk.core.Point3D.create(rib_poly_cm[1][0], rib_poly_cm[1][1], 0)\
                )
                for p in rib_poly_cm[2:]:
                    line = line_rib_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(p[0], p[1], 0)\
                    )
                line = line_rib_collection.addByTwoPoints(\
                    line.endSketchPoint,\
                    adsk.core.Point3D.create(rib_poly_cm[0][0], rib_poly_cm[0][1], 0)\
                )
                """
                rib_curves = sketch_rib.findConnectedCurves(line)
                rib_offsetted = sketch_rib.offset(rib_curves, adsk.core.Point3D.create(x / _scale, 0, 0), self.rib_offset / _scale)
                design = adsk.fusion.Design.cast(_app.activeProduct)
                #entities = adsk.core.ObjectCollection.create()
                #for line in line_rib_collection:
                #    entities.add(line)
                design.deleteEntities(rib_curves)
                """

                # beam hole
                sketch_rib_hole_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                sketch_rib_hole = sketch_rib_hole_collections[-1]
                sketch_rib_hole.name = 'rib hole{}'.format(rib_number)
                circles = sketch_rib_hole.sketchCurves.sketchCircles
                circle = circles.addByCenterRadius(adsk.core.Point3D.create(x/_scale, 0, 0), hole/(_scale*2))
                # leading edge marker
                sketch_rib_leadingmarker_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                sketch_rib_leadingmarker = sketch_rib_leadingmarker_collections[-1]
                sketch_rib_leadingmarker.name = 'leadingmarker{}'.format(rib_number)
                line_rib_leadingmarker_collections.append(sketch_rib_leadingmarker.sketchCurves.sketchLines)
                line_rib_leadingmarker_collection = line_rib_leadingmarker_collections[-1]
                rib_front = [(-self.rib_center * math.cos(rot) + rib_center_camber * math.sin(rot)) * cmod + x , (-self.rib_center * math.sin(rot) - rib_center_camber * math.cos(rot)) * cmod]
                rib_end = [((1.0 - self.rib_center) * math.cos(rot) + rib_center_camber * math.sin(rot)) * cmod + x , ((1.0 - self.rib_center) * math.sin(rot) - rib_center_camber * math.cos(rot)) * cmod]
                line = line_rib_leadingmarker_collection.addByTwoPoints(\
                    adsk.core.Point3D.create((rib_front[0] + math.cos(rot)) / _scale, (rib_front[1] + math.sin(rot)) / _scale, 0), \
                    adsk.core.Point3D.create((rib_front[0] + 2.0 * math.cos(rot)) / _scale, (rib_front[1] + 2.0 * math.sin(rot)) / _scale, 0)\
                )

            # jig
            if self.check[1]:
                zig_off = self.zig_wid * self.rib_center
                zig_front_y = min(self.getMaxY(rib_poly) - 8, zig_off)
                zig_end_y = max(self.getMinY(rib_poly) + 8, zig_off - self.zig_wid)
                zig_fr = self.getFromY(rib_poly, zig_front_y)
                zig_en = self.getFromY(rib_poly, zig_end_y)
                zig_print_offset_x = x * 5 - 500
                zig_print_offset_y = 200
                if len(zig_fr) != 0 and len(zig_en) != 0:
                    zig_front_x = zig_fr[0][0] - x
                    zig_end_x = zig_en[0][0] - x
                    jig = \
                    [
                        [ zig_print_offset_x - self.keta_hei , zig_print_offset_y + zig_off],
                        [ zig_print_offset_x - self.keta_hei , zig_print_offset_y + zig_off - self.zig_wid],
                        [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , zig_print_offset_y + zig_off - self.zig_wid],
                        [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , zig_print_offset_y + zig_off - self.zig_wid - 15],
                        [ zig_print_offset_x - self.keta_hei + 10 , zig_print_offset_y + zig_off - self.zig_wid - 15],
                        [ zig_print_offset_x - self.keta_hei + 10 , zig_print_offset_y + zig_end_y - 10],
                        [ zig_print_offset_x + zig_end_x - 20 if zig_end_x - 20 > - self.keta_hei + 10 else zig_print_offset_x - self.keta_hei + 10, zig_print_offset_y + zig_end_y - 10],
                        [ zig_print_offset_x + zig_end_x , zig_print_offset_y + zig_end_y],
                        [ zig_print_offset_x + zig_end_x - 10 , zig_print_offset_y + zig_end_y + 10],
                        [ zig_print_offset_x - self.keta_hei + 10 , zig_print_offset_y + zig_end_y + 10],
                        [ zig_print_offset_x - self.keta_hei + 10 , zig_print_offset_y + zig_front_y - 10],
                        [ zig_print_offset_x + zig_front_x - 10 , zig_print_offset_y + zig_front_y - 10],
                        [ zig_print_offset_x + zig_front_x , zig_print_offset_y + zig_front_y],
                        [ zig_print_offset_x + zig_front_x - 20 , zig_print_offset_y + zig_front_y + 10],
                        [ zig_print_offset_x - self.keta_hei + 10 , zig_print_offset_y + zig_front_y + 10],
                        [ zig_print_offset_x - self.keta_hei + 10 ,  zig_print_offset_y + zig_off + 15],
                        [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , zig_print_offset_y + zig_off + 15],
                        [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , zig_print_offset_y + zig_off]
                    ]
                    jig_cm = self.set_scale(jig, _scale)
                    sketch_jig_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                    sketch_jig = sketch_jig_collections[-1]
                    sketch_jig.name = 'jig{}'.format(rib_number)
                    line_jig_collections.append(sketch_jig.sketchCurves.sketchLines)
                    line_jig_collection = line_jig_collections[-1]
                    line = line_jig_collection.addByTwoPoints(\
                        adsk.core.Point3D.create(jig_cm[0][0], jig_cm[0][1], 0), \
                        adsk.core.Point3D.create(jig_cm[1][0], jig_cm[1][1], 0)\
                    )
                    for j in jig_cm[2:]:
                        line = line_jig_collection.addByTwoPoints(\
                            line.endSketchPoint,\
                            adsk.core.Point3D.create(j[0], j[1], 0)\
                        )
                    line = line_jig_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(jig_cm[0][0], jig_cm[0][1], 0)\
                    )
            if self.check[2]:
                # beam support
                if rib_number % self.keta_interval == 0:
                        keta_support_offsetY = 500
                        keta_support_hole = (hole + self.hole_center-self.tepa*(x+self.rib_interval))/2
                        keta_support = [
                            [ zig_print_offset_x - self.keta_hei , keta_support_offsetY + zig_off ],
                            [ zig_print_offset_x - self.keta_hei , keta_support_offsetY + zig_off - self.zig_wid ],
                            [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , keta_support_offsetY + zig_off - self.zig_wid ],
                            [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , keta_support_offsetY + zig_off - self.zig_wid - 15 ],
                            [ zig_print_offset_x - self.keta_hei + 10 , keta_support_offsetY + zig_off - self.zig_wid - 15 ],
                            [ zig_print_offset_x - self.keta_hei + 10 , keta_support_offsetY - 20 ],
                            [ zig_print_offset_x + keta_support_hole/2 , keta_support_offsetY - 20 ],
                            [ zig_print_offset_x + keta_support_hole/2 , keta_support_offsetY - keta_support_hole/2  ],
                            [ zig_print_offset_x - keta_support_hole/2 , keta_support_offsetY - keta_support_hole/2 ],
                            [ zig_print_offset_x - keta_support_hole/2 , keta_support_offsetY + keta_support_hole/2 ],
                            [ zig_print_offset_x + keta_support_hole/2 , keta_support_offsetY + keta_support_hole/2 ],
                            [ zig_print_offset_x + keta_support_hole/2 , keta_support_offsetY + 20 ],
                            [ zig_print_offset_x - self.keta_hei + 10 , keta_support_offsetY + 20 ],
                            [ zig_print_offset_x - self.keta_hei + 10 , keta_support_offsetY + zig_off + 15 ],
                            [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , keta_support_offsetY + zig_off + 15 ],
                            [ zig_print_offset_x - self.keta_hei - self.frame_hei * 2 / 3 , keta_support_offsetY + zig_off ]
                        ]
                keta_support_cm = self.set_scale(keta_support, _scale)
                sketch_beamsup_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                sketch_beamsup = sketch_beamsup_collections[-1]
                sketch_beamsup.name = 'beam support{}'.format(rib_number)
                line_beamsup_collections.append(sketch_beamsup.sketchCurves.sketchLines)
                line_beamsup_collection = line_beamsup_collections[-1]
                line = line_beamsup_collection.addByTwoPoints(\
                    adsk.core.Point3D.create(keta_support_cm[0][0], keta_support_cm[0][1], 0), \
                    adsk.core.Point3D.create(keta_support_cm[1][0], keta_support_cm[1][1], 0)\
                )
                for j in keta_support_cm[2:]:
                    line = line_beamsup_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(j[0], j[1], 0)\
                    )
                line = line_beamsup_collection.addByTwoPoints(\
                    line.endSketchPoint,\
                    adsk.core.Point3D.create(keta_support_cm[0][0], keta_support_cm[0][1], 0)\
                )

            # rear jig
            if self.check[3]:
                rear_zig_poly_out = self.offsetPoly(airfoil_poly,-10)# offset-10mm
                rear_zig_poly_out = self.delete_in_dat(airfoil_poly,rear_zig_poly_out)
                rear_zig_poly_in = airfoil_poly
                rear_zig_offset_y = -300
                rear_zig_offset_x = rib_number*30

                last_out = len(rear_zig_poly_out)
                last_in = len(rear_zig_poly_in)

                kx = rear_zig_poly_out[last_out-1][0] - rear_zig_poly_in[last_in-1][0]
                ky = rear_zig_poly_out[last_out-1][1] - rear_zig_poly_in[last_in-1][1]
                k = math.sqrt(kx**2 + ky**2)

                vx = 4*kx/k
                vy = 4*ky/k

                rear_zig_te_x = rear_zig_poly_in[last_in - 1][0] + 5*vx
                rear_zig_te_y = rear_zig_poly_in[last_in-1][1] + 5*vy

                lx = vx*math.cos(math.pi/2)-vy * math.sin(math.pi / 2) #if -vx * math.sin(math.pi / 2)>4.0 else 4.0
                ly = vx*math.sin(math.pi / 2)+vy*math.cos(math.pi/2) #if vy * math.cos(math.pi / 2)>4.0 else 4.0

                rear_jig1 = []
                rear_jig2 = []
                rear_jig1.append([rear_zig_te_x+rear_zig_offset_x, rear_zig_te_y + rear_zig_offset_y])
                for p in rear_zig_poly_out[0:int(len(rear_zig_poly_out)*3/5)]:
                    rear_jig1.append([p[0]+rear_zig_offset_x, p[1] + rear_zig_offset_y])
                for p in rear_zig_poly_in[int(len(rear_zig_poly_in)*2/5):last_in]:
                    rear_jig1.append([p[0]+rear_zig_offset_x, p[1] + rear_zig_offset_y])
                for p in rear_zig_poly_out[int(len(rear_zig_poly_out)*2/5):last_out-1]:
                    rear_jig2.append([p[0]+rear_zig_offset_x, p[1] + rear_zig_offset_y])
                rear_jig2.append([rear_zig_te_x+rear_zig_offset_x, rear_zig_te_y + rear_zig_offset_y])
                for p in rear_zig_poly_in[0:int(len(rear_zig_poly_in)*3/5)]:
                    rear_jig2.append([p[0] + rear_zig_offset_x, p[1] + rear_zig_offset_y])
                rear_jig_cut2 = \
                [
                    [rear_zig_poly_in[last_in-1][0] +  rear_zig_offset_x, rear_zig_poly_in[last_in-1][1] + rear_zig_offset_y],
                    [rear_zig_poly_in[last_in-1][0] + vx+lx + rear_zig_offset_x, rear_zig_poly_in[last_in-1][1] + vy+ly + rear_zig_offset_y],
                    [rear_zig_poly_in[last_in-1][0] + 2*vx + rear_zig_offset_x,rear_zig_poly_in[last_in-1][1] + 2*vy + rear_zig_offset_y]
                ]
                rear_jig_cut1 = \
                [
                    [rear_zig_poly_in[last_in-1][0] + rear_zig_offset_x , rear_zig_poly_in[last_in-1][1] + rear_zig_offset_y],
                    [rear_zig_poly_in[last_in-1][0] + vx-lx + rear_zig_offset_x , rear_zig_poly_in[last_in-1][1] + vy-ly + rear_zig_offset_y],
                    [rear_zig_poly_in[last_in-1][0] + 2*vx + rear_zig_offset_x , rear_zig_poly_in[last_in-1][1] + 2*vy + rear_zig_offset_y]
                ]

                rear_jig1_cm = self.set_scale(rear_jig1, _scale)
                rear_jig2_cm = self.set_scale(rear_jig2, _scale)
                rear_jig_cut1_cm = self.set_scale(rear_jig_cut1, _scale)
                rear_jig_cut2_cm = self.set_scale(rear_jig_cut2, _scale)

                sketch_rear1_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                sketch_rear1 = sketch_rear1_collections[-1]
                sketch_rear1.name = 'rear jig 1-{}'.format(rib_number)
                sketch_rear2_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                sketch_rear2 = sketch_rear2_collections[-1]
                sketch_rear2.name = 'rear jig 2-{}'.format(rib_number)
                line_rear1_collections.append(sketch_rear1.sketchCurves.sketchLines)
                line_rear1_collection = line_rear1_collections[-1]
                line_rear2_collections.append(sketch_rear2.sketchCurves.sketchLines)
                line_rear2_collection = line_rear2_collections[-1]
                line = line_rear1_collection.addByTwoPoints(\
                        adsk.core.Point3D.create(rear_jig1_cm[0][0], rear_jig1_cm[0][1], 0), \
                        adsk.core.Point3D.create(rear_jig1_cm[1][0], rear_jig1_cm[1][1], 0)\
                    )
                for j in rear_jig1_cm[2:]:
                    line = line_rear1_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(j[0], j[1], 0)\
                    )
                line = line_rear1_collection.addByTwoPoints(\
                    line.endSketchPoint,\
                    adsk.core.Point3D.create(rear_jig1_cm[0][0], rear_jig1_cm[0][1], 0)\
                )
                line = line_rear1_collection.addByTwoPoints(\
                        adsk.core.Point3D.create(rear_jig_cut1_cm[0][0], rear_jig_cut1_cm[0][1], 0), \
                        adsk.core.Point3D.create(rear_jig_cut1_cm[1][0], rear_jig_cut1_cm[1][1], 0)\
                    )
                for j in rear_jig_cut1_cm[2:]:
                    line = line_rear1_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(j[0], j[1], 0)\
                    )
                line = line_rear1_collection.addByTwoPoints(\
                    line.endSketchPoint,\
                    adsk.core.Point3D.create(rear_jig_cut1_cm[0][0], rear_jig_cut1_cm[0][1], 0)\
                )
                line = line_rear2_collection.addByTwoPoints(\
                        adsk.core.Point3D.create(rear_jig2_cm[0][0], rear_jig2_cm[0][1], 0), \
                        adsk.core.Point3D.create(rear_jig2_cm[1][0], rear_jig2_cm[1][1], 0)\
                    )
                for j in rear_jig2_cm[2:]:
                    line = line_rear2_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(j[0], j[1], 0)\
                    )
                line = line_rear2_collection.addByTwoPoints(\
                    line.endSketchPoint,\
                    adsk.core.Point3D.create(rear_jig2_cm[0][0], rear_jig2_cm[0][1], 0)\
                )
                line = line_rear2_collection.addByTwoPoints(\
                        adsk.core.Point3D.create(rear_jig_cut2_cm[0][0], rear_jig_cut2_cm[0][1], 0), \
                        adsk.core.Point3D.create(rear_jig_cut2_cm[1][0], rear_jig_cut2_cm[1][1], 0)\
                    )
                for j in rear_jig_cut2_cm[2:]:
                    line = line_rear2_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(j[0], j[1], 0)\
                    )
                line = line_rear2_collection.addByTwoPoints(\
                    line.endSketchPoint,\
                    adsk.core.Point3D.create(rear_jig_cut2_cm[0][0], rear_jig_cut2_cm[0][1], 0)\
                )

            # rear tenon and mortise
            rear1 = self.getFromY(rib_poly, self.rib_rear)
            rear2 = self.getFromY(rib_poly, self.rib_rear - 2)
            #print(rear1, rear2)
            if len(rear1) == 2 and len(rear2) == 2:
                #print("hei")
                rearL = max(rear1[0][0], rear2[0][0])
                rearR = min(rear1[1][0], rear2[1][0])
                if(rearR - rearL > 7 and self.check[4]):
                    mortise = \
                    [
                        [ rearL + 3 , self.rib_rear ],
                        [ rearL + 3 , self.rib_rear - 2 ],
                        [ rearR - 3 , self.rib_rear - 2 ],
                        [ rearR - 3 , self.rib_rear ]
                    ]
                    rearR -= x
                    rearL -= x
                    mortise_cm = self.set_scale(mortise, _scale)
                    sketch_mortise_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                    sketch_mortise = sketch_mortise_collections[-1]
                    sketch_mortise.name = 'mortise{}'.format(rib_number)
                    line_mortise_collections.append(sketch_mortise.sketchCurves.sketchLines)
                    line_mortise_collection = line_mortise_collections[-1]

                    line = line_mortise_collection.addByTwoPoints(\
                    adsk.core.Point3D.create(mortise_cm[0][0], mortise_cm[0][1], 0), \
                    adsk.core.Point3D.create(mortise_cm[1][0], mortise_cm[1][1], 0)\
                        )
                    for j in mortise_cm[2:]:
                        line = line_mortise_collection.addByTwoPoints(\
                            line.endSketchPoint,\
                            adsk.core.Point3D.create(j[0], j[1], 0)\
                        )
                    line = line_mortise_collection.addByTwoPoints(\
                        line.endSketchPoint,\
                        adsk.core.Point3D.create(mortise_cm[0][0], mortise_cm[0][1], 0)\
                    )
                    if(last_rearR - last_rearL > 7 and self.check[5]):
                        rear_support_offsetY = -200
                        #print("hi")
                        tenon = \
                        [
                            [ x - self.rib_interval + 1 , last_rearL + rear_support_offsetY ],
                            [ x - self.rib_interval + 1 , last_rearL + 3 + rear_support_offsetY ],
                            [ x - self.rib_interval , last_rearL + 3 + rear_support_offsetY ],
                            [ x - self.rib_interval , last_rearR - 3 + rear_support_offsetY ],
                            [ x - self.rib_interval + 1 , last_rearR - 3 + rear_support_offsetY ],
                            [ x - self.rib_interval + 1 , last_rearR + rear_support_offsetY ],
                            [ x - 1 , rearR + rear_support_offsetY ],
                            [ x - 1 , rearR - 3 + rear_support_offsetY ],
                            [ x , rearR - 3 + rear_support_offsetY ],
                            [ x , rearL + 3 + rear_support_offsetY ],
                            [ x - 1 , rearL + 3 + rear_support_offsetY ],
                            [ x - 1 , rearL + rear_support_offsetY ]
                        ]
                        tenon_cm = self.set_scale(tenon, _scale)
                        sketch_tenon_collections.append(rootComp.sketches.add(rootComp.xYConstructionPlane))
                        sketch_tenon = sketch_tenon_collections[-1]
                        sketch_tenon.name = 'tenon{}'.format(rib_number)
                        line_tenon_collections.append(sketch_tenon.sketchCurves.sketchLines)
                        line_tenon_collection = line_tenon_collections[-1]
                        line = line_tenon_collection.addByTwoPoints(\
                        adsk.core.Point3D.create(tenon_cm[0][0], tenon_cm[0][1], 0), \
                        adsk.core.Point3D.create(tenon_cm[1][0], tenon_cm[1][1], 0)\
                            )
                        for j in tenon_cm[2:]:
                            line = line_tenon_collection.addByTwoPoints(\
                                line.endSketchPoint,\
                                adsk.core.Point3D.create(j[0], j[1], 0)\
                            )
                        line = line_tenon_collection.addByTwoPoints(\
                            line.endSketchPoint,\
                            adsk.core.Point3D.create(tenon_cm[0][0], tenon_cm[0][1], 0)\
                        )
                    last_rearL = rearL
                    last_rearR = rearR
                else:
                    last_rearR = -1
                    last_rearL = -1

            x += self.rib_interval
            rib_number += 1
            # Update progress value of progress dialog
            progressDialog.progressValue = rib_number + 1

        # Hide the progress dialog at the end.
        progressDialog.hide()


# Global set of event handlers to keep them referenced for the duration of the command
_handlers = []
_prop = PropDesign()

def fileOpen(input,ftype = '*'):
    # Set styles of file dialog.
    fileDlg = _ui.createFileDialog()
    fileDlg.isMultiSelectEnabled = False
    fileDlg.title = 'Fusion File Dialog'
    fileDlg.filter = '*.{}'.format(ftype)

    # Show file open dialog
    dlgResult = fileDlg.showOpen()
    if dlgResult == adsk.core.DialogResults.DialogOK:
        #_ui.messageBox(fileDlg.filenames[0])
        input.value = fileDlg.filenames[0]
    else:
        input.value = "error"

# Adds a new row to the table.
def addRowToTable(tableInput):
    global _rowNumber
    # Get the CommandInputs object associated with the parent command.
    cmdInputs = adsk.core.CommandInputs.cast(tableInput.commandInputs)

    # Create three new command inputs.
    stringInput1 =  cmdInputs.addStringValueInput('TableInput1_string{}'.format(_rowNumber), 'rib_number', str(_rowNumber))
    stringInput2 =  cmdInputs.addStringValueInput('TableInput2_string{}'.format(_rowNumber), 'mix_ratio', str(0))

    # Add the inputs to the table.
    row = tableInput.rowCount
    tableInput.addCommandInput(stringInput1, row, 0)
    tableInput.addCommandInput(stringInput2, row, 1)

    # Increment a counter used to make each row unique.
    _rowNumber = _rowNumber + 1

# Event handler that reacts to any changes the user makes to any of the command inputs.
class MyCommandInputChangedHandler(adsk.core.InputChangedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            global _prop, _scale
            eventArgs = adsk.core.InputChangedEventArgs.cast(args)
            inputs = eventArgs.inputs
            cmdInput = eventArgs.input
            #_ui.messageBox(str(cmdInput.parentCommandInput.id))
            if cmdInput.parentCommandInput != None:
                if cmdInput.parentCommandInput.id == 'tab_1':
                    if cmdInput.id == 'import_xrot':
                        fileOpen(inputs.itemById('xrotor_restartfile'))
                    elif cmdInput.id == 'import_main':
                        fileOpen(inputs.itemById('main_foil_path'), 'dat')
                    elif cmdInput.id == 'import_sub':
                        fileOpen(inputs.itemById('sub_foil_path'), 'dat')
                    for input in inputs:
                        if input.id == 'xrotor_restartfile':
                            _prop.filename = input.value
                        elif input.id == 'main_foil_path':
                            _prop.main_foil_path = input.value
                        elif input.id == 'sub_foil_path':
                            _prop.sub_foil_path = input.value
                        elif input.id == 'rib_start':
                            _prop.rib_start = input.value * _scale
                        elif input.id == 'rib_interval':
                            _prop.rib_interval = input.value * _scale
                        elif input.id == 'rib_center':
                            _prop.rib_center = float(input.value)
                        elif input.id == 'beam_support_interval':
                            _prop.keta_interval = int(input.value)
                        elif input.id == 'beam_tepa':
                            _prop.tepa = float(input.value)
                        elif input.id == 'hole_center':
                            _prop.hole_center = input.value * _scale
                        elif input.id == 'beam_height':
                            _prop.keta_hei = input.value * _scale
                        elif input.id == 'jig_width':
                            _prop.zig_wid = input.value * _scale
                        elif input.id == 'frame_height':
                            _prop.frame_hei = input.value * _scale

                elif cmdInput.parentCommandInput.id == 'table':
                    tableInput = inputs.itemById('table')
                    if cmdInput.id == 'tableAdd':
                        addRowToTable(tableInput)
                    elif cmdInput.id == 'tableDelete':
                        if tableInput.selectedRow == -1:
                            _ui.messageBox('Select one row to delete.')
                        else:
                            tableInput.deleteRow(tableInput.selectedRow)
                    _prop.airfoil_mix_number = []
                    _prop.airfoil_mix_ratio = []
                    for r in range(1,tableInput.rowCount):
                        _prop.airfoil_mix_number.append(int(tableInput.getInputAtPosition(r, 0).value))
                        _prop.airfoil_mix_ratio.append(float(tableInput.getInputAtPosition(r, 1).value))
                elif cmdInput.parentCommandInput.id == 'tab_4':
                    for input in inputs:
                        if input.id == 'rib':
                            _prop.check[0] = input.value
                        elif input.id == 'jig':
                            _prop.check[1] = input.value
                        elif input.id == 'beam_support':
                            _prop.check[2] = input.value
                        elif input.id == 'rear_jig':
                            _prop.check[3] = input.value
                        elif input.id == 'mortise':
                            _prop.check[4] = input.value
                        elif input.id == 'tenon':
                            _prop.check[5] = input.value
                elif cmdInput.parentCommandInput.id == 'tab_3':
                    if cmdInput.id == 'build':
                        _prop.build()
                        #_ui.messageBox(str(_prop.check))




        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts to when the command is destroyed. This terminates the script.
class MyCommandDestroyHandler(adsk.core.CommandEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # When the command is done, terminate the script
            # This will release all globals which will remove all event handlers
            adsk.terminate()
        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))


# Event handler that reacts when the command definitio is executed which
# results in the command being created and this event being fired.
class MyCommandCreatedHandler(adsk.core.CommandCreatedEventHandler):
    def __init__(self):
        super().__init__()
    def notify(self, args):
        try:
            # Get the command that was created.
            cmd = adsk.core.Command.cast(args.command)

            # Connect to the command destroyed event.
            onDestroy = MyCommandDestroyHandler()
            cmd.destroy.add(onDestroy)
            _handlers.append(onDestroy)

            # Connect to the input changed event.
            onInputChanged = MyCommandInputChangedHandler()
            cmd.inputChanged.add(onInputChanged)
            _handlers.append(onInputChanged)

            # Get the CommandInputs collection associated with the command.
            inputs = cmd.commandInputs

            # Create a tab input.
            tabCmdInput1 = inputs.addTabCommandInput('tab_1', 'param')
            tab1ChildInputs = tabCmdInput1.children

            # Create a string value input.
            xrot_file_input = tab1ChildInputs.addStringValueInput('xrotor_restartfile', 'xrotor_restartfile', _prop.filename)

            # Create bool value input with button style that can be clicked.
            tab1ChildInputs.addBoolValueInput('import_xrot', 'import_xrot', False, '', True)

            # Create a string value input.
            main_foil_input = tab1ChildInputs.addStringValueInput('main_foil_path', 'main_foil_path', _prop.main_foil_path)

            # Create bool value input with button style that can be clicked.
            tab1ChildInputs.addBoolValueInput('import_main', 'import_main', False, '', True)

            # Create a string value input.
            sub_foil_input = tab1ChildInputs.addStringValueInput('sub_foil_path', 'sub_foil_path', _prop.sub_foil_path)

            # Create bool value input with button style that can be clicked.
            tab1ChildInputs.addBoolValueInput('import_sub', 'import_sub', False, '', True)

            # Create value input.
            rib_start_input = tab1ChildInputs.addValueInput('rib_start', 'hub_radius', 'mm', adsk.core.ValueInput.createByReal(_prop.rib_start / _scale))

            # Create value input.
            rib_interval_input = tab1ChildInputs.addValueInput('rib_interval', 'rib_interval', 'mm', adsk.core.ValueInput.createByReal(_prop.rib_interval / _scale))

            # Create value input.
            rib_center_input = tab1ChildInputs.addStringValueInput('rib_center', 'rib_center', str(_prop.rib_center))

            # Create value input.
            beam_support_interval_input = tab1ChildInputs.addStringValueInput('beam_support_interval', 'beam_support_interval', str(_prop.keta_interval))

            # Create value input.
            beam_tepa_input = tab1ChildInputs.addStringValueInput('beam_tepa', 'beam_tepa', str(_prop.tepa))

            # Create value input.
            hole_center_input = tab1ChildInputs.addValueInput('hole_center', 'hole_center', 'mm', adsk.core.ValueInput.createByReal(_prop.hole_center / _scale))

            # Create value input.
            beam_height_input = tab1ChildInputs.addValueInput('beam_height', 'beam_height', 'mm', adsk.core.ValueInput.createByReal(_prop.keta_hei / _scale))

            # Create value input.
            jig_width_input = tab1ChildInputs.addValueInput('jig_width', 'jig_width', 'mm', adsk.core.ValueInput.createByReal(_prop.zig_wid / _scale))

            # Create value input.
            frame_height_input = tab1ChildInputs.addValueInput('frame_height', 'frame_height', 'mm', adsk.core.ValueInput.createByReal(_prop.frame_hei / _scale))

            # Create tab input 2
            tabCmdInput2 = inputs.addTabCommandInput('tab_2', 'mix foil')
            tab2ChildInputs = tabCmdInput2.children

            # Create table input
            tableInput = tab2ChildInputs.addTableCommandInput('table', 'Table', 2, '1:1')
            tableInput.maximumVisibleRows = 20
            global _rowNumber
            cmdInputs = adsk.core.CommandInputs.cast(tableInput.commandInputs)
            head1 = cmdInputs.addTextBoxCommandInput('rib_number', 'rib number', 'rib number', 1, True)
            head2 = cmdInputs.addTextBoxCommandInput('mix_ratio', 'subfoil mix ratio', 'sub mix ratio[%]', 1, True)
            tableInput.addCommandInput(head1, 0, 0)
            tableInput.addCommandInput(head2, 0, 1)
            _rowNumber = _rowNumber + 1
            for n, r in zip(_prop.airfoil_mix_number, _prop.airfoil_mix_ratio):
                cmdInputs = adsk.core.CommandInputs.cast(tableInput.commandInputs)
                stringInput1 =  cmdInputs.addStringValueInput('TableInput1_string{}'.format(_rowNumber), 'rib_number', str(n))
                stringInput2 =  cmdInputs.addStringValueInput('TableInput2_string{}'.format(_rowNumber), 'mix_ratio', str(r))
                row = tableInput.rowCount
                tableInput.addCommandInput(stringInput1, row, 0)
                tableInput.addCommandInput(stringInput2, row, 1)
                _rowNumber = _rowNumber + 1

            # Add inputs into the table.
            addButtonInput = tab2ChildInputs.addBoolValueInput('tableAdd', 'Add', False, '', True)
            tableInput.addToolbarCommandInput(addButtonInput)
            deleteButtonInput = tab2ChildInputs.addBoolValueInput('tableDelete', 'Delete', False, '', True)
            tableInput.addToolbarCommandInput(deleteButtonInput)

            # Create tab input 4
            tabCmdInput4 = inputs.addTabCommandInput('tab_4', 'option')
            tab4ChildInputs = tabCmdInput4.children
            tab4ChildInputs.addBoolValueInput('rib', 'rib', True, '', _prop.check[0])
            tab4ChildInputs.addBoolValueInput('jig', 'jig', True, '', _prop.check[1])
            tab4ChildInputs.addBoolValueInput('beam_support', 'beam support', True, '', _prop.check[2])
            tab4ChildInputs.addBoolValueInput('rear_jig', 'rear jig', True, '', _prop.check[3])
            tab4ChildInputs.addBoolValueInput('mortise', 'mortise', True, '', _prop.check[4])
            tab4ChildInputs.addBoolValueInput('tenon', 'tenon', True, '', _prop.check[5])

            # Create tab input 3
            tabCmdInput3 = inputs.addTabCommandInput('tab_3', 'build')
            tab3ChildInputs = tabCmdInput3.children
            # Create bool value input with button style that can be clicked.
            tab3ChildInputs.addBoolValueInput('build', 'build', False, '', True)

        except:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))

def run(context):
    try:
        global _app, _ui
        _app = adsk.core.Application.get()
        _ui = _app.userInterface

        # Get the existing command definition or create it if it doesn't already exist.
        cmdDef = _ui.commandDefinitions.itemById('cmdInputsSample')
        if not cmdDef:
            cmdDef = _ui.commandDefinitions.addButtonDefinition('cmdInputsSample', 'Command Inputs Sample', 'Sample to demonstrate various command inputs.')

        # Connect to the command created event.
        onCommandCreated = MyCommandCreatedHandler()
        cmdDef.commandCreated.add(onCommandCreated)
        _handlers.append(onCommandCreated)

        # Execute the command definition.
        cmdDef.execute()

        # Prevent this module from being terminated when the script returns, because we are waiting for event handlers to fire.
        adsk.autoTerminate(False)
    except:
        if _ui:
            _ui.messageBox('Failed:\n{}'.format(traceback.format_exc()))
