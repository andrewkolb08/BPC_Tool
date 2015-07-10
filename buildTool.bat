REM This script will do all the work necessary to create
REM a working visualizationTool executable.
REM It requires visualizationTool.spec and pyinstaller

pyinstaller --icon='.\BP_Picture.ico' BPC_Tool.spec
