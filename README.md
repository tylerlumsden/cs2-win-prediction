Experimental programs for CS2 win prediction

# Files

The ```parse``` directory contains a Go module for extracting ticks (data points) from a CS2 demo.

```parsedemos.ps1``` is a PowerShell script which runs the ```parse.go``` program on all demos in the ```parse/demos``` directory, extracting data points for each demo into a .csv file located in the ```parse/csv``` directory.

```train_predictor.ipynb``` is a notebook which loads all data points in every csv contained in the ```parse/csv``` directory, and trains win prediction classifiers using these data points.

# Acknowledgements

All demo parsing is based on the CS2 parser developed by [@markus-wa](https://github.com/markus-wa) for the Go library [https://github.com/markus-wa/demoinfocs-golang]