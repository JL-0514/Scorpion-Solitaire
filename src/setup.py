from cx_Freeze import setup, Executable

# Dependencies are automatically detected, but it might need
# fine tuning.
build_options = {
    'packages': [], 
    'excludes': [],
    'includes': ['Card', 'CardSet', 'GameCanvas'],
    'include_files': [('img', 'src/img')],
    'optimize': 2
}

import sys
base = 'Win32GUI' if sys.platform=='win32' else None

executables = [
    Executable(
        script='GameMain.py', 
        base=base, 
        target_name = 'Scorpion Solitaire',
    )
]

setup(name='Scorpion Solitaire',
      version = '1.0',
      description = 'A scorpion solitaire game.',
      options = {'build_exe': build_options},
      executables = executables)
