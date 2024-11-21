import asyncio
from typing import Any, Callable, Coroutine, List
from response_formats.planned_steps import PlanChunk, PlanSteps,Step, StepCategory
import re

class StepsExecutor:
    
    def get_action(self, category: str) -> Callable[[Step], Coroutine[Any, Any, None]]:
        return {
            StepCategory.Addition: self._addition,
            StepCategory.Replacement: self._replacement,
            StepCategory.NoChange: self._noop
        }[category]
        
    async def _addition(self, lines: List[str], line_indices: List[int], step: Step):
        if step.category == StepCategory.Addition:
            line_count_before = len(lines)
            for index in reversed(line_indices):
                for line in step.code.after.split('\n'):
                    lines.insert(index, line + '\n')
            line_count_after = len(lines)
            
        return (lines, line_count_after - line_count_before)
        
        
    async def _replacement(self, lines: List[str], line_indices: List[int], step: Step):
        
        line_count_before = len(lines)
        for index in line_indices:
            if 0 <= index < len(lines):
                lines[index:index+1] = [line + '\n' for line in step.code.after.split('\n')]
        line_count_after = len(lines)
         
        return (lines, line_count_after - line_count_before)
    
    async def _deletion(self, lines: List[str], line_indices: List[int], step: Step):
        line_count_before = len(lines)
        for index in sorted(line_indices, reverse=True):
            if 0 <= index < len(lines):
                del lines[index]
        line_count_after = len(lines)
        
        return (lines, line_count_after - line_count_before)
    
    async def _noop(self, lines: List[str], line_indices: List[int], step: Step):
        print(f"Noop: {step.step_no}, description: {step.description}")
        pass
    
    def _extract_content(self, text):
        pattern = r'<BEGIN_FILE_CONTENT>(.*?)<END_FILE_CONTENT>'
        match = re.search(pattern, text, re.DOTALL)
        if match:
            return match.group(1).strip()
        return None

    async def execute(self, plans: List[PlanChunk]):
        async def exec_file_actions(plan_chunk: PlanChunk):
            
            lines = self._extract_content(plan_chunk.chunk).split('\n')
            
            for step in sorted(plan_chunk.plan.steps, key=lambda s: s.step_no):
                lines_diff = 0
                print(f"\n Executing step: {step.step_no}, description: {step.line_num}")
                try:
                    if(step.category == StepCategory.NoChange or step.line_num == 'N/A'):
                        continue
                    
                    if '-' in step.line_num:
                        start, end = map(int, step.line_num.split('-'))
                        line_indices = range(start + lines_diff - 1, end)
                    else:
                        if 'L' in step.line_num:
                            line_indices = [int(step.line_num[1:]) + lines_diff - 1]
                        else:
                            line_indices = [int(step.line_num) + lines_diff - 1]

                    (lines, diff) = await self.get_action(step.category)(lines, line_indices, step)
                    lines_diff = diff
                except Exception as e:
                    print(f"Error in step: {step.step_no}, description: {step.description}, \n Step: {step}")
                    print(e)
                    continue
            
            with open(plan_chunk.plan.file_name, 'w') as file:
                file.writelines(lines)
            
        actions_tasks = []            
        for plan in plans:
            actions_tasks.append(exec_file_actions(plan))
        
        await asyncio.gather(*actions_tasks)