import tkinter
import os,sys
from tkinter import filedialog as tkFileDialog
import math
import numpy as np

def getCloseIndex(t,s):
    delta = [abs(i-s) for i in t]
    print(delta)
    return delta.index(min(delta))

"""
print(os.getpid())
root = tkinter.Tk()
root.withdraw()

fTyp = [('テキストファイル', '*.txt')]
# 複数のタイプを指定することも可能。

iDir = '/home/ユーザ名/'  # iDir='c:/' #Windows

# askopenfilenames 複数ファイルを選択する。
filenames = tkFileDialog.askopenfilenames(filetypes=fTyp, initialdir=iDir)
filenames = list(filenames)
if len(filenames) == 0:
    sys.exit()
"""

blade_radius_normalized  = []
filenames = []

section_number = int(input("セクション数"))

for i in range(section_number):
    print("Section{}".format(i+1))
    blade_radius_normalized.append(float(input("ブレード位置r/R")))
    filenames.append(input("ポーラーファイル名.txt").strip("\""))
    cl = float(input("設計揚力係数"))

#blade_radius_normalized = [0.1,0.5,0.75,0.9]
blade_radius_normalized = [math.floor(r*1000)/1000 for r in blade_radius_normalized]
count = 0
output_aero_data = ""

for f,r in zip(filenames,blade_radius_normalized):

    #ポーラーファイルからレイノルズ数を読み取る
    file = open(f, "r")
    Re = file.readlines()[7]
    Re = float(Re[29:33])*1e6
    Re = math.floor(Re)
    print(Re)
    file.close()

    aero = np.loadtxt(fname=f,skiprows=11).T#解析ファイル読み込み
    check_posi = [i for i in range(len(aero[2]) - 1) if(aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i]) >= 0.05 and aero[1][i]>0]
    #check_nega = [i for i in range(len(aero[2]) - 1) if(aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i]) <= -0.05]
    cl_list = [aero[1][i] for i in range(len(aero[2]) - 1) if abs((aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i])) < 0.05]
    cd_list = [aero[2][i] for i in range(len(aero[2]) - 1) if abs((aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i])) < 0.05]
    alpha_list = [aero[0][i] for i in range(len(aero[2]) - 1) if abs((aero[2][i + 1] - aero[2][i]) / (aero[1][i + 1] - aero[1][i])) < 0.05]
    alpha_list_posi = [aero[0][i] for i in check_posi]
    cl_list_posi = [aero[1][i] for i in check_posi]
    #alpha_list_nega = [aero[0][i] for i in check_nega]
    #cl_list_nega = [aero[1][i] for i in check_nega]
    cl_index = getCloseIndex(cl_list,cl)#設計揚力係数ともっとも近い解析地点を探す
    cl_delta_deg = (cl_list[cl_index+1]-cl_list[cl_index])/(alpha_list[cl_index+1]-alpha_list[cl_index])#設計揚力係数付近の揚力係数の傾きを求める
    cl_delta_rad = float(cl_delta_deg*180/math.pi)#揚力係数傾きの単位をcl/degからcl/radに変更
    alpha = alpha_list[cl_index]#設計揚力係数に近い迎角を得る
    zero_lift_alpha = float(alpha - cl_list[cl_index]/cl_delta_deg)#設計揚力係数を通るようにpolarグラフを近似した時のx切片
    res2 = np.polyfit(cl_list,cd_list, 2)#最小二乗法による二次関数近似
    cl_at_mincd = -res2[1]/(2*res2[0])
    cd_min = -res2[1]**2/(4*res2[0])+res2[2]#設計揚力係数
    cl_max = cl_list[-1]#最大揚力係数
    cl_min = cl_list[0]#最小揚力係数
    cl_delta_rad_at_stall = (max(cl_list_posi)-cl_list[-1])/(alpha_list_posi[cl_list_posi.index(max(cl_list_posi))]-alpha_list[-1])*180/math.pi
    cl_increment_to_stall = max(cl_list_posi)-cl_list[-1]
    print("cl_list",cl_list)
    print("cl_list_posi",cl_list_posi)
    print("cl_increment",cl_increment_to_stall)

    #print(cl_delta_deg)


    count += 1
    output_aero_data += "\n"
    output_aero_data += " Section "+str(count)+"   r/R = "+str(r)+"\n"
    output_aero_data += " ====================================================================\n"
    output_aero_data += " Zero-lift alpha (deg):  {zero_lift_alpha:.2f}        Minimum Cd            : {min_Cd:.4f}\n".format(zero_lift_alpha = zero_lift_alpha,min_Cd = cd_min)
    output_aero_data += " d(Cl)/d(alpha)       :  {:.3f}".format(cl_delta_rad)+"        Cl at minimum Cd     : {:.3f}\n".format(cl_at_mincd)
    output_aero_data += " d(Cl)/d(alpha)@stall :  {:.3f}".format(cl_delta_rad_at_stall)+"        d(Cd)/d(Cl**2)       : {:.4f}".format(res2[0])+"\n"
    output_aero_data += " Maximum Cl           :  {:.2f}".format(cl_max)+"         Reference Re number  :  {}.\n".format(Re)
    output_aero_data += " Minimum Cl           : {cl_min:.2f}         Re scaling exponent  : -0.4000\n".format(cl_min=cl_min)
    output_aero_data += " Cl increment to stall: {:.3f}".format(cl_increment_to_stall)+"        Cm                   : -0.100\n"
    output_aero_data += "                                      Mcrit                :  0.800\n"
    output_aero_data += " ====================================================================\n"

with open("aero_output.txt", mode='w') as f:
    f.write(output_aero_data)
