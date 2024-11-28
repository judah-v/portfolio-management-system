# Check for dependencies and install any that are missing
# Note: This application assumes a local MySql server with 
#       the database 'portfolio_management' created.
#       Even after installing these dependecies, if that
#       server and/or database doesn't exist, the program will not run

import subprocess

dependencies = [
    'tkinter', 
    'webbrowser',
    'mysql',
    'qrcode',
    'threading',
    'flask',
    'signal'
    ]

for mod in dependencies:
    try:
        exec(f'import {mod}')
    except ModuleNotFoundError as e:
        cmd = f"pip install {mod}"
        if mod == 'mysql':
            cmd = f"pip install {mod}-connector"

        subprocess.run(cmd, shell=True)
