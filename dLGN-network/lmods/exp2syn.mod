COMMENT

AMPA, NMDA, tonic glutamate, and GAMAb
synaptic depression is taken from T&M model
https://senselab.med.yale.edu/ModelDB/showmodel?model=3815&file=/tsodyks/tmgsyn.mod#tabs-2

ENDCOMMENT

NEURON {
	POINT_PROCESS AMPAandNMDAwithTone
	:parameters
	RANGE AMPAt1, AMPAt2, AMPAp, NMDAt1, NMDAt2, NMDAp, e, GLUTg,GABABg, gsynmod, fracca, mgblockscaler
	:synaptic depression
	RANGE tau_1, tau_rec, u0
	NONSPECIFIC_CURRENT i
	USEION k READ ek WRITE ik
	USEION ca READ cai,cao WRITE ica
	:readouts
	RANGE i, ampai, nmdai, ampag, nmdag
}

UNITS {
	(nA) = (nanoamp)
	(mV) = (millivolt)
	(uS) = (microsiemens)
	FARADAY = (faraday) (coulomb)
	R = (k-mole) (joule/degC)
}

PARAMETER {
	AMPAt1       = 0.1 (ms) <1e-9,1e9>
	AMPAt2       = 10 (ms) <1e-9,1e9>
        AMPAp        =  0 ()   <1e-9,1e9> : part of AMPA conductnace in the synaptic current
	NMDAt1       =  9 (ms) <1e-9,1e9>
	NMDAt2       = 50 (ms) <1e-9,1e9>
        NMDAp        =  1 ()   <1e-9,1e9> : part of NMDA conductnace in the synaptic current
	NMDA2AMPA    = 1 () <0,1> : fration of peak conductance NMDA to AMPA
	GLUTg        = 0 (mS)  <1e-9,1e9> : tonic glutomate conductance
	GABABg       = 0 (mS)  <1e-9,1e9> : tonic GABAb conductance
	e            = 0 (mV)  
	ek (mV)
	fracca = 0.13 : fraction of current that is ca ions; Srupuston &al 95
	gsynmod      = 1 ()        : allows modulate total synaptic conductan
	: tau_1 was the same for inhibitory and excitatory synapses
	: in the models used by T et al.
	tau_1 = 3 (ms) < 1e-9, 1e9 >
	: tau_rec = 800 ms for excitatory
	tau_rec = 800 (ms) < 1e-9, 1e9 >
	: u0 amount of x->y
	u0 = 0.04 <0,1>
	: Mg-block scaler. If zero Mg-block disabled
	mgblockscaler = 1 <0,1>

}

ASSIGNED {
	v (mV)
	i (nA)
	ik (nA)
	ampag (uS)
	nmdag (uS)
	ampai (nA)
	nmdai (nA)
	AMPAfactor
	NMDAfactor
        TOTALCond
	mgblock (1)
	mgblockstatic (1)
	mgblockdynamic (1)
	ica	  (nA)
	cai     (mM)
	cao     (mM)
	x
	celsius
}

STATE {
	ampaA (uS)
	ampaB (uS)
	nmdaA (uS)
	nmdaB (uS)
}

INITIAL {

	LOCAL tp, factor

	if (AMPAt1/AMPAt2 > 0.9999) { AMPAt1 = 0.9999*AMPAt2 }
	if (AMPAt1/AMPAt2 < 1e-9  ) { AMPAt1 = AMPAt2*1e-9   }
	ampaA = 0
	ampaB = 0
	tp = (AMPAt1*AMPAt2)/(AMPAt2 - AMPAt1)*  log(AMPAt2/AMPAt1)
	factor = -exp(-tp/AMPAt1) + exp(-tp/AMPAt2)
	AMPAfactor = 1/factor

	if (NMDAt1/NMDAt2 > 0.9999) { NMDAt1 = 0.9999*NMDAt2 }
	if (NMDAt1/NMDAt2 < 1e-9  ) { NMDAt1 = NMDAt2*1e-9   }
	nmdaA = 0
	nmdaB = 0
	tp = (NMDAt1*NMDAt2)/(NMDAt2 - NMDAt1)*  log(NMDAt2/NMDAt1)
	factor = -exp(-tp/NMDAt1) + exp(-tp/NMDAt2)
	NMDAfactor = 1/factor
    
       TOTALCond = NMDAp + AMPAp
       
       	mgblockstatic   = 1.0-mgblockscaler
	mgblockdynamic  = mgblockscaler

}

