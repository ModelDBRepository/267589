from numpy import *
from neuron import h

h.celsius = 36.
"""
  forsec CellRef.apical {
    pcabar_TC_iT_Des98 = 8.9487559513902622e-05
    gh_max_TC_ih_Bud97 = 8.4228903849141138e-06
    gNap_Et2bar_TC_Nap_Et2 = 7.4653712158998865e-05
    gk_max_TC_iA = 0.0041818662141791902
    gk_max_TC_HH = 0.0099243833236075541
    gna_max_TC_HH = 0.0052508466616232969
    pcabar_TC_iL = 1.1024317581168538e-05
    gSK_E2bar_SK_E2 = 0.00021799609115766169
    taur_TC_cad = 9.5512406128698544
    gamma_TC_cad = 0.00053950618656117702
  }
  
  forsec CellRef.axonal {
    gk_max_TC_HH = 0.11490723847692205
    gna_max_TC_HH = 0.21874510090978222
  }
  
  forsec CellRef.basal {
    pcabar_TC_iT_Des98 = 8.9487559513902622e-05
    gh_max_TC_ih_Bud97 = 8.4228903849141138e-06
    gNap_Et2bar_TC_Nap_Et2 = 7.4653712158998865e-05
    gk_max_TC_iA = 0.0041818662141791902
    gk_max_TC_HH = 0.0099243833236075541
    gna_max_TC_HH = 0.0052508466616232969
    pcabar_TC_iL = 1.1024317581168538e-05
    gSK_E2bar_SK_E2 = 0.00021799609115766169
    taur_TC_cad = 9.5512406128698544
    gamma_TC_cad = 0.00053950618656117702
  }
  
  forsec CellRef.somatic {
    pcabar_TC_iT_Des98 = 8.9487559513902622e-05
    gh_max_TC_ih_Bud97 = 4.7504774088700974e-05
    gNap_Et2bar_TC_Nap_Et2 = 1.3389527019193626e-05
    gk_max_TC_iA = 0.063745893099437026
    gk_max_TC_HH = 0.11616929624507591
    gna_max_TC_HH = 0.091136959874091761
    pcabar_TC_iL = 0.00049811286552489979
    gSK_E2bar_SK_E2 = 0.0012832790164235054
    taur_TC_cad = 11.005585762426819
    gamma_TC_cad = 0.0067401226271938839
  }

"""


