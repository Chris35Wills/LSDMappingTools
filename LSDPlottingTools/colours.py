"""
A set of functions to perform modifications to matplotlib colourbars,
and colourmaps, beyond the core maplotlib colourbar/colourmap functionality.

Created on Thu Jan 12 14:33:21 2017

    Author: DAV
"""
from __future__ import absolute_import, division, print_function, unicode_literals

from six import with_metaclass

import numpy as _np
import matplotlib as _mpl
import matplotlib.pyplot as _plt
import matplotlib.gridspec as _gridspec
import matplotlib.colors as _mcolors
import matplotlib.cm as _cm
from array import array

from matplotlib.colors import LinearSegmentedColormap


def truncate_colormap(cmap, minval=0.0, maxval=1.0, n=-1):
    """
    Truncates a standard matplotlib colourmap so
    that you can use part of the colour range in your plots.
    Handy when the colourmap you like has very light values at
    one end of the map that can't be seen easily.

    Arguments:
      cmap (:obj: `Colormap`): A matplotlib Colormap object. Note this is not
         a string name of the colourmap, you must pass the object type.
      minval (int, optional): The lower value to truncate the colour map to. 
         colourmaps range from 0.0 to 1.0. Should be 0.0 to include the full 
         lower end of the colour spectrum.
      maxval (int, optional): The upper value to truncate the colour map to.
         maximum should be 1.0 to include the full upper range of colours.
      n (int): Leave at default. 
    
    Example:
       minColor = 0.00
       maxColor = 0.85
       inferno_t = truncate_colormap(_plt.get_cmap("inferno"), minColor, maxColor) 
    """
    cmap = _plt.get_cmap(cmap)
    
    if n == -1:
        n = cmap.N
    new_cmap = _mcolors.LinearSegmentedColormap.from_list(
         'trunc({name},{a:.2f},{b:.2f})'.format(name=cmap.name, a=minval, b=maxval),
         cmap(_np.linspace(minval, maxval, n)))
    return new_cmap
    
def discrete_colourmap(N, base_cmap=None):
    """Creates an N-bin discrete colourmap from the specified input colormap.
    
    Author: github.com/jakevdp adopted by DAV
    
    Note: Modified so you can pass in the string name of a colourmap
        or a Colormap object.

    Arguments: 
        N (int): Number of bins for the discrete colourmap. I.e. the number
            of colours you will get.
        base_cmap (str or Colormap object): Can either be the name of a colourmap
            e.g. "jet" or a matplotlib Colormap object
    """

    print(type(base_cmap))
    if isinstance(base_cmap, _mcolors.Colormap):
        base = base_cmap
    elif isinstance(base_cmap, str):
        base = _plt.cm.get_cmap(base_cmap)
    else:
        print("Colourmap supplied is of type: ", type(base_cmap))
        raise ValueError('Colourmap must either be a string name of a colormap, \
                         or a Colormap object (class instance). Please try again.')
        
    color_list = base(_np.linspace(0, 1, N))
    cmap_name = base.name + str(N)
    return base.from_list(cmap_name, color_list, N)
    
def cmap_discretize(N, cmap):
    """Return a discrete colormap from the continuous colormap cmap.
    
    Arguments:
        cmap: colormap instance, eg. cm.jet. 
        N: number of colors.

    Example:
        x = resize(arange(100), (5,100))
        djet = cmap_discretize(cm.jet, 5)
        imshow(x, cmap=djet)
    """

    if type(cmap) == str:
        cmap = _plt.get_cmap(cmap)
    colors_i = _np.concatenate((_np.linspace(0, 1., N), (0.,0.,0.,0.)))
    colors_rgba = cmap(colors_i)
    indices = _np.linspace(0, 1., N+1)
    cdict = {}
    for ki,key in enumerate(('red','green','blue')):
        cdict[key] = [ (indices[i], colors_rgba[i-1,ki], colors_rgba[i,ki])
                       for i in range(N+1) ]
    # Return colormap object.
    return _mcolors.LinearSegmentedColormap(cmap.name + "_%d"%N, cdict, 1024)
    

def colorbar_index(fig, cax, ncolors, cmap, drape_min_threshold, drape_max):
    """State-machine like function that creates a discrete colormap and plots
       it on a figure that is passed as an argument.

    Arguments:
       fig (matplotlib.Figure): Instance of a matplotlib figure object.
       cax (matplotlib.Axes): Axes instance to create the colourbar from. 
           This must be the Axes containing the data that your colourbar will be
           mapped from.
       ncolors (int): The number of colours in the discrete colourbar map.
       cmap (str or Colormap object): Either the name of a matplotlib colormap, or 
           an object instance of the colormap, e.g. cm.jet
       drape_min_threshold (float): Number setting the threshold level of the drape raster
           This should match any threshold you have set to mask the drape/overlay raster.
       drape_max (float): Similar to above, but for the upper threshold of your drape mask.
    """

    discrete_cmap = discrete_colourmap(ncolors, cmap)
    
    mappable = _cm.ScalarMappable(cmap=discrete_cmap)
    mappable.set_array([])
    #mappable.set_clim(-0.5, ncolors + 0.5)
    mappable.set_clim(drape_min_threshold, drape_max)
    
    print(type(fig))
    print(type(mappable))
    print(type(cax))
    print() 
    cbar = fig.colorbar(mappable, cax=cax)
    print(type(cbar))
    #cbar.set_ticks(_np.linspace(0, ncolors, ncolors))
    cbar.set_ticks(_np.linspace(drape_min_threshold, drape_max, ncolors+1))
    #cbar.set_ticklabels(range(ncolors))
    
    return cbar

