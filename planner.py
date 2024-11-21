import asyncio
from typing import List
from common_models import Question
from openai_client_factory import OpenAIClientFactory
from response_formats.planned_steps import PlanChunk, PlanSteps


class Planner:
    def __init__(self, openai_client_factory: OpenAIClientFactory = None, ):
        self.openai_client_factory = openai_client_factory

    async def plan(self, question: Question, chunks, prev_plan: List[PlanSteps]) -> List[PlanChunk]:
        plans_dict_list = [plan.to_dict() for plan in prev_plan]
        
        async def get_steps(question, chunk) -> PlanChunk:
            prompt = (
                f"Task: {question.text}\n"
                f"Context: {chunk}\n"
                f"Previous Plan Steps: \n {plans_dict_list}\n"
                f"Exclude from the plan the steps that are overlapping with the pevious Plan Steps\n"
                "Output: Provide the steps needed to achieve the task in the following JSON format:\n"
                "{\n"
                '  "steps": [\n'
                '    {\n'
                '      "step_no": 1,\n'
                '      "description": "Description of step 1",\n'
                '      "category": "The category can be either of (Addition, Replacement or NoChange)",\n'
                '      "code" :\n'
                '       {\n'
                '           "before": "code before applying the change",\n'
                '           "after": "code after applying the change"\n'
                '       }\n,'
                '      "line_num": "the line number range of the code change 1-2"\n'
                '    },\n'
                '  ],\n'
                '  "file_name": "file name"\n'
                "}"
            )
            
            client = await self.openai_client_factory.get_client(question.models[0])
          
            
            response = await client.beta.chat.completions.parse(
                model=question.models[0],
                messages= [
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt}
                ],
                n=1,
                stop=None,
                temperature=0,
                response_format=PlanSteps
            )
            
            return PlanChunk(chunk, response.choices[0].message.parsed)
        
        tasks = []
        for chunk in chunks:
            tasks.append(get_steps(question, chunk))
        
        steps = await asyncio.gather(*tasks)
        
        return steps