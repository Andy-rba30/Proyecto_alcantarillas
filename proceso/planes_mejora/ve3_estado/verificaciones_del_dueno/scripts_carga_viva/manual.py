import math
FT=0.3048; KIP=4.4482216152605; PSF=47.880259; LBFT=14.5939029
def cv9(H_ft, Di_in, LLDF, axle_kip, sa_ft, IM_DE_ft=None, m=1.2, wt=20., lt=10.):
    sw=6.0
    Hit=(sw-wt/12-0.06*Di_in/12)/LLDF
    if H_ft<Hit: ww=wt/12+LLDF*H_ft+0.06*Di_in/12; P=axle_kip/2
    else: ww=wt/12+sw+LLDF*H_ft+0.06*Di_in/12; P=axle_kip
    Hip=(sa_ft-lt/12)/LLDF
    if H_ft<Hip: lw=lt/12+LLDF*H_ft
    else: lw=lt/12+sa_ft+LLDF*H_ft; P*=2
    DE=H_ft if IM_DE_ft is None else IM_DE_ft
    IM=max(0,33*(1-0.125*DE))
    PL=P*(1+IM/100)*m/(lw*ww)  # ksf
    return dict(Hit=Hit,Hip=Hip,ww=ww,lw=lw,P=P,IM=IM,PL_psf=PL*1000)
def lldf_c(Di_ft): return min(1.75,max(1.15,1.15+0.6*(Di_ft-2)/6))
print("== (a) ACPA DD1 Ej.1: 30 in, Do=3.08 ft, H=2 ft")
L=lldf_c(2.5)
for nom,ax,sa in (("camion",32,14),("tandem",25,4)):
    r=cv9(2,30,L,ax,sa); WL=r['PL_psf']*min(r['lw'],3.08)
    print(nom,L,{k:round(v,3) for k,v in r.items()},"WL plf",round(WL,1))
r=cv9(2,30,L,32,14); WL9=r['PL_psf']*min(r['lw'],3.08)
# ACPA
a=4+20/12+1.15*2; b=10/12+1.15*2; A=a*b; IM=0.33*(1-0.125*2); w=32000*(1+IM)/A
WT=w*a*3.08; Le=a+1.75*0.75*3.08
print("ACPA a,b,A,w,WT,Le,WL",round(a,3),round(b,3),round(A,2),round(w,1),round(WT),round(Le,3),round(WT/Le,1))
print("ratio total",WL9/(WT/Le), "vs 3272:",WL9/3272)
# descomposicion: carga lineal a lo largo del tubo
print("presion",r['PL_psf']/w,"  Le/L",Le/a)
# factores sucesivos partiendo de ACPA
P0=32000*(1+IM)/a/b
steps=[]
# 1) cambiar a una rueda con m=1.2 (9a): P=16000*1.2, ancho a sin sw(4ft)
a1=20/12+1.15*2; w1=16000*1.2*(1+IM)/(a1*b); steps.append(("una rueda m=1.2 en vez de 2 ruedas en paso",w1/w))
a2=20/12+1.2*2; b2=10/12+1.2*2; w2=16000*1.2*(1+IM)/(a2*b2); steps.append(("LLDF 1.15->1.20",w2/w1))
a3=a2+0.15; w3=16000*1.2*(1+IM)/(a3*b2); steps.append(("0.06 Di",w3/w2))
steps.append(("SL: min(lw,Bc)/min(b,Bc)", min(b2,3.08)/min(b,3.08)))
steps.append(("sin Le", Le/a))
tot=1
for s,f in steps: tot*=f; print(f"  {s}: x{f:.4f}")
print("  producto",tot)
print("== (b) PPI Ej.2: HDPE 48 in, Do=54, H=2 ft, rueda 45 kip 18x18, IM=0, m=1")
lw=18+1.15*24; ww=18+1.15*24+0.06*48; print(lw,ww,45000/(lw*ww),"psi")
r=cv9(2,48,1.15,32,14); print("HL-93 camion 9a:",{k:round(v,3) for k,v in r.items()}, "psi",r['PL_psf']/144)
r=cv9(2,48,1.15,25,4); print("HL-93 tandem 9a:",{k:round(v,3) for k,v in r.items()}, "psi",r['PL_psf']/144)
print("== (c) 0.60 m")
for H,Di,Bc,cond in ((0.60,0.60,0.75,'flex'),(0.61,0.60,0.75,'conc'),(0.60,0.60,0.75,'conc')):
    L=1.15 if cond=='flex' else lldf_c(Di/FT)
    for nom,ax,sa in (("camion",32,14),("tandem",25,4)):
        r=cv9(H/FT,Di/.0254,L,ax,sa)
        PL=r['PL_psf']*PSF/1000; lw=r['lw']*FT
        print(cond,H,nom,"LLDF",round(L,4),"IM",round(r['IM'],3),"lw",round(lw,4),"ww",round(r['ww']*FT,4),"PL kPa",round(PL,3),"WL kN/m (Bc)",round(PL*min(lw,Bc),3),"P_L*min(lw,Di)",round(PL*min(lw,Di),3))
