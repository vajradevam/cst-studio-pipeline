from cx_Freeze import setup, Executable

base = "Win32GUI"    

executables = [Executable("main.py", base=base)]

packages = ["idna", "numpy", "customtkinter", "__future__", "csv"]
options = {
    'build_exe': {    
        'packages':packages,
    },    
}

setup(
    name = "CST Studio 2020 Data Pipeline",
    options = options,
    version = "0.0.1",
    description = '©Vajradevam S., Neptunes Aerospace, 2024',
    executables = executables
)