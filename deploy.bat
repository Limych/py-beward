python -m unittest discover .\tests
@IF ERRORLEVEL 1 EXIT /b 1
del /Q dist\*
python setup.py bdist_wheel
python -m twine upload dist\*
