import sys, os, json
from numpy import *
from sklearn.decomposition import PCA
from scipy.stats     import gaussian_kde as kde
import matplotlib
matplotlib.rcParams.update({'font.size': 5})
from matplotlib.pyplot import *


with open(sys.argv[1]) as fd:
    j = json.load(fd)

models = [ [ m['parameters'],m["target"] ]
    for r in 'final records unique model models'.split() if r in j
    for m in j[r] if not m is None
]

dublicates={}
if 'parameters' in j:
    scales = []
    parameters = []
    for p,s,m,M in j["parameters"]:
        if type(p) is list or type(p) is tuple:
            #for n in p: scales.append(s)
            scales.append(s)
            parameters.append(p[0])
            for n in p[1:]: dublicates[n]=p[0]
        else:
            scales.append(s)
            parameters.append(p)

else:
    scales = None

#if not 'parameters' in j:
    #parameters = []
    #for p,_ in models:
        #for n in p:
            #if not n in parameters and not n in dublicates:
                #parameters.append(n)
#else:
    
    #for p,_,_,_ in j["parameters"]:
        #if type(p) is list or type(p) is tuple:
            ##parameters += list(p)
            
        #else:
            
    #for p,_ in models:
        #for n in p:
            #if not n in parameters:
                #parameters.append(n)
#DB>>
# parameters = parameters[:10]
#<<DB
targets = array([ t for _,t in models])
#.astype(float)
#targets = targets/4

#DB>>
# print(targets)
# exit(0)
#<<DB

#models = array([
    #[ (p[n] if n in p else nan)  
    #for n in parameters ]
    #for p,_ in models
#])
models = array([
    [ p[n] for n in parameters if n in p ]
    for p,_ in models
])

if scales is None:
    xmin = [ amin(models[where(~isnan(models[:,i])),i]) for i in range(models.shape[1]) ]
    xmax = [ amax(models[where(~isnan(models[:,i])),i]) for i in range(models.shape[1]) ]
else:
    xmin = [ amin(log10( models[where(~isnan(models[:,i])),i] ) if scales[i] == 'log' else models[where(~isnan(models[:,i])),i] ) for i in range(models.shape[1]) ]
    xmax = [ amax(log10( models[where(~isnan(models[:,i])),i] ) if scales[i] == 'log' else models[where(~isnan(models[:,i])),i] ) for i in range(models.shape[1]) ]
    


f = figure(1,figsize=(18,15))

t1 = [ i for i,m in enumerate(targets) if m == 1]
t2 = [ i for i,m in enumerate(targets) if m == 2]

if scales is None:
    hist0 = [
        column_stack( (linspace(xmin[i],xmax[i],21), kde(models[where(~isnan(models[:,i])),i])(linspace(xmin[i],xmax[i],21))) )
        for i in range(models.shape[1]) ]
    hist1 = [
        column_stack( (linspace(xmin[i],xmax[i],21), kde(models[where(~isnan(models[t1,i])),i])(linspace(xmin[i],xmax[i],21))) )
        for i in range(models.shape[1]) ]
    hist2 = [
        column_stack( (linspace(xmin[i],xmax[i],21), kde(models[where(~isnan(models[t2,i])),i])(linspace(xmin[i],xmax[i],21))) )
        for i in range(models.shape[1]) ]

    # hist0 = [
        # histogram(models[where(~isnan(models[:,i])),i],bins=21,range=(xmin[i],xmax[i]) )
        # for i in range(models.shape[1]) ]
    # hist1 = [
        # histogram(models[where(~isnan(models[t1,i])),i],bins=21,range=(xmin[i],xmax[i]) )
        # for i in range(models.shape[1]) ]
    # hist2 = [
        # histogram(models[where(~isnan(models[t2,i])),i],bins=21,range=(xmin[i],xmax[i]) )
        # for i in range(models.shape[1]) ]
