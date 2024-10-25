import sys
import os
from threading import Lock, Event
from typing import List
import time
from threading import Thread

class PipelineReport():
    def __init__(self, pipeline_steps: List[str], ):
        self.steps: List[str] = pipeline_steps
        self.steps_current: dict = {step: 0 for step in pipeline_steps}
        self.steps_total: dict = {step: 0 for step in pipeline_steps}
        

class ProgressReporter():
    def __init__(self, lock: Lock, steps: List[str], stop_event: Event =  None):
        self.pipeline_report = PipelineReport(steps)
        self.lock = lock
        self.stop_event = stop_event
        
    def init_step(self, step_name: str, total_tasks: int):
        if step_name not in self.pipeline_report.steps:
            raise ValueError(f"Step {step_name} not found in pipeline")
        
        if total_tasks < 0:
            raise ValueError(f"Total tasks must be greater than 0")
        
        with self.lock:
            self.pipeline_report.steps_total[step_name] = total_tasks
            self.pipeline_report.steps_current[step_name] = total_tasks
    
    def update(self, step_name: str, finished_tasks: int = 1):
        with self.lock:
            if step_name not in self.pipeline_report.steps:
                raise ValueError(f"Step {step_name} not found in pipeline")
            if finished_tasks < 0:
                raise ValueError(f"Finished tasks must be greater than 0")
            if finished_tasks > self.pipeline_report.steps_total[step_name]:
                raise ValueError(f"Finished tasks must be less than total tasks")
            if self.pipeline_report.steps_current[step_name] - finished_tasks  < 0:
                raise ValueError(f"finished tasks cannot exceed total tasks")
            
            self.pipeline_report.steps_current[step_name] -= finished_tasks
    
    def report(self):
        while True:
            with self.lock:
                os.system('cls' if os.name == 'nt' else 'clear')
                for step in self.pipeline_report.steps:
                    current = self.pipeline_report.steps_total[step] - self.pipeline_report.steps_current[step]
                    total = self.pipeline_report.steps_total[step]
                    progress = int((current / total) * 50) if total > 0 else 0
                    progress_bar = '[' + '\033[92m' + '#' * progress + '\033[0m' + ' ' * (50 - progress) + ']'
                    sys.stdout.write(f'{step:<20}: {progress_bar} {current}/{total}\n')
                
                sys.stdout.flush()
            
            if self.stop_event and self.stop_event.is_set():
                break
                
            time.sleep(0.25)
           