def nonlinear_colormap():
    """Creates a non-linear colourmap from an existing colourmap.
    """
    pass

class nonlinear_colourmap(LinearSegmentedColormap):
    """Creates a non-linear colourmap from an existing colourmap.
    
    Author: DAV from http://protracted-matter.blogspot.ie/2012/08/nonlinear-colormap-in-matplotlib.html
    
    Todo:I don't think this works for imshow plots. Not sure exactly why.
         So unfortunately no use with drape plots :(
    """
    
    name = 'nlcmap'
        
    def __init__(self, cmap, levels):
        
        if isinstance(cmap, str):
            self.cmap = _cm.get_cmap(cmap)
        elif isinstance(cmap, _mcolors.Colormap):
            self.cmap = cmap
        else:
            raise ValueError('Colourmap must either be a string name of a colormap, \
                         or a Colormap object (class instance). Please try again.' \
                         "Colourmap supplied is of type: ", type(cmap))

        self.N = self.cmap.N
        self.monochrome = self.cmap.monochrome
        self.levels = _np.asarray(levels)#, dtype='float64')
        self._x = self.levels
        self.levmax = self.levels.max()
        self.levmin = self.levels.min()
        self.transformed_levels = _np.linspace(self.levmin, self.levmax,
             len(self.levels))

    def __call__(self, xi, alpha=1.0, **kw):
        yi = _np.interp(xi, self._x, self.transformed_levels)
        return self.cmap(yi / (self.levmax-self.levmin) + 0.5, alpha)

#    def __call__(self, xi, alpha=1.0, **kw):
#        yi = _np.interp(xi, self._x, self.transformed_levels)
#        return self.cmap(yi / self.levmax, alpha)
    
    @staticmethod
    def create_levels(tmin, tmax, sigma1, sigma2, t1mean, t2mean):
        """ Creates levels for the non-linear colourmap"""
        levels = _np.concatenate((
                    [tmin, tmax],
                    _np.linspace(t1mean - 2 * sigma1, t1mean + 2 * sigma1, 5),
                    _np.linspace(t2mean - 2 * sigma2, t2mean + 2 * sigma2, 5),
                    ))
        levels = levels[levels <= tmax]
        levels.sort()
        print(levels)
        return levels


class TransformedColourmap(object):
    """ Applies function (which should operate on vectors of shape 3:
    [r, g, b]), on colormap cmap. This routine will break any discontinuous
    points in a colormap.
    
    DOES NOT WORK!
    """
    def __init__(self, function, cmap):
        self.cdict = cmap._segmentdata
        
        step_dict = {}
        # Firt get the list of points where the segments start or end
        for key in ('red','green','blue'):
            step_dict[key] = map(lambda x: x[0], self.cdict[key])
            step_list = sum(step_dict.values(), [])
            step_list = array(list(set(step_list)))
        
        # Then compute the LUT, and apply the function to the LUT
        reduced_cmap = lambda step : array(cmap(step)[0:3])
        old_LUT = array(map( reduced_cmap, step_list))
        new_LUT = array(map( function, old_LUT))
        
        # Now try to make a minimal segment definition of the new LUT
        cdict = {}
        for i,key in enumerate(('red','green','blue')):
            this_cdict = {}
            for j,step in enumerate(step_list):
                if step in self.step_dict[key]:
                    this_cdict[step] = new_LUT[j,i]
                elif new_LUT[j,i]!=old_LUT[j,i]:
                    this_cdict[step] = new_LUT[j,i]
                    
            colorvector=  map(lambda x: x + (x[1], ), this_cdict.items())
            colorvector.sort()
            cdict[key] = colorvector

    def __call__(self, function, cmap):
        return _mcolors.LinearSegmentedColormap('colormap', self.cdict, 1024)


class MidpointNormalize(_mcolors.Normalize):
    """Custom normalise option to normalise data in non-linear ways.
    
    Pass the object returned from this function to the norm= argument in 
    plotting functions like imshow or pcolormesh.
    """
    def __init__(self, vmin=None, vmax=None, midpoint=None, clip=False):
        self.midpoint = midpoint
        _mcolors.Normalize.__init__(self, vmin, vmax, clip)

    def __call__(self, value, clip=None):
        # I'm ignoring masked values and all kinds of edge cases to make a
        # simple example...
        x, y = [self.vmin, self.midpoint, self.vmax], [0, 0.5, 1]
        return _np.ma.masked_array(_np.interp(value, x, y))    

        
class MetaColours(type):
    """A metclass for colourmaps making them all read-only attributes"""
    
    @property
    def niceterrain(cls):
        """ A terrain colour map that doesn't have the stupid blue colour for
            low lying land...
        """
        return cls._niceterrain

    @property
    def darkearth(cls):
        """ A terrain colour map that doesn't have the stupid blue colour for
            low lying land...
        """
        return cls._darkearth

#class UsefulColourmaps(object, metaclass=MetaColours):
class UsefulColourmaps(with_metaclass(MetaColours, object)):    
    """The interface for accessing usefulcolourmaps attributes"""
    _niceterrain = truncate_colormap("terrain", 0.25, 0.9)
    _darkearth = truncate_colormap("gist_earth", 0.25, 0.9)

#class UsefulColourmaps(object):
#    """A holding class for some useful custom colourmaps"""
#    
#    @property
#    def niceterrain():
#        niceterrain = truncate_colormap("terrain", 0.25, 0.9)
#        return niceterrain
    
    # That's all for now!
    
    
    
    