BREAKPOINT {

	SOLVE state METHOD cnexp

	ampag = ampaB - ampaA
	nmdag = nmdaB - nmdaA
	: Jahr Stevens 1990 J. Neurosci
	mgblock = mgblockstatic + mgblockdynamic / (1.0 + 0.28 * exp(-0.062(/mV) * v) )
	ampai = gsynmod * ampag * (v - e)
	nmdai = gsynmod * nmdag * (v - e) * mgblock * (1-fracca)
	if(fracca>0.0){ : assuming only NMDA pumps calcium
		ica =   gsynmod * nmdag * ghkg(v,cai,cao,2) * mgblock * fracca
	}
	i =  GLUTg*(v - e) + ampai + nmdai
	ik = GABABg*(v-ek)
}

DERIVATIVE state {
	ampaA' = -ampaA/AMPAt1
	ampaB' = -ampaB/AMPAt2
	nmdaA' = -nmdaA/NMDAt1
	nmdaB' = -nmdaB/NMDAt2
}

NET_RECEIVE(weight (uS), y, z, tsyn (ms) ) {
INITIAL {
	y = 0
	z = 0
	tsyn = t
}
	: first calculate z at event-
	:   based on prior y and z
	z = z*exp(-(t - tsyn)/tau_rec)
	z = z + ( y*(exp(-(t - tsyn)/tau_1) - exp(-(t - tsyn)/tau_rec)) / ((tau_1/tau_rec)-1) )
	: now calc y at event-
	y = y*exp(-(t - tsyn)/tau_1)


	x = 1-y-z
	y = y + x*u0
	tsyn = t

	ampaA = ampaA + weight*x*u0*AMPAfactor*AMPAp/TOTALCond
	ampaB = ampaB + weight*x*u0*AMPAfactor*AMPAp/TOTALCond
	nmdaA = nmdaA + weight*x*u0*NMDAfactor*NMDAp/TOTALCond
	nmdaB = nmdaB + weight*x*u0*NMDAfactor*NMDAp/TOTALCond
}

: from
:  http://senselab.med.yale.edu/modeldb/ShowModel.asp?model=144490&file=\bpap\ghk.inc

COMMENT
    GHK function that returns effective driving force
    Slope at low voltages is 1
    z needs to be set as a PARAMETER
ENDCOMMENT

FUNCTION ghkg(v(mV), ci(mM), co(mM), z) (mV) {
    LOCAL xi, f, exi, fxi
    f = R*(celsius+273.15)/(z*(1e-3)*FARADAY)
    xi = v/f
    exi = exp(xi)
    if (fabs(xi) < 1e-4) {
        fxi = 1 - xi/2
    }else{
        fxi = xi/(exi - 1)
    }
    ghkg = f*((ci/co)*exi - 1)*fxi
}

FUNCTION ghk(v(mV), ci(mM), co(mM), z) (.001 coul/cm3) {
    LOCAL xi, f, exi, fxi
    f = R*(celsius+273.15)/(z*(1e-3)*FARADAY)
    xi = v/f
    exi = exp(xi)
    if (fabs(xi) < 1e-4) {
        fxi = 1 - xi/2
    }else{
        fxi = xi/(exi - 1)
    }
    ghk = (.001)*z*FARADAY*(ci*exi - co)*fxi
}
