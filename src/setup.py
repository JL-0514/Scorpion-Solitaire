from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'packages': [], 
    'excludes': [],
    'optimize': 2,
    'includes': ['Card', 'CardSet', 'GameCanvas']
}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable('GameMain.py', base=base, target_name = 'ScorpionSolitaire')
]

setup(name='Scorpion Solitaire',
      version = '1.0',
      description = 'A scorpion solitaire game.',
      options = {'build_exe': build_options},
      executables = executables)
