#!/usr/bin/env python3

# pip install pandas typer

# import
import sys
import pandas as pd
from datetime import timedelta
import typer

dvr_script = None
resolve = None
project_manager = None
project = None
timeline = None

# ------------------------- loading davinci resolve api script -------------------------

def load_source(module_name, file_path):
    if sys.version_info[0] >= 3 and sys.version_info[1] >= 5:
        import importlib.util

        module = None
        spec = importlib.util.spec_from_file_location(module_name, file_path)
        if spec:
            module = importlib.util.module_from_spec(spec)
        if module:
            sys.modules[module_name] = module
            spec.loader.exec_module(module)
        return module
    else:
        import imp
        return imp.load_source(module_name, file_path)

try:
    import DaVinciResolveScript as dvr_script
except ImportError:
    try:
        expectedPath = "/opt/resolve/Developer/Scripting/Modules/"
        load_source('DaVinciResolveScript', expectedPath + "DaVinciResolveScript.py")
        import DaVinciResolveScript as dvr_script
    except Exception as ex:
        print("Unable to find module DaVinciResolveScript - please ensure that the module DaVinciResolveScript is discoverable by python")
        print("For a default DaVinci Resolve installation, the module is expected to be located in: " + expectedPath)
        print(ex)
        sys.exit(1)

# ------------------------- resolve api connection stuff -------------------------

resolve = dvr_script.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

# ------------------------- srt file functions -------------------------

def srt2df(file_path):
    df = pd.DataFrame(columns=['id', 'start', 'end', 'text'])

    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()

    # Split the content into subtitle blocks
    subtitle_blocks = content.strip().split('\n\n')

    for block in subtitle_blocks:
        lines = block.split('\n')
        if len(lines) >= 3:  # Ensure we have at least index, timestamp, and text

            nid = int(lines[0])

            timestamp = lines[1]
            text = '\n'.join(lines[2:])  # Join all text lines

            # Extract start time
            start_time = timestamp.split(' --> ')[0]
            end_time = timestamp.split(' --> ')[1]
            
            # Convert time to seconds
            h, m, s = start_time.replace(',', '.').split(':')
            startTime_seconds = float(h) * 3600 + float(m) * 60 + float(s)

            h, m, s = end_time.replace(',', '.').split(':')
            endTime_seconds = float(h) * 3600 + float(m) * 60 + float(s)

            # Append to dataframe
            new_index = len(df)
            df.loc[new_index] = [nid, startTime_seconds, endTime_seconds, text]

    return df

def df2srt(df, file_path):
    with open(file_path, 'w', encoding='utf-8') as file:
        for index, row in df.iterrows():

            nid = row['id']

            if nid == 0:
                continue
            
            start_time = timedelta(seconds=row['start'])
            hours, remainder = divmod(start_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = start_time.microseconds // 1000
            start_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

            end_time = timedelta(seconds=row['end'])
            hours, remainder = divmod(end_time.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            milliseconds = end_time.microseconds // 1000
            end_time_str = f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

            # Write subtitle entry
            file.write(f"{nid}\n")
            file.write(f"{start_time_str} --> {end_time_str}\n")
            file.write(f"{row['text']}\n\n")

# ------------------------- resolve timeline functions -------------------------

# find a video track with the name marker and extract the text from the Text+ track item to a dataframe
def timelineText2df(timeline, marker):
    df = pd.DataFrame(columns=['id', 'start', 'end', 'text'])
    if timeline:
        track_count = timeline.GetTrackCount("video")
        for i in range(1, track_count + 1):
            track = timeline.GetItemListInTrack("video", i)
            if track:
                track_name = timeline.GetTrackName("video", i)
                if track_name == marker:
                    nid = 1
                    for item in track:
                        if item.GetName() == "Text+":
                            start_time = item.GetStart() / timeline.GetSetting('timelineFrameRate')
                            end_time = item.GetEnd() / timeline.GetSetting('timelineFrameRate')
                            fusion_comp = item.GetFusionCompByIndex(1)
                            if fusion_comp:
                                text_tool = fusion_comp.FindToolByID("TextPlus")
                                if text_tool:
                                    text_content = text_tool.GetInput("StyledText")
                                    new_index = len(df)
                                    df.loc[new_index] = [nid, start_time, end_time, text_content]
                                    nid += 1
    return df

# find a video track with the name marker and update the text+ track item witht he text from the dataframe
def df2timelineText(df, timeline, marker):
    if timeline:
        track_count = timeline.GetTrackCount("video")
        for i in range(1, track_count + 1):
            track = timeline.GetItemListInTrack("video", i)
            if track:
                track_name = timeline.GetTrackName("video", i)
                nid = 1
                if track_name == marker:
                    for item in track:
                        if item.GetName() == "Text+":
                            start_time = item.GetStart() / timeline.GetSetting('timelineFrameRate')
                            end_time = item.GetEnd() / timeline.GetSetting('timelineFrameRate')
                            fusion_comp = item.GetFusionCompByIndex(1)
                            if fusion_comp:
                                text_tool = fusion_comp.FindToolByID("TextPlus")
                                # print("A")
                                if text_tool:
                                    # print("B")
                                    for index, row in df.iterrows():
                                        if row['id'] == nid:
                                            text_tool.SetInput("StyledText", row['text'])
                                            nid += 1
                                            break

# ------------------------- app -------------------------

app = typer.Typer()

@app.command(help="Export text from timeline to srt file")
def export(path: str, track: str):
    df = timelineText2df(timeline, track)
    df2srt(df, path)

@app.command(help="Update timeline with srt file")
def update(path: str, track: str):
    df = srt2df(path)
    df2timelineText(df, timeline, track)

@app.command(help="Update timeline with srt file and render video")
def render(path: str, track: str):
    df = srt2df(path)
    df2timelineText(df, timeline, track)
    rid = project.AddRenderJob()
    project.StartRendering(rid, isInteractiveMode=False)

if __name__ == '__main__':
    app()
