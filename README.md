[My website](www.jaspercorcoran.com)

# control_rig_builder
Code samples and project breakdown for my bi-directional control rig builder in Autodesk Maya. Covers my technical art tool philosophy, and software design strategies with Python for animation pipelines.

This breakdown will cover more of the Python and Software Design aspects of my control rig pipeline tools. For a Maya side example, check out my Technical Artist Portfolio: www.jaspercorcoran.com

For my pipeline tools I am above all designing with the goal to make the tool easy to use by artists, and easy to extend by programmers. Project goals and requirements vary widely, so tools planned for adaptibility and longevity are most likely to be kept and used in a pipeline.

## PySide UI

The majority of my tools are packaged into Pyside2 UIs designed under the assumption that the user will not be expected to interact with the unerlying Python logic. I've worked with control rig systems that were did not have a user interface, so creating a rig required scripting familiarity and the need to dig through the documentation to get up and running. In my tool, interactions with the UI essentially build out that Python script by choosing functions and class instances, allowing the rigs to exist as exportable and writable templates behind the scenes (more on that later).

I am taking advantage of class inheritence throughout this tool, my UIs being the first of these parent child heirarchies. I have a base class that extends the QMainWindow, and is a module that is common to all of my tools to make default parameters predicatble in all of my tools. Based on a GDC talk from Muhammad Bin Tahir Mir, I enforce abstract class decorators and NotImplementedError where possible. This makes it so if a developer wants to make a new tool in my pipeline, there are basic parameters that are needed that create a sense of uniformity with all tools.

As a general design rule, I have made it a goal to have no cmds or OpenMaya imports in any of my UIs. This forces a decoupling of responsiblity, where UI classes are only dealing with PySide2 widgets and commands, and any maya related functionality is passed on to helper modules. I find this sets a good standard for what the UI class is actually responsible for.

Now moving on to the main logic of the modules

## Designing for Developer Extensibility

```python 
your_code = do_some_stuff
```

## Designing for Artists

My control rigs are built by thinking of a creature being rigged as a collection of body part classes, instead of one giant character. Writing a script to handle just the current human project is not considering the four armed character that is next on the to do list. Modularity is the most popular solution for control rig scripts, and I've used this as my foundational approach.



