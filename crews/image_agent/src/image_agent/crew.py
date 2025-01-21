from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from .tools.dalle_tool import get_dalle_tool

@CrewBase
class ImageAgentCrew():
    """Image Generation Crew for Renaissance-style scene prompts"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def scenic_artist(self) -> Agent:
        return Agent(
            config=self.agents_config['scenic_artist'],  # Matches the name in agents.yaml
            verbose=True
        )

    @agent
    def image_prompt_generator(self) -> Agent:
        return Agent(
            config=self.agents_config['image_prompt_generator'],
            verbose=True
        )

    @agent
    def dalle_artist(self) -> Agent:
        return Agent(
            config=self.agents_config['dalle_artist'],
            tools=[get_dalle_tool()],  # Add the DALL-E tool here
            verbose=True
        )

    @task
    def scenic_ideas_task(self) -> Task:
        return Task(
            config=self.tasks_config['scenic_ideas_task'],
            output_file='scenic_ideas.md'
        )

    @task
    def prompt_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['prompt_generation_task'],
            output_file='prompts.md'
        )

    @task
    def image_generation_task(self) -> Task:
        return Task(
            config=self.tasks_config['image_generation_task'],
            output_file='generated_images.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Image Generation Crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )