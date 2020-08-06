import math
"""
ペラ設計ファイルから自動で図面を出力するプログラム
xrotorのrestartファイル、使用する翼型のdatファイルを入力して
VectorScriptを出力する
"""
#=======================================================================
#--------------------------------入力部分--------------------------------
#=======================================================================
# リブのオフセット(バルサの場合、外皮の厚み分)[mm]
rib_offset = 1
# 設計ファイル読み込み(xrotorのrestartfile)
filename = r"sample\bladeDesign2020_ver13_forApp.txt"
# サブ翼型のdatファイルパス(ペラ根本、ペラ端で使用)
sub_foil_path = r"sample\Maecellus_t14.65_100p.dat"
# メイン翼型のdatファイルパス(ペラ中央で使用)
main_foil_path = r"sample\slim_t8.1_ver2_100p.dat"
# 出力ファイル名
output_filename = "output.txt"
# ハブ半径[mm]
rib_start = 133
# リブ間[mm](リブ厚を無視して)
rib_interval = 30
# 桁位置
rib_center = 0.25
# 後縁サポート材(書き換えなくて大丈夫)
rib_rear = -50
# 桁支持具の間隔(リブ何個ごとに作るか)
keta_interval = 11#[リブ数/桁支持具の数]
# 各リブにおけるサブ翼型の混合比(根本側)
airfoil_mix_root = [100,95,90,85,80,75,70,65,60,55,50,45,40,35,30,25,20,15,10]
# 各リブにおけるサブ翼型の混合比(先端側)
airfoil_mix_tip = [10,20,30,40,50,60,70,80,90,100,100,100,100,100]
# 先端において何番リブから混ぜ始めるか
tip_mix_start = 30
# 桁のテーパー比
tepa = 0.00772#0.00991453
# 上のテーパー比のとき、桁を回転中心まで伸ばした時の回転中心における桁径
hole_center = 16.60992#17.34837607
#冶具
# 桁穴中心の高さ[mm]
keta_hei = 80
# 冶具幅[mm]
zig_wid = 160
# フレーム高さ[mm]
frame_hei = 80
#=======================================================================
#--------------------------------入力終了--------------------------------
#=======================================================================

XDAT_U=[0.0002,0.0003,0.0004,0.0005,0.0006,0.0007,0.0008,0.0009,0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.009,0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09, 0.1, 0.11, 0.12, 0.13, 0.14, 0.15, 0.16, 0.17, 0.18, 0.19, 0.2, 0.21, 0.22, 0.23, 0.24, 0.25, 0.26, 0.27, 0.28, 0.29, 0.3, 0.31, 0.32, 0.33, 0.34, 0.35, 0.36, 0.37, 0.38, 0.39, 0.4, 0.41, 0.42, 0.43, 0.44, 0.45, 0.46, 0.47, 0.48, 0.49, 0.5, 0.52, 0.54, 0.56, 0.58, 0.6, 0.62, 0.64, 0.66, 0.68, 0.7, 0.72, 0.74, 0.76, 0.78, 0.8, 0.82, 0.84, 0.86, 0.88, 0.9, 0.92, 0.94, 0.96, 0.98,1.0]

XDAT_D=[1.0, 0.98, 0.96, 0.94, 0.92, 0.9, 0.88, 0.86, 0.84, 0.82, 0.8, 0.78, 0.76, 0.74, 0.72, 0.7, 0.68, 0.66, 0.64, 0.62, 0.6, 0.58, 0.56, 0.54, 0.52, 0.5, 0.49, 0.48, 0.47, 0.46, 0.45, 0.44, 0.43, 0.42, 0.41, 0.4, 0.39, 0.38, 0.37, 0.36, 0.35, 0.34, 0.33, 0.32, 0.31, 0.3, 0.29, 0.28, 0.27, 0.26, 0.25, 0.24, 0.23, 0.22, 0.21, 0.2, 0.19, 0.18, 0.17, 0.16, 0.15, 0.14, 0.13, 0.12, 0.11, 0.1, 0.09, 0.08, 0.07, 0.06, 0.05, 0.04, 0.03, 0.02, 0.01,0.009,0.008,0.007,0.006,0.005,0.004,0.003,0.002,0.001,0.0009,0.0008,0.0007,0.0006,0.0005,0.0004,0.0003,0.0002, 0.0]

def linear(xs, ys, xn):
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


def linear_reverse(xs, ys, xn):
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

def shape_dat(datlist):
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
    for x in XDAT_D:

        datlist_shaped.append([x,linear_reverse(datlist_x, datlist_y,x)])
    for x in XDAT_U:
        datlist_shaped.append([x,linear(datlist_x, datlist_y,x)])
    return datlist_shaped

def interpolate_dat(datlist_shaped_list, propotions):
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

def cross(a,b):
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
def inner_product(a,b):
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

def isInner(ps,p):
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
        sin = cross(a,b)
        cos = inner_product(a,b)
        tan = math.atan2(sin,cos)
        total_degree += math.degrees(tan)
    return total_degree > 358 and total_degree < 362
def isCross(p1, p2, q1, q2):
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

def getCross(p1, p2, p3, p4):
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

    return [p1[0] + a[0] * cross(b,[p3[0]-p1[0],p3[1]-p1[1]])/cross(b, a) , p1[1] + a[1] * cross(b,[p3[0]-p1[0],p3[1]-p1[1]])/cross(b, a)]

def removeCross(ps):
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
                if isCross(ps[i], ps[i+1], ps[j], ps[j+1]):
                    c = getCross(ps[i], ps[i+1], ps[j], ps[j+1])
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


def getCenterThickness(airfoil, c):#中心線のy座標を求める
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

def isDepressed(c, p, v1, v2):
    v = [v2[0]-v1[0],v2[1]-v1[1]]
    d1 = math.sqrt((c[0]-p[0])**2 + (c[1]-p[1])**2)
    d2 = math.sqrt((c[0]-(p[0]+v[0]))**2 + (c[1]-(p[1]+v[1]))**2)
    if d1 > d2:
        return True
    else:
        return False

def getFromY(ps, ty):
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

def getMaxY(ps):
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

def getMinY(ps):
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
def delete_out_dat(pb,pa):
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
            if isInner(pb, pa[i]) == False:
                del pa[i]
                return pa, True
        return pa, False
    result = _delete_out_dat(pb,pa)
    while result[1]:
        result = _delete_out_dat(pb,result[0])
    return result[0]

def delete_in_dat(pb,pa):
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
            if isInner(pb, pa[i]):
                del pa[i]
                return pa, True
        return pa, False
    result = _delete_in_dat(pb,pa)
    while result[1]:
        result = _delete_in_dat(pb,result[0])
    return result[0]

def offsetPoly(ps, offset):
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
        return removeCross(r)
    else:
        return r

f=open(filename)
fd = f.read()
f.close()
lines = fd.split('\n')
blade_radius = 1000 * float(lines[3].split()[0]) # 半径を設計ファイルから取得
print("blade_radius",blade_radius)
design_data_r = []
design_data_c = []
design_data_rot = []
for line in lines[9:]:
    d = line.split()
    if(len(d) == 4):
        design_data_r.append(float(d[0]) * blade_radius)
        design_data_c.append(float(d[1]) * blade_radius)
        design_data_rot.append(float(d[2])*math.pi/180)

f=open(sub_foil_path)
ad = f.read()
f.close()
lines = ad.split('\n')
_sub_foil = []
for line in lines[1:]:
    d = line.split()
    if(len(d) == 2):
        _sub_foil.append([float(d[0]), float(d[1])])
sub_foil = shape_dat(_sub_foil)

f=open(main_foil_path)
ad = f.read()
f.close()
lines = ad.split('\n')
_main_foil = []
for line in lines[1:]:
    d = line.split()
    if(len(d) == 2):
        _main_foil.append([float(d[0]), float(d[1])])
main_foil = shape_dat(_main_foil)

output_rib_data = ""
x = rib_start
rot_offset = (-design_data_rot[0] - design_data_rot[-1] + math.pi) / 2
rib_number = 0
last_rearR = -1
last_rearL = -1

while x < blade_radius:
    print("rib:",rib_number)
    # 翼弦長
    cmod = linear(design_data_r, design_data_c, x)
    # 水平面を0度としたときのリブの角度をrot_offset分平行移動したもの
    rot = -linear(design_data_r, design_data_rot, x) - rot_offset
    # 各リブの桁穴直径
    hole = hole_center-tepa*x

    airfoil_data = []

    if rib_number < len(airfoil_mix_root):
        mix = airfoil_mix_root[rib_number] / 100.0
    elif tip_mix_start<=rib_number and rib_number-tip_mix_start<len(airfoil_mix_tip):
        mix = airfoil_mix_tip[rib_number-tip_mix_start]/100.0
    else:
        mix = 0

    airfoil_data = interpolate_dat([sub_foil,main_foil],[mix,1-mix])
    rib_center_camber = getCenterThickness(airfoil_data, rib_center)

    airfoil_poly = []
    rear_airfoil_poly = []

    #桁穴位置を中心に迎角分回転する操作
    for p in airfoil_data:
        px = (p[0] - rib_center) * cmod
        py = (p[1] - rib_center_camber) * cmod
        nx = px * math.cos(rot) - py * math.sin(rot) + x
        ny = px * math.sin(rot) + py * math.cos(rot)
        airfoil_poly.append([nx, ny])

    ##オフセット入力部分！
    _rib_poly = offsetPoly(airfoil_poly, rib_offset)
    #はみ出たところ消す
    rib_poly = delete_out_dat(airfoil_poly, _rib_poly)

    output_rib_data += "BeginPoly;ClosePoly;\n"

    for p in rib_poly:
        output_rib_data += "AddPoint(" + str(p[0]) + "," + str(p[1]) + ");\n"
    output_rib_data += "EndPoly;\n"
    #ここまでがリブ外形


    #桁穴
    # 桁穴分の円を一周描く操作
    output_rib_data += "Arc(" + str(x - hole / 2) + "," + str(-hole/2) + "," + str(x + hole / 2) + "," + str(hole/2) + ",#0,#360);\n"
    rib_front = [(-rib_center * math.cos(rot) + rib_center_camber * math.sin(rot)) * cmod + x , (-rib_center * math.sin(rot) - rib_center_camber * math.cos(rot)) * cmod]
    rib_end = [((1.0 - rib_center) * math.cos(rot) + rib_center_camber * math.sin(rot)) * cmod + x , ((1.0 - rib_center) * math.sin(rot) - rib_center_camber * math.cos(rot)) * cmod]
    output_rib_data += "MoveTo(" + str(rib_front[0] + math.cos(rot)) + "," + str(rib_front[1] + math.sin(rot)) + ");\n"
    output_rib_data += "LineTo(" + str(rib_front[0] + 3.0 * math.cos(rot)) + "," + str(rib_front[1] + 3.0 * math.sin(rot)) + ");\n"

    #治具幅に対する桁穴%位置と、リブに対する桁穴%位置を一致させるためのoffset
    zig_off = zig_wid * rib_center
    zig_front_y = min(getMaxY(rib_poly) - 8, zig_off)
    zig_end_y = max(getMinY(rib_poly) + 8, zig_off - zig_wid)
    zig_fr = getFromY(rib_poly, zig_front_y)
    zig_en = getFromY(rib_poly, zig_end_y)
    zig_print_offset_x = x * 5 - 500
    zig_print_offset_y = 200
    if len(zig_fr) != 0 and len(zig_en) != 0:
        zig_front_x = zig_fr[0][0] - x
        zig_end_x = zig_en[0][0] - x

        output_rib_data += "BeginPoly;ClosePoly;\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei) + "," +                      str(zig_print_offset_y + zig_off) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei) + "," +                      str(zig_print_offset_y + zig_off - zig_wid) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," +    str(zig_print_offset_y + zig_off - zig_wid) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," +    str(zig_print_offset_y + zig_off - zig_wid - 15) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," +                 str(zig_print_offset_y + zig_off - zig_wid - 15) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," +                 str(zig_print_offset_y + zig_end_y - 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x + zig_end_x - 20 if zig_end_x - 20 > - keta_hei + 10 else zig_print_offset_x - keta_hei + 10) + ","\
                                       + str(zig_print_offset_y + zig_end_y - 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x + zig_end_x) + "," +                     str(zig_print_offset_y + zig_end_y) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x + zig_end_x - 10) + "," +                str(zig_print_offset_y + zig_end_y + 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," +                 str(zig_print_offset_y + zig_end_y + 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," +                 str(zig_print_offset_y + zig_front_y - 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x + zig_front_x - 10) + "," +              str(zig_print_offset_y + zig_front_y - 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x + zig_front_x) + "," +                   str(zig_print_offset_y + zig_front_y) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x + zig_front_x - 20) + "," +              str(zig_print_offset_y + zig_front_y + 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10 ) + "," +                str(zig_print_offset_y + zig_front_y + 10) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," +                 str(zig_print_offset_y + zig_off + 15) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," +    str(zig_print_offset_y + zig_off + 15) + ");\n"
        output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," +    str(zig_print_offset_y + zig_off) + ");\n"
        output_rib_data += "EndPoly;\n"
        #桁穴中心は(zig_print_offset_x,zig_print_offset_y)

    #桁支持具
    if rib_number % keta_interval == 0:
            keta_support_offsetY = 500
            keta_support_hole = (hole + hole_center-tepa*(x+rib_interval))/2
            output_rib_data += "BeginPoly;ClosePoly;\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei) + "," + str(keta_support_offsetY + zig_off) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei) + "," + str(keta_support_offsetY + zig_off - zig_wid) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," + str(keta_support_offsetY + zig_off - zig_wid) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," + str(keta_support_offsetY + zig_off - zig_wid - 15) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," + str(keta_support_offsetY + zig_off - zig_wid - 15) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," + str(keta_support_offsetY - 20) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x + keta_support_hole/2) + "," + str(keta_support_offsetY - 20) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x + keta_support_hole/2) + "," + str(keta_support_offsetY - keta_support_hole/2 ) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_support_hole/2) + "," + str(keta_support_offsetY - keta_support_hole/2) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_support_hole/2) + "," + str(keta_support_offsetY + keta_support_hole/2) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x + keta_support_hole/2) + "," + str(keta_support_offsetY + keta_support_hole/2) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x + keta_support_hole/2) + "," + str(keta_support_offsetY + 20) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," + str(keta_support_offsetY + 20) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei + 10) + "," + str(keta_support_offsetY + zig_off + 15) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," + str(keta_support_offsetY + zig_off + 15) + ");\n"
            output_rib_data += "AddPoint(" + str(zig_print_offset_x - keta_hei - frame_hei * 2 / 3) + "," + str(keta_support_offsetY + zig_off) + ");\n"
            output_rib_data += "EndPoly;\n"


    #後縁治具
    rear_zig_poly_out = offsetPoly(airfoil_poly,-10)# offset-10mm
    rear_zig_poly_out = delete_in_dat(airfoil_poly,rear_zig_poly_out)
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

    #(vx,vy)に直角
    lx = vx*math.cos(math.pi/2)-vy * math.sin(math.pi / 2) #if -vx * math.sin(math.pi / 2)>4.0 else 4.0
    ly = vx*math.sin(math.pi / 2)+vy*math.cos(math.pi/2) #if vy * math.cos(math.pi / 2)>4.0 else 4.0

    output_rib_data += "BeginPoly;ClosePoly;\n"
    output_rib_data += "AddPoint(" + str(rear_zig_te_x+rear_zig_offset_x) + "," + str(rear_zig_te_y + rear_zig_offset_y) + ");\n"
    for p in rear_zig_poly_out[0:int(len(rear_zig_poly_out)*3/5)]:
        output_rib_data += "AddPoint(" + str(p[0]+rear_zig_offset_x) + "," + str(p[1] + rear_zig_offset_y) + ");\n"
    for p in rear_zig_poly_in[int(len(rear_zig_poly_in)*2/5):last_in]:
        output_rib_data += "AddPoint(" + str(p[0]+rear_zig_offset_x) + "," + str(p[1] + rear_zig_offset_y) + ");\n"
    output_rib_data += "EndPoly;\n"

    output_rib_data += "BeginPoly;ClosePoly;\n"
    for p in rear_zig_poly_out[int(len(rear_zig_poly_out)*2/5):last_out-1]:
        output_rib_data += "AddPoint(" + str(p[0]+rear_zig_offset_x) + "," + str(p[1] + rear_zig_offset_y) + ");\n"
    output_rib_data += "AddPoint(" + str(rear_zig_te_x+rear_zig_offset_x) + "," + str(rear_zig_te_y + rear_zig_offset_y) + ");\n"

    for p in rear_zig_poly_in[0:int(len(rear_zig_poly_in)*3/5)]:
        output_rib_data += "AddPoint(" + str(p[0] + rear_zig_offset_x) + "," + str(p[1] + rear_zig_offset_y) + ");\n"
    output_rib_data += "EndPoly;\n"

    output_rib_data += "BeginPoly;ClosePoly;\n"
    output_rib_data += "AddPoint(" + str(rear_zig_poly_in[last_in-1][0] +  rear_zig_offset_x) + "," + str(rear_zig_poly_in[last_in-1][1] + rear_zig_offset_y) + ");\n"
    output_rib_data += "AddPoint(" + str(rear_zig_poly_in[last_in-1][0] + vx+lx + rear_zig_offset_x) + "," + str(rear_zig_poly_in[last_in-1][1] + vy+ly + rear_zig_offset_y) + ");\n"
    output_rib_data += "AddPoint(" + str(rear_zig_poly_in[last_in-1][0] + 2*vx + rear_zig_offset_x) + "," + str(rear_zig_poly_in[last_in-1][1] + 2*vy + rear_zig_offset_y) + ");\n"
    output_rib_data += "EndPoly;\n"

    output_rib_data += "BeginPoly;ClosePoly;\n"
    output_rib_data += "AddPoint(" + str(rear_zig_poly_in[last_in-1][0] + rear_zig_offset_x) + "," + str(rear_zig_poly_in[last_in-1][1] + rear_zig_offset_y) + ");\n"
    output_rib_data += "AddPoint(" + str(rear_zig_poly_in[last_in-1][0] + vx-lx + rear_zig_offset_x) + "," + str(rear_zig_poly_in[last_in-1][1] + vy-ly + rear_zig_offset_y) + ");\n"
    output_rib_data += "AddPoint(" + str(rear_zig_poly_in[last_in-1][0] + 2*vx + rear_zig_offset_x) + "," + str(rear_zig_poly_in[last_in-1][1] + 2*vy + rear_zig_offset_y) + ");\n"
    output_rib_data += "EndPoly;\n"



    #後縁支持具
    rear1 = getFromY(rib_poly, rib_rear)
    rear2 = getFromY(rib_poly, rib_rear - 2)
    if len(rear1) == 2 and len(rear2) == 2:
        rearL = max(rear1[0][0], rear2[0][0])
        rearR = min(rear1[1][0], rear2[1][0])
        if(rearR - rearL > 7):
            output_rib_data += "BeginPoly;ClosePoly;\n"
            output_rib_data += "AddPoint(" + str(rearL + 3) + "," + str(rib_rear) + ");\n"
            output_rib_data += "AddPoint(" + str(rearL + 3) + "," + str(rib_rear - 2) + ");\n"
            output_rib_data += "AddPoint(" + str(rearR - 3) + "," + str(rib_rear - 2) + ");\n"
            output_rib_data += "AddPoint(" + str(rearR - 3) + "," + str(rib_rear) + ");\n"
            output_rib_data += "EndPoly;\n"
            rearR -= x
            rearL -= x
            if(last_rearR - last_rearL > 7):
                rear_support_offsetY = -200
                output_rib_data += "BeginPoly;ClosePoly;\n"
                output_rib_data += "AddPoint(" + str(x - rib_interval + 1) + "," + str(last_rearL + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - rib_interval + 1) + "," + str(last_rearL + 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - rib_interval) + "," + str(last_rearL + 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - rib_interval) + "," + str(last_rearR - 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - rib_interval + 1) + "," + str(last_rearR - 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - rib_interval + 1) + "," + str(last_rearR + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - 1) + "," + str(rearR + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - 1) + "," + str(rearR - 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x) + "," + str(rearR - 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x) + "," + str(rearL + 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - 1) + "," + str(rearL + 3 + rear_support_offsetY) + ");\n"
                output_rib_data += "AddPoint(" + str(x - 1) + "," + str(rearL + rear_support_offsetY) + ");\n"
                output_rib_data += "EndPoly;\n"
            last_rearL = rearL
            last_rearR = rearR
        else:
            last_rearR = -1
            last_rearL = -1


    x += rib_interval
    rib_number += 1

with open(output_filename, mode='w') as f:
    f.write(output_rib_data)
