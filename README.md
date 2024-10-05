# TextPlus2SRT (tp2srt)
TextPlus2SRT (tp2srt) is a Python script that allows you to export Text+ from a DaVinci Resolve track to a .srt file, and update the timeline with text from a .srt file.  
It uses the DaVinci Resolve API, pandas libraries and typer libraries.

To use TextPlus2SRT, you need to have DaVinci Resolve installed and running. You also need to have the pandas and typer libraries installed. You can install them using pip:

```
pip install pandas typer
```

Once you have the necessary dependencies, you can run the script from the command line. There are three commands available:

1. `export`: This command exports text from a specified track in the timeline to a .srt file. You need to provide the path to the .srt file and the name of the track.

2. `update`: This command updates the text in a specified track in the timeline with the text from a .srt file. You need to provide the path to the .srt file and the name of the track.

3. `render`: This command updates the text in a specified track in the timeline with the text from a .srt file, and then starts rendering the project. You need to provide the path to the .srt file and the name of the track.

The script is designed to be used in a command line environment, but it can also be integrated into other Python scripts or applications.
