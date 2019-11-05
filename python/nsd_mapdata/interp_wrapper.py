import numpy as np
from scipy.ndimage import map_coordinates
from utils import isnotfinite

def isnotfinite(arr):
    res = np.isfinite(arr)
    np.bitwise_not(res, out=res)  # in-place
    return res


def interp_wrapper(vol, coords, interptype=None):
    """
     interp_wrapper(vol,coords,interptype)
    
     <vol> is a 3D matrix (can be complex-valued)
     <coords> is 3 x N with the matrix coordinates to interpolate at.
       one or more of the entries can be NaN.
     <interptype> (optional) is 'nearest' | 'linear' | 'cubic' | 'wta'.  default: 'cubic'.
    
     this is a convenient wrapper for ba_interp3.  the main problem with
     normal calls to ba_interp3 is that it assigns values to interpolation
     points that lie outside the original data range.  what we do is to 
     ensure that coordinates that are outside the original field-of-view
     (i.e. if the value along a dimension is less than 1 or greater than
     the number of voxels in the original volume along that dimension)
     are returned as NaN and coordinates that have any NaNs are returned
     as NaN.
    
     another feature is 'wta' (winner-take-all). this involves the assumption that 
     <vol> contains only discrete integers. each distinct integer is mapped
     as a binary volume (0s and 1s) using linear interpolation to each coordinate,
     the integer with the largest resulting value at that coordinate wins, and that
     coordinate is assigned the winning integer.
    
     we automatically convert <vol> and <coords> to double before calling
     ba_interp3.m because it requires double format.  the output from
     this function is also double.
    
     for complex-valued data, we separately interpolate the real and imaginary parts.
    
     history:
     2019/06/18 - add support for 'wta'.
     2016/04/28 - add support for complex-valued data.
     2011/03/19 - be explicit on double conversion and double output.
    
     example:
     vol = -getsamplebrain(1);
     [xx,yy,zz] = ndgrid(1:size(vol,1),1:size(vol,2),1:size(vol,3));
     xx = xx + 2;
     yy = yy + 8;
     newvol = reshape(ba_interp3_wrapper(vol,[flatten(xx); flatten(yy); flatten(zz)]),size(vol));
     figure; imagesc(makeimagestack(vol));
     figure; imagesc(makeimagestack(newvol));
    
     another example:
     vol = getsamplebrain(6);
     [xx,yy,zz] = ndgrid(1:size(vol,1),1:size(vol,2),1:size(vol,3));
     xx = xx + .7;
     yy = yy + 1.2;
     newvol = reshape(ba_interp3_wrapper(ang2complex(vol),[flatten(xx); flatten(yy); flatten(zz)]),size(vol));
     newvol = mod(angle(newvol),2*pi);
     figure; imagesc(makeimagestack(vol(:,:,1:2)),[0 2*pi]);    colormap(hsv); axis image;
     figure; imagesc(makeimagestack(newvol(:,:,1:2)),[0 2*pi]); colormap(hsv); axis image;
    """
    # input
    if interptype is None:
        # default
        interptype = 'cubic'
        order=3
    elif interptype == 'cubic':
        order=3
    elif interptype == 'linear':
        order=1
    elif interptype == 'nearest':
        order=0
    
    # convert vol to float (needed)
    # vol = vol.astype(np.float32)
    
    # bad locations must get set to NaN
    bad = np.any(isnotfinite(coords), axis=0)
    coords[:, bad] = 1

    # out of range must become NaN, too   [ba_interp3 replicates the edge values which is not what we want]
    bad = np.any(np.c_[bad, \
                       coords[0,:] < 1, \
                       coords[0,:] > vol.shape[0],\
                       coords[1,:] < 1, \
                       coords[1,:] > vol.shape[1], \
                       coords[2,:] < 1, \
                       coords[2,:] > vol.shape[2]], axis=1).astype(bool)

    # resample the volume
    if not np.any(np.isreal(vol)):
        # we interpolate the real and imaginary parts independently
        """
        TODO
        f = copymatrix( ...
                complex(ba_interp3(double(real(vol)),double(coords(2,:)),double(coords(1,:)),double(coords(3,:)),interptype), ...
                        ba_interp3(double(imag(vol)),double(coords(2,:)),double(coords(1,:)),double(coords(3,:)),interptype)), ...
                bad,NaN);
        """
        
    else:
        # this is the tricky 'wta' case
        if interptype=='wta':
            
            """
            TODO
            
            # figure out the discrete integer labels
            alllabels = np.unique(vol.ravel())
            assert(np.all(np.isfinite(alllabels)))
            if length(alllabels) > 1000
            warning('more than 1000 labels are present');
            end
            
            # loop over each label
            allvols = zeros([length(alllabels) size(coords,2)]);
            for p=1:length(alllabels)
            allvols(p,:) = ba_interp3(double(vol==alllabels(p)),double(coords(2,:)),double(coords(1,:)),double(coords(3,:)),'linear');
            end
            
            # which coordinates have no label contribution?
            realbad = sum(allvols,1)==0;
            
            # perform winner-take-all (f0 is the index relative to alllabels!)
            [mx,f0] = max(allvols,[],1);
        
            # figure out the final labeling scheme
            f = alllabels(f0);
        
            # fill in NaNs for coordinates with no label contribution and bad coordinates too
            f(realbad) = NaN;
            f(bad) = NaN;
            """

        # this is the usual easy case
        else:

            transformeddata = map_coordinates(np.nan_to_num(vol).astype(np.float64), coords, order=order, mode='nearest')
            transformeddata[bad] = np.nan
       
    return transformeddata