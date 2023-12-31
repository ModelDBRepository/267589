:Comment : mtau deduced from text (said to be 6 times faster than for NaTa)
:Comment : so I used the equations from NaT and multiplied by 6
:Reference : Modeled according to kinetics derived from Magistretti & Alonso 1999
:Comment: corrected rates using q10 = 2.3, target temperature 34, orginal 21

: 2019: From ModelDB, accession no. 139653.
: mInf and hInf modified for thalamic cells models by Elisabetta Iavarone @ Blue Brain Project.
: See equations for references.

NEURON	{
	SUFFIX TC_Nap_Et2
	USEION na READ ena WRITE ina
	RANGE gNap_Et2bar, gNap_Et2, ina
}

UNITS	{
	(S) = (siemens)
	(mV) = (millivolt)
	(mA) = (milliamp)
}

PARAMETER	{
	gNap_Et2bar = 0.00001 (S/cm2)
}

ASSIGNED	{
	v		(mV)
	ena		(mV)
	ina		(mA/cm2)
	gNap_Et2	(S/cm2)
	mInf
	mTau
	mAlpha
	mBeta
	hInf
	hTau
	hAlpha
	hBeta
	celsius		(degC)
}

STATE	{
	m
	h
}

BREAKPOINT	{
	SOLVE states METHOD cnexp
	gNap_Et2 = gNap_Et2bar*m*m*m*h
	ina = gNap_Et2*(v-ena)
}

DERIVATIVE states	{
	rates()
	m' = (mInf-m)/mTau
	h' = (hInf-h)/hTau
}

INITIAL{
	rates()
	m = mInf
	h = hInf
:DB>>
printf("celsius=%0.2f\n",celsius)
:<<DB
}


PROCEDURE rates(){
    LOCAL qt
:    qt = 2.3^((34-21)/10)
    qt = 2.3^((celsius-22)/10) : RTH corrected to fit DB temerature.
                               : RTH it woudn't change DB fitting 
                               :     but add temerature correction

    UNITSOFF
    mInf = 1.0/(1+exp(-(v+56.93)/9.09)) : Parri and Crunelli, J. Neurosci. 1998
    if(v == -38){
	v = v+0.0001
    }
    mAlpha = (0.182 * (v- -38))/(1-(exp(-(v- -38)/6)))
    mBeta  = (0.124 * (-v -38))/(1-(exp(-(-v -38)/6)))
    mTau = 6*(1/(mAlpha + mBeta))/qt

    if(v == -17){
	v = v + 0.0001
    }
    if(v == -64.4){
	v = v+0.0001
    }
    hInf = 1.0/(1+exp((v+58.7)/14.2)) : Amarillo et al., J Neurophysiol, 2014 
    hAlpha = -2.88e-6 * (v + 17) / (1 - exp((v + 17)/4.63))
    hBeta = 6.94e-6 * (v + 64.4) / (1 - exp(-(v + 64.4)/2.63))
    hTau = (1/(hAlpha + hBeta))/qt
    UNITSON
}
