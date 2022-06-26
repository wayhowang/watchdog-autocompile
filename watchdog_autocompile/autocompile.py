"""
pip install watchdog

watchmedo tricks tricks.yaml

tricks.yaml
-----------
tricks:
- autocompile.AutoCompileTrick:
    patterns: ["*"]
    ignore_patterns: []
    source_directory: "source_dir"
    build_directory: "target_dir"
    patterns_and_commands: 
    - pattern: ["*.py"]
      command: "echo compiling ${source}..."
    - pattern: ["*.py"]
      command: "python py3to2.py ${source} ${output}"
    - pattern: ["*.py"]
      command: "echo compilation done."

"""

import string
import shutil
import subprocess
from typing import AnyStr, Dict, Sequence, Tuple, Union
from watchdog.observers import Observer
from watchdog.events import *
from watchdog.tricks import Trick
from watchdog.utils.patterns import match_any_paths
import os
import os.path


class PathMapper:
    def __init__(self, source_dir: str, target_dir: str) -> None:
        self.source_dir = source_dir
        self.target_dir = target_dir

    def map(self, source_path: str) -> str:
        rel_path = os.path.relpath(source_path, self.source_dir)
        return os.path.join(self.target_dir, rel_path)

    def valid(self, source_path: str) -> bool:
        return not os.path.relpath(source_path, self.source_dir).startswith('..')


class AutoCompileTrick(Trick):
    def __init__(self, patterns=None, ignore_patterns=None, 
            source_directory='.', build_directory=None, 
            patterns_and_commands: Sequence[Dict[AnyStr, AnyStr]]=[]) -> None:

        if build_directory is None:
            raise Exception('build_directory cannot be None')
        
        if source_directory == build_directory:
            raise Exception('source_directory and build_directory cannot be same')

        super().__init__(
            patterns=patterns, ignore_patterns=ignore_patterns,
            ignore_directories=False)

        self.path_mapper = PathMapper(source_directory, build_directory)

        self.patterns_and_commands = patterns_and_commands

    def on_any_event(self, event):
        if not self.path_mapper.valid(event.src_path):
            return

    def on_moved(self, event: Union[DirMovedEvent, FileMovedEvent]):
        if not self.path_mapper.valid(event.src_path):
            return

        os.renames(self.path_mapper.map(event.src_path), self.path_mapper.map(event.dest_path))

    def on_created(self, event: Union[DirCreatedEvent, FileCreatedEvent]):
        if not self.path_mapper.valid(event.src_path):
            return

        target_path = self.path_mapper.map(event.src_path)
        if isinstance(event, DirCreatedEvent):
            os.makedirs(target_path)
        else:
            try:
                os.makedirs(os.path.dirname(target_path))
            except:
                pass
            with open(target_path, 'w'):
                pass
        
    def on_deleted(self, event: Union[DirDeletedEvent, FileDeletedEvent]):
        if not self.path_mapper.valid(event.src_path):
            return
        target_path = self.path_mapper.map(event.src_path)
        try:
            shutil.rmtree(target_path)
        except:
            pass


    def on_modified(self, event: Union[DirModifiedEvent, FileModifiedEvent]):

        if not self.path_mapper.valid(event.src_path):
            return

        if isinstance(event, DirModifiedEvent):
            return

        target_path = self.path_mapper.map(event.src_path)

        try:
            os.makedirs(os.path.dirname(target_path))
        except:
            pass

        context = {
            'source': event.src_path,
            'output': target_path
        }
        
        executed = False

        for patterns_and_command in self.patterns_and_commands:
            patterns = patterns_and_command.get('pattern')
            command = patterns_and_command.get('command')
            if match_any_paths([event.src_path], patterns, None, True):
                command = string.Template(command).safe_substitute(**context)
                self.process = subprocess.Popen(command, shell=True)
                self.process.wait()                
                executed = True

        if not executed:
            shutil.copy(event.src_path, self.path_mapper.map(event.src_path))

    def on_closed(self, event):
        if not self.path_mapper.valid(event.src_path):
            return
