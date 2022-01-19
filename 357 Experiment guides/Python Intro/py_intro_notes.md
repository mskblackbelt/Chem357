# Python Introduction for Physical Chemistry

Students should end up with a feel for programming in Python and interacting with the JupyterHub/JupyterLab interface. Use MolSSI course for [Python Scripting for Computational Molecular Science](https://education.molssi.org/python_scripting_cms/) as a template. Basic skills students should have by the end of the exercise:

- Create a notebook
- Log on to Sugarcube, familiarize yourself with [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/user/interface.html) 
    - Create a new folder called "Introduction"
    - Copy the file `data.zip` from the `shared_jupyter_data` folder to your new folder and unzip it (right-click and select "Extract Archive". The file _must_ be in your own folder for this to work.)
    - Make a new Jupyter notebook in the folder. Make sure to change the title to follow the convention used in class
    - Change the first cell to a Markdown cell, give your notebook a title and brief description. For assistance, see the [CommonMark help page](https://commonmark.org/help/).
    	- Here is [another resource for learning about Markdown](https://docs.github.com/en/github/writing-on-github/getting-started-with-writing-and-formatting-on-github/basic-writing-and-formatting-syntax).
    - Evaluate that cell using <kbd>Shift</kbd> + <kbd>Return</kbd> 
- Perform basic arithmetic operations
- Assign a value to a variable
- Define a simple function
	- Calculate the value of an equation? Fibonacci sequence?
- Import a:
	- library
	- function from a library
- Work with the file system (use [`pathlib`](https://realpython.com/python-pathlib/))
	- Navigate and list files
	- Read a text file
	- Write a file
- Work with tabular data
	- Read in tabular data using `numpy` functions
	- Work with data in `numpy` arrays
- Plot data using `matplotlib`
	- Create a dataset using a function
	- Create a plot from a dataset
	- Label plot axes, title, legend, etc.
	- Plot multiple graphs in one figure 
	- Save figure to a file

Should this content be separated from the plotting lesson? Or should plotting follow naturally on from this? 
