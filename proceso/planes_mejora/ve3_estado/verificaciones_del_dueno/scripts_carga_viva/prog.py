from src.modulos import M8_estructural as M8
from src.modelos import ErrorProyecto
FT=0.3048
def run(tag,H,Di,cond,Bc=None):
    try:
        ef=(lambda PL,lw: PL*min(lw,Bc)) if Bc else None
        cv=M8.carga_viva_enterrada(H=H,D_i=Di,conducto=cond,efecto=ef,efecto_descripcion="WL" if Bc else "")
        print(tag,cv.vehiculo,"LLDF",round(cv.LLDF,4),"IM",round(cv.IM_pct,3),"m",cv.m,"lw",round(cv.l_w_m,4),"ww",round(cv.w_w_m,4),
              "PL kPa",round(cv.P_L_kPa,3),"= psf",round(cv.P_L_kPa*1000/47.880259,1),"psi",round(cv.P_L_kPa/6.894757,3),"efecto",round(cv.efecto,3), "plf",round(cv.efecto*1000/14.5939029,1))
    except ErrorProyecto as e:
        print(tag,type(e).__name__,str(e)[:230])
run("a DD1",2*FT,30*.0254,"tubo_concreto",3.08*FT)
run("b PPI geom HL93",2*FT,48*.0254,"flexible")
run("c flex .60",0.60,0.60,"flexible")
run("c conc .60",0.60,0.60,"tubo_concreto",0.75)
run("c conc .61",0.61,0.60,"tubo_concreto",0.75)
run("conc 0.6 H=1.0",1.0,0.60,"tubo_concreto",0.75)
run("conc 0.9 H=0.61",0.61,0.90,"tubo_concreto",1.10)
