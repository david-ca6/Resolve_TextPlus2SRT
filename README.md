# TextPlus2SRT (tp2srt)
TextPlus2SRT (tp2srt) is a Python script that allows you to export Text+ from a DaVinci Resolve track to a .srt file, and update the timeline with text from a .srt file.  
It uses the DaVinci Resolve API, pandas libraries and typer libraries.

## Use case
- Export text from a DaVinci Resolve track to a .srt file to upload to a video hosting platform (YouTube) for accessibility.
- Easier translation of subtitles. It's easier to translate a .srt file than to go through all the Text+ item on a track.
- Export .srt file for backup. It's nice to have a .srt file in case something happens to the project files.

## Requirements
Youneed to have the pandas and typer libraries installed.  
You can install them using pip:
```
pip install pandas typer
```

## Usage

### CLI
To use TextPlus2SRT, you need to have DaVinci Resolve installed and running. 

Once you have the necessary dependencies, you can run the script from the command line. There are three commands available:

1. `export`: This command exports text from a specified track in the timeline to a .srt file. You need to provide the path to the .srt file and the name of the track.  
    For example to export the track named "EN" to the file "test.srt" you can do:
    ```
    python textp2srt.py export test.srt EN
    ```

2. `update`: This command updates the text in a specified track in the timeline with the text from a .srt file. You need to provide the path to the .srt file and the name of the track.
    For example to update the track named "EN" with the text from the file "test.srt" you can do:
    ```
    python textp2srt.py update test.srt EN
    ```

3. `render`: This command updates the text in a specified track in the timeline with the text from a .srt file, and then starts rendering the project. You need to provide the path to the .srt file and the name of the track.
    For example to update the track named "EN" with the text from the file "test.srt", then render the project, you can do:
    ```
    python textp2srt.py render test.srt EN
    ```

The script is designed to be used in a command line environment, but it can also be integrated into other Python scripts or applications.

### GUI

The GUI version is a simple application that allows you to export text from a DaVinci Resolve track to a .srt file, and update the timeline with text from a .srt file.

To run the GUI version, you need to have the necessary dependencies installed. You can install them using pip:
```
pip install pandas typer dearpygui
```

Then you can run the script from the command line:
```
python textp2srtG.py
```

