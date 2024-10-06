#!/usr/bin/env python3

# pip install pandas dearpygui
# python -m pip install pandas dearpygui

import sys
import pandas as pd
from datetime import timedelta
import typer
import dearpygui.dearpygui as dpg
import os
import textp2srt as t2s

# Import DaVinci Resolve script
dvr_script = None
resolve = None
project_manager = None
project = None
timeline = None

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
        dpg.create_context()
        with dpg.window(label="Error"):
            dpg.add_text("Unable to find module DaVinciResolveScript. Please ensure that the module is discoverable by Python.")
            dpg.add_button(label="OK", callback=lambda: dpg.stop_dearpygui())
        dpg.create_viewport(title="Error", width=400, height=200)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()
        sys.exit(1)

resolve = dvr_script.scriptapp("Resolve")
project_manager = resolve.GetProjectManager()
project = project_manager.GetCurrentProject()
timeline = project.GetCurrentTimeline()

def get_video_tracks():
    global timeline
    timeline = project.GetCurrentTimeline() # get timeline again in case it changed since the last call
    track_count = timeline.GetTrackCount("video")
    return [timeline.GetTrackName("video", i) for i in range(1, track_count + 1)]

def main():
    dpg.create_context()

    def execute_callback():
        track = dpg.get_value("track")
        file_path = os.path.join(dpg.get_value("directory"), dpg.get_value("file_name"))
        if not track or not file_path:
            dpg.set_value("status", "Please select a track, directory, and file name.")
            return
        
        selected_mode = dpg.get_value("Mode")
        print(f"Selected mode: {selected_mode}")  # Debug print
        if selected_mode == "Export":
            print("Exporting...")
            df = t2s.timelineText2df(timeline, track)
            t2s.df2srt(df, file_path)
        elif selected_mode == "Update":
            print("Updating...")
            df = t2s.srt2df(file_path)
            t2s.df2timelineText(df, timeline, track)
        else:
            print(f"Unexpected mode: {selected_mode}")
        dpg.set_value("status", f"Operation completed: {selected_mode}")

    def directory_dialog():
        dpg.add_file_dialog(
            directory_selector=True, show=False,
            callback=lambda s, a, u: dpg.set_value("directory", a['file_path_name']),
            tag="directory_dialog"
        )

    def update_tracks():
        tracks = get_video_tracks()
        dpg.configure_item("track", items=tracks)
        dpg.set_value("status", "Tracks updated")

    with dpg.window(label="TextPlus2SRT", tag="TextPlus2SRT"):
        dpg.add_radio_button(label="Mode", items=["Export", "Update"], default_value="Export", horizontal=True, tag="Mode", callback=lambda: dpg.configure_item("render", show=dpg.get_value("Mode") == "Update"))
        
        dpg.add_text("Track")
        with dpg.group(horizontal=True):
            dpg.add_combo(items=get_video_tracks(), tag="track")
            dpg.add_button(label="Update", callback=update_tracks)
        
        dpg.add_text("Working Directory")
        with dpg.group(horizontal=True):
            dpg.add_input_text(tag="directory", default_value=os.getcwd())
            dpg.add_button(label="Select Directory", callback=lambda: dpg.show_item("directory_dialog"))
        
        dpg.add_text("SRT File Name")
        dpg.add_input_text(tag="file_name", default_value="subtitle.srt")

        dpg.add_button(label="Execute", callback=execute_callback)
        dpg.add_text("", tag="status")

    directory_dialog()

    dpg.create_viewport(title="Text+2SRT", width=500, height=300)
    dpg.setup_dearpygui()
    dpg.show_viewport()
    print(dpg.set_primary_window("TextPlus2SRT", True))
    dpg.start_dearpygui()
    dpg.destroy_context()

if __name__ == "__main__":
    main()
