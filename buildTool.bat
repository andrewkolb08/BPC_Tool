REM This script will do all the work necessary to create
REM a working BPC_Tool executable.
REM It requires BPC_Tool.spec and pyinstaller

pyinstaller --icon='.\BP_Picture.ico' BPC_Tool.spec