else:
    hist0 = [
        column_stack( (linspace(xmin[i],xmax[i],21), kde(log10( models[where(~isnan(models[:,i])),i]))(linspace(xmin[i],xmax[i],21))) )
        if scales[i] == 'log' else
        column_stack( (linspace(xmin[i],xmax[i],21), kde(       models[where(~isnan(models[:,i])),i] )(linspace(xmin[i],xmax[i],21))) )
        for i in range(models.shape[1]) ]
    hist1 = [
        column_stack( (linspace(xmin[i],xmax[i],21), kde(log10( models[where(~isnan(models[t1,i])),i]))(linspace(xmin[i],xmax[i],21))) )
        if scales[i] == 'log' else
        column_stack( (linspace(xmin[i],xmax[i],21), kde(       models[where(~isnan(models[t1,i])),i] )(linspace(xmin[i],xmax[i],21))) )
        for i in range(models.shape[1]) ]
    hist2 = [
        column_stack( (linspace(xmin[i],xmax[i],21), kde(log10( models[where(~isnan(models[t2,i])),i]))(linspace(xmin[i],xmax[i],21))) )
        if scales[i] == 'log' else
        column_stack( (linspace(xmin[i],xmax[i],21), kde(       models[where(~isnan(models[t2,i])),i] )(linspace(xmin[i],xmax[i],21))) )
        for i in range(models.shape[1]) ]

    # hist0 = [
        # histogram(log10( models[where(~isnan(models[:,i])),i]),bins=21,range=(xmin[i],xmax[i]) )
        # if scales[i] == 'log' else
        # histogram(       models[where(~isnan(models[:,i])),i] ,bins=21,range=(xmin[i],xmax[i]) )
        # for i in range(models.shape[1]) ]
    # hist1 = [
        # histogram(log10( models[where(~isnan(models[t1,i])),i]),bins=21,range=(xmin[i],xmax[i]) )
        # if scales[i] == 'log' else
        # histogram(       models[where(~isnan(models[t1,i])),i] ,bins=21,range=(xmin[i],xmax[i]) )
        # for i in range(models.shape[1]) ]
    # hist2 = [
        # histogram(log10( models[where(~isnan(models[t2,i])),i]),bins=21,range=(xmin[i],xmax[i]) )
        # if scales[i] == 'log' else
        # histogram(       models[where(~isnan(models[t2,i])),i] ,bins=21,range=(xmin[i],xmax[i]) )
        # for i in range(models.shape[1]) ]
    
Nx = 6#int( round( sqrt( len(parameters) ) ) )
Ny = len(parameters)//Nx + (1 if len(parameters)%Nx else 0)
for i,(p,h0,h1,h2) in enumerate(zip(parameters,hist0,hist1,hist2)):
    ax = subplot(Ny,Nx,i+1)
    ax.tick_params(direction="in")
    allnames = p + " " + " ".join([ n for n in dublicates if dublicates[n] == p])
    xlabel(allnames)
    if scales is not None and scales[i] == 'log':
        ax.set_xscale('log',base=10) 
        # h,b = h1
        # b = (10**b[:-1]+10**b[1:])/2
        # plot(b,h/sum(h),"o",c="#d62728",label="neuron 1" )
        # h,b = h2
        # b = (10**b[:-1]+10**b[1:])/2
        # plot(b,h/sum(h),"o",c="#9467bd",label="neuron 2")
        # #-------------
        # h,b = h0
        # b = (10**b[:-1]+10**b[1:])/2
        # #b = (b[:-1]+b[1:])/2
        # plot(b,h/sum(h),"k-",lw=3,label="all")
        # #bar(b,h/sum(h),width=(b[1]-b[0]),color='k')
        plot(10**h1[:,0],h1[:,1],"-",c="#d62728",label="neuron 1" )
        plot(10**h2[:,0],h2[:,1],"-",c="#9467bd",label="neuron 2" )
        plot(10**h0[:,0],h0[:,1],"-",c="k"      ,label="all" )
    else:
        # h,b = h1
        # b = (b[:-1]+b[1:])/2
        # plot(b,h/sum(h),"o",c="#d62728",label="neuron 1" )
        # h,b = h2
        # b = (b[:-1]+b[1:])/2
        # plot(b,h/sum(h),"o",c="#9467bd",label="neuron 2")
        # #-----------
        # h,b = h0
        # b = (b[:-1]+b[1:])/2
        # plot(b,h/sum(h),"k-",lw=3,label="all")
        # #bar(b,h/sum(h),width=(b[1]-b[0]),color='k')
        plot(h1[:,0],h1[:,1],"-",c="#d62728",label="neuron 1" )
        plot(h2[:,0],h2[:,1],"-",c="#9467bd",label="neuron 2" )
        plot(h0[:,0],h0[:,1],"-",c="k"      ,label="all" )
    if i==0:
        legend(loc='best')

f2 = figure(2, figsize=(15,15))
pca = PCA(n_components=6,whiten=True)
scaledmodels = array( [ [ (log10(p) if s == 'log' else p )for p,s in zip(m,scales)] for m in models] )
scaledmodels -= mean(scaledmodels,axis= 0)
scaledmodels /=  std(scaledmodels,axis= 0)
#X = pca.fit_transform( scaledmodels -= mean(scaledmodels,axis= 0) )
X = pca.fit_transform(scaledmodels)
cmap = get_cmap("tab10")
color=[ ("#d62728" if k == 1 else ("#9467bd" if k == 2 else 'k') )  for k in targets ]
print(color)
for i in range(6):
    for j in range(i+1,6):
        subplot(5,5,i*5+j)
        scatter(X[:,j],X[:,i], color=color,s=21)
        if j == i+1:
            ylabel(f'PCA{i+1}',fontsize=14)
            xlabel(f'PCA{j+1}',fontsize=14)
subplot(5,5,20+1)
plot(arange(6)+1,pca.singular_values_,'k-',lw=3)
ylabel("Singular Values",fontsize=14)
ylim(bottom=0)
subplot(5,5,20+2)
bar(arange(6)+1,pca.explained_variance_ratio_*100)
ylabel("Explained variance %",fontsize=14)
ylim(bottom=0)
show()
