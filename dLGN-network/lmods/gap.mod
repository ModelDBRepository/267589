NEURON {
	THREADSAFE
	POINT_PROCESS gap
	NONSPECIFIC_CURRENT i
	RANGE r, i, dum
	POINTER vgap
}
PARAMETER {
	vgap (millivolt)
	r = 1e10 (megohm)
	dum = 0 (milivolt)
}
ASSIGNED {
	i (nanoamp)
	v (millivolt)
}

BREAKPOINT {
	i = (v - vgap)/r
}

