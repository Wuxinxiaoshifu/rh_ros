from setuptools import setup, find_packages, Extension

extModule = Extension('fastPathIntersect',
                ['pathFinding/C/fastPathIntersect.c', 'pathFinding/C/geometry.c'])

setup(name='rhpathfinder',
      version='0.0.1',
      description='Path finding code for Rhinohawk project',
      author='Stephen Pheiffer',
      install_requires=[
          'numpy', 'typing',
      ],
      packages=find_packages(),
      ext_modules=[extModule])