class dLGN:
    def __init__(self, nid=0):
        #=== Somatic compartment ===#
        self.soma = h.Section(name=f"soma{nid:04d}")
        self.soma.nseg = 1
        self.soma.diam = 70.
        self.soma.L = 100
        self.soma.cm = 1.
        # self.soma.Ra = 100.
        self.soma(0.5).v = -76.
        
        self.soma.insert("pas")
        self.soma.insert("TC_cad")
        self.soma.insert("TC_ih_Bud97")
        self.soma.insert("TC_Nap_Et2")
        self.soma.insert("TC_iA")
        self.soma.insert("TC_iL")
        self.soma.insert("SK_E2")
        self.soma.insert("TC_HH")
        self.soma.insert("TC_iT_Des98")
        self.soma(0.5).TC_iT_Des98.pcabar = 8.94876E-05
        self.soma(0.5).TC_ih_Bud97.gh_max = 4.75048E-05
        self.soma(0.5).TC_Nap_Et2.gNap_Et2bar = 1.33895E-05
        self.soma(0.5).TC_iA.gk_max = 0.0637459
        self.soma(0.5).TC_HH.gk_max = 0.116169
        self.soma(0.5).TC_HH.gna_max = 0.091137
        self.soma(0.5).TC_iL.pcabar = 0.000498113
        self.soma(0.5).SK_E2.gSK_E2bar = 0.00128328
        self.soma(0.5).TC_cad.taur = 11.0056
        self.soma(0.5).TC_cad.gamma = 0.00674012
        self.soma.ena = 50
        self.soma.ek = -90
        self.soma(0.5).pas.e = -80
        self.soma(0.5).pas.g = 3.2505679140951987e-05
        
        #=== Axon compartment ===#
        self.axon = h.Section(name=f'axon{nid:04d}')
        self.axon.nseg = 1
        self.axon.diam = 1
        self.axon.L = 100
        self.axon.cm = 1.
        # self.axon.Ra = 1000
        self.axon.insert("TC_HH")
        self.axon(0.5).v = -76.
        self.axon(0.5).gk_max_TC_HH  = 0.025743424884903152
        self.axon(0.5).gna_max_TC_HH = 0.19029057946443442
        self.axon.ena = 50
        self.axon.ek = -90
        self.axon.connect(self.soma(0),1)

        # #=== Dendritic compartment ===#
        # self.dend = h.Section(name="dend")
        # self.dend.nseg = 10
        # self.dend.diam = 10.
        # self.dend.L = 1000
        # self.dend.cm = 1.
        # self.dend.Ra = 100.
        # self.dend(0.5).v = -76.
        
        # self.dend.insert("pas")
        # self.dend.insert("TC_cad")
        # self.dend.insert("TC_ih_Bud97")
        # self.dend.insert("TC_Nap_Et2")
        # self.dend.insert("TC_iA")
        # self.dend.insert("TC_iL")
        # self.dend.insert("SK_E2")
        # self.dend.insert("TC_HH")
        # self.dend.insert("TC_iT_Des98")
 
        # self.dend(0.5).TC_iT_Des98.pcabar = 8.9487559513902622e-05
        # self.dend(0.5).TC_ih_Bud97.gh_max = 8.4228903849141138e-06
        # self.dend(0.5).TC_Nap_Et2.gNap_Et2bar = 7.4653712158998865e-05
        # self.dend(0.5).TC_iA.gk_max = 0.0041818662141791902
        # self.dend(0.5).TC_HH.gk_max = 0.0099243833236075541
        # self.dend(0.5).TC_HH.gna_max = 0.0052508466616232969
        # self.dend(0.5).TC_iL.pcabar = 1.1024317581168538e-05
        # self.dend(0.5).SK_E2.gSK_E2bar = 0.00021799609115766169
        # self.dend(0.5).TC_cad.taur = 9.5512406128698544
        # self.dend(0.5).TC_cad.gamma = 0.00053950618656117702
        # self.dend.ena = 50
        # self.dend.ek = -90
        # self.dend(0.5).pas.e = -80
        # self.dend(0.5).pas.g = 3.2505679140951987e-05
        
        # self.dend.connect(self.soma(1),0)
        
    def setcable(self,\
        # these are reasonable values for most models
        freq     = 100,   # Hz, frequency at which AC length constant will be computed
        d_lambda = 0.1
        ):
        '''
            /* Sets nseg in each section to an odd value
           so that its segments are no longer than 
             d_lambda x the AC length constant
           at frequency freq in that section.

           Be sure to specify your own Ra and cm before calling geom_nseg()

           To understand why this works, 
           and the advantages of using an odd value for nseg,
           see  Hines, M.L. and Carnevale, N.T.
                NEURON: a tool for neuroscientists.
                The Neuroscientist 7:123-135, 2001.
            */
            hoc code is taken from ModelDB #144541
            fixseg.hoc
        '''


        lam  = self.axon.L/sqrt(self.axon(0).diam + self.axon(1).diam)
        #  length of the section in units of lambda
        lam *= sqrt(2) * 1e-5*sqrt(4*pi*freq*self.axon.Ra*self.axon.cm)
        dflambda = d_lambda*self.axon.L/lam
        self.axon.nseg = int((self.axon.L/dflambda+0.9)/2)*2 + 1
        

