"""Recalculo independiente del revisor (no importa nada de la app ni del validador). Unidades inglesas."""
import math
from scipy.optimize import brentq
g=32.174
def geo(y,D):
    y=min(y,D*0.999999)
    th=2*math.acos(1-2*y/D); A=D*D/8*(th-math.sin(th)); P=D*th/2; T=D*math.sin(th/2); return A,P,T
def Qman(y,D,n,S): A,P,T=geo(y,D); return 1.486/n*A*(A/P)**(2/3)*S**0.5
def yn(Q,D,n,S):
    # rama inferior hasta 0.938D
    ymax=0.938*D
    if Qman(ymax,D,n,S)<Q: return None
    return brentq(lambda y:Qman(y,D,n,S)-Q,1e-6,ymax)
def yc(Q,D): return brentq(lambda y:Q*Q/g-geo(y,D)[0]**3/geo(y,D)[2],1e-6,D*0.99999)
def Qcrit(y,D): A,P,T=geo(y,D); return math.sqrt(g*A**3/T)
def hw_inlet(Q,D,S,K=0.0098,M=2.0,c=0.0398,Y=0.67):
    A=math.pi*D*D/4; q=Q/(A*D**0.5)
    def uns():
        y=yc(Q,D); a,p,t=geo(y,D); Hc=y+(Q/a)**2/(2*g)
        return (Hc/D+K*q**M-0.5*S)*D
    def sub(): return (c*q*q+Y-0.5*S)*D
    if q<=3.5: return uns(),'no sum'
    if q>=4.0: return sub(),'sum'
    # transicion lineal entre 3.5 y 4.0
    def at(qq,f):
        QQ=qq*A*D**0.5; return f(QQ)
    y1=hw_inlet(3.5*A*D**0.5,D,S,K,M,c,Y)[0]; y2=hw_inlet(4.0*A*D**0.5,D,S,K,M,c,Y)[0]
    return y1+(y2-y1)*(q-3.5)/0.5,'trans'
if __name__=='__main__':
    D=3.0
    print('EX2 2.5cfs yn(0.013)=%.4f yn(0.012)=%.4f yc=%.4f'%(yn(2.5,D,.013,.005),yn(2.5,D,.012,.005),yc(2.5,D)))
    print('  Q Manning con y=0.444, n=.013: %.3f ; n=.012: %.3f'%(Qman(.444,D,.013,.005),Qman(.444,D,.012,.005)))
    print('  Q critico con y=0.470: %.3f'%Qcrit(.470,D))
    for Q,ynp,ycp in [(5,.651,.688),(10,.934,.992),(25,1.551,1.607)]:
        print('  Q=%g yn=%.4f (HY8 %.3f) yc=%.4f (HY8 %.3f) HWi=%.4f'%(Q,yn(Q,D,.013,.005),ynp,yc(Q,D),ycp,hw_inlet(Q,D,.005)[0]))
    print('EX4 90cfs yc=%.4f ; Qcrit(2.967)=%.2f ; yn .012=%.4f .013=%.4f'%(yc(90,D),Qcrit(2.967,D),yn(90,D,.012,.03),yn(90,D,.013,.03)))
    for Q,ycp in [(54,2.385),(63,2.534),(72,2.678),(81,2.823)]: print('   EX4 Q=%g yc exacto %.4f HY8 %.3f'%(Q,yc(Q,D),ycp))
    print('EX4 HW 69.2:',hw_inlet(69.2,D,.03))
    a,p,t=geo(2.072,D); print('EX4 V a 2.072 ft: %.3f; V normal .013: %.3f'%(90/a, 90/geo(yn(90,D,.013,.03),D)[0]))
