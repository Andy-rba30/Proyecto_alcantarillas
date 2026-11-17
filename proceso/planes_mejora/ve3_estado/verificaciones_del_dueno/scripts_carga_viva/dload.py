import math
from manual import cv9, lldf_c, FT, PSF
def interp(x,xs,ys):
    if x<=xs[0]: return ys[0]
    for a,b,c,d in zip(xs,ys,xs[1:],ys[1:]):
        if x<=c: return b+(d-b)*(x-a)/(c-a)
    return ys[-1]
CL=[("I",40),("II",50),("III",65),("IV",100),("V",140)]
def clase(D):
    for n,d in CL:
        if D<=d: return n
    return ">V"
print("Di  H   | WL_M8 kN/m  D_M8 clase | WL_conLe  D clase | dif D%   (Tipo 2, gamma 19, VAF 1.40, pared B)")
for Di in (0.6,0.9,1.2,1.5):
  for H in (0.61,0.8,1.0,1.5,2.4):
    din=Di/.0254; t=(din/12+1)*.0254; Bc=Di+2*t
    L=lldf_c(Di/FT); best=None
    for ax,sa in ((32,14),(25,4)):
        r=cv9(H/FT,din,L,ax,sa); PL=r['PL_psf']*PSF/1000; lw=r['lw']*FT; ww=r['ww']*FT
        WL=PL*min(lw,Bc)
        if best is None or WL>best[0]: best=(WL,ww)
    WL,ww=best; WLe=WL*ww/(ww+1.75*0.75*Bc)
    WE=1.40*Bc*19*H; WF=9.81*math.pi*Di**2/4
    BFE=interp(din,(12,24,36,72,144),(3.2,3.0,2.9,2.8,2.8)); BFLL=interp(din,(12,18,24,30),(2.4,2.4,2.4,2.2))
    D1=((WE+WF)/BFE+WL/BFLL)/Di; D2=((WE+WF)/BFE+WLe/BFLL)/Di   # kN/m/m = N/m/mm
    print(f"{Di:.1f} {H:.2f} | {WL:6.1f} {D1:6.1f} {clase(D1):>3} | {WLe:6.1f} {D2:6.1f} {clase(D2):>3} | {100*(D1/D2-1):+5.0f}%")
