import os
import pyproj
import cmocean
import netCDF4
import PIL.Image
import numpy as np
import matplotlib.pyplot as plt

from plotting import tile


#nc_to_xarray(ncfilelist)
  #return xarray_object

#plot_roms (xarray)

def plot_roms(ncfile: str, target: str, varname: str, crop: bool = True, zoom: int = 10):
    '''Plot roms output'''

    EPSG3857 = pyproj.Proj('EPSG:3857')
    TILE3857 = tile.Tile3857()

    with netCDF4.Dataset(ncfile) as nc:

        # Extract spatial variables
        lon = nc.variables['lon_rho'][:]
        lat = nc.variables['lat_rho'][:]
        msk = nc.variables['mask_rho'][:]
        lo,la = EPSG3857(lon,lat) # project EPSG:4326 to EPSG:3857 (web mercator)

        # temporal
        time = nc.variables['ocean_time']
        time = netCDF4.num2date(time[:], units=time.units)

        # data
        data = nc.variables[varname]
        d = data[:]

        # image size based on tiles
        mla = la[msk == 0]
        mlo = lo[msk == 0]
        lrt = TILE3857.tile(mlo.max(), mla.min(), zoom)
        lrb = TILE3857.bounds(*lrt)
        ult = TILE3857.tile(mlo.min(), mla.max(), zoom)
        ulb = TILE3857.bounds(*ult)
        ntx = lrt[0] - ult[0] + 1 # number of tiles in x
        nty = lrt[1] - ult[1] + 1 # number of tiles in y

        # loop times in file
        for t in range(len(time)):

            d = d[t, :] # select time

            # check for vertical coordinate
            if d.ndim > 2:
                d = d[-1,:] # surface is last in ROMS

            # apply mask
            d = np.ma.masked_where(msk == 0, d)

            # pcolor uses surrounding points, if any are masked, mask this cell
            #   see https://matplotlib.org/api/_as_gen/matplotlib.pyplot.pcolor.html
            d[:-1,:] = np.ma.masked_where(msk[1:,:] == 0, d[:-1,:])
            d[:,:-1] = np.ma.masked_where(msk[:,1:] == 0, d[:,:-1])

            # image size/resolution
            #dpi = 256
            dpi = 96   # suitable for screen and web
            height = nty * dpi
            width  = ntx * dpi

            fig = plt.figure(dpi=dpi, facecolor='none', edgecolor='none')
            fig.set_alpha(0)
            fig.set_figheight(height/dpi)
            fig.set_figwidth(width/dpi)

            ax = fig.add_axes([0., 0., 1., 1.], xticks=[], yticks=[])
            ax.set_axis_off()

            # pcolor
            pcolor = ax.pcolor(lo, la, d, cmap=plt.get_cmap('viridis'), edgecolors='none', linewidth=0.05)

            ax.set_frame_on(False)
            ax.set_clip_on(False)
            ax.set_position([0, 0, 1, 1])

            # set limits based on tiles
            ax.set_xlim(ulb[0], lrb[2])
            ax.set_ylim(lrb[1], ulb[3])

            # File output
            origfile = ncfile.split('/')[-1][:-3]
            filename = f'{target}/{origfile}_{varname}.png' 
            fig.savefig(filename, dpi=dpi, bbox_inches='tight', pad_inches=0.0, transparent=True)

            plt.close(fig)

            if crop:
                with PIL.Image.open(filename) as im:
                    zeros = PIL.Image.new('RGBA', im.size)
                    im = PIL.Image.composite(im, zeros, im)
                    bbox = im.getbbox()
                    crop = im.crop(bbox)
                    crop.save(filename, optimize=True)


if __name__ == '__main__':
  main()