param_nslh =[
    ["soma.L"                           , 'lin',  20., 200.], # 76.5
    ["soma(0.5).pas.e"                  , 'lin', -55., -90.], # -80
    ["soma(0.5).pas.g"                  , 'log', 1e-7, 1e-1], # 3.2505679140951987e-05
    ["soma(0.5).TC_HH.gk_max"           , 'log', 1e-7, 1e-1], # 0.041035125
    ["soma(0.5).TC_HH.gna_max"          , 'log', 1e-7, 1e-1], # 0.03664769
    ["soma(0.5).TC_HH.vtraub"           , 'lin', -70., 20. ], # -55.5
    ["soma(0.5).TC_HH.vtraub2"          , 'lin', -70., 20. ], # -45.5

    ["soma(0.5).SK_E2.gSK_E2bar"        , 'log', 1e-7, 1e-1], # 0.0004683615
    ["soma(0.5).SK_E2.zTau"             , 'lin', 1.,   500.], # 1.
    ["soma(0.5).TC_iT_Des98.shift"      , 'lin', -25.,  25.], # 2
    ["soma(0.5).TC_iT_Des98.actshift"   , 'lin', -25.,  25.], # 0
    ["soma(0.5).TC_iT_Des98.pcabar"     , 'log', 1e-7, 5e-1], # 8.81249E-05
    ["soma(0.5).TC_ih_Bud97.gh_max"     , 'log', 1e-7, 5e-1], # 5.0524245E-05
    ["soma(0.5).TC_ih_Bud97.e_h"        , 'lin', -50.,   0.], # -43.
    ["soma(0.5).TC_Nap_Et2.gNap_Et2bar" , 'log', 1e-7, 5e-1], # 5.65208E-05
    ["soma(0.5).TC_cad.taur"            , 'lin',   2.,  30.], #  5.35391],
    ["soma(0.5).TC_cad.gamma"           , 'log', 1e-5, 1e-1], #  0.02939311
    ["soma(0.5).TC_iA.gk_max"           , 'log', 1e-7, 1e-1], # 0.020153085
    ["soma(0.5).TC_iL.pcabar"           , 'log', 1e-7, 1e-1], # 0.0005641955
    ["soma.cao"                         , 'lin',   1.,   6.], # 2. (really 5)
###
    [("soma.ena","axon.ena")            , 'lin',  40.,  65.], # 50
    [("soma.ek", "axon.ek" )            , 'lin', -65.,-110.], # -90
###
    ["axon.diam"                        , 'lin',   .5,   5.], # 76.5
    ["axon.L"                           , 'lin', 100.,1000.], # 76.5
    ["axon(0.5).TC_HH.gk_max"           , 'log', 1e-7,   1.], # 0.025743424884903152
    ["axon(0.5).TC_HH.gna_max"          , 'log', 1e-7,   1.], # 0.19029057946443442
    ["axon(0.5).TC_HH.vtraub"           , 'lin', -70., 20. ], # -55.5
    ["axon(0.5).TC_HH.vtraub2"          , 'lin', -70., 20. ], # -45.5
    [("axon.Ra","soma.Ra")              , 'lin',  20., 120 ]  # 76.5
]


if __name__ == "__main__":
    from matplotlib.pyplot import *
    xc = dLGN()
    xc.setcable()
    # ic = h.IClamp(0.5, sec=xc.soma)
    # ic.amp = 4.
    ic = h.IClamp(0.5, sec=xc.soma)
    ic.amp = 1.2
    ic.delay = 500.
    ic.dur   = 500.
    t,v1,c1,v2,c2 = h.Vector(),h.Vector(),h.Vector(),h.Vector(),h.Vector()
    t.record(h._ref_t)
    v1.record(xc.soma(0.5)._ref_v)
    c1.record(xc.soma(0.5)._ref_cai)
    v2.record(xc.axon(0.5)._ref_v)
    #c2.record(xc.dend(0.5)._ref_cai)
    
    h.finitialize()
    h.fcurrent()
    h.frecord_init()
    # st = int(h.ion_style("ca_ion", sec=xc.soma)-128 )
    # #h.ion_style("ca_ion",2,2,1,1,1, sec=xc.soma) )
    
    # eadvance   = st//64
    # einit      = (st - eadvance*64)//32
    # e_style    = (st - eadvance*64 - einit*32)//8
    # cinit      = (st - eadvance*64 - einit*32 - e_style*8)//4
    # c_style    = st - eadvance*64 - einit*32 - e_style*8 - cinit*4
    # print("style",c_style,cinit,e_style,einit,eadvance)
    # print(xc.soma(0.5).cai)
    # #print(xc.soma(0.5).TC_iL.cai)

    while h.t < 1600. :h.fadvance()
    vax = subplot(211)
    plot(array(t),array(v1),'k-')
    plot(array(t),array(v2),'r-')
    cax = subplot(212,sharex= vax)
    plot(array(t),array(c1),'k-')
    # plot(array(t),array(c2),'r-')
    show()
    exit(0)
