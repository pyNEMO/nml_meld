from setuptools import setup

setup(
      use_scm_version=True,

      packages=['pynemo_namelist_tool','pynemo_namelist_tool.tests'],
      
      install_requires=[''],
      
      include_package_data=True,
      #The data files that needs to be included in packaging
      package_data={'': ['tests/inputs/*.f90'],
                    
                    },
      #If files are needs outside the installed packages
      data_files=[],
      
      entry_points={
                    'console_scripts':[
                        'pynemo_nml=nmlmeld.pynemo_nml_exe:main'
                        ],
                    },
      )
