from setuptools import setup


# setup plotting
setup(name="plotting", 
      version='0.1.a',
      description='Plotting for ROMS',
      url='https://github.com/asascience/IOOS-cloud-IaC/python/plotting',
      author='RPS North America',
      author_email='rpsgroup.com',
      packages=['plotting'],
      install_requires=[
        'plotting',
        'pyproj',
        'cmocean',
        'numpy',
        'matplotlib',
        'netCDF4',
        'Pillow']
     )

# setup cluster

