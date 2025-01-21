from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class QuoteAgentCrew():
    """Quote Generation Crew for philosophical and literary quotes"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def author_selector(self) -> Agent:
        return Agent(
            config=self.agents_config['author_selector'],
            verbose=False
        )

    @agent
    def quote_provider(self) -> Agent:
        return Agent(
            config=self.agents_config['quote_provider'],
            verbose=False
        )

    @task
    def author_selection_task(self) -> Task:
        return Task(
            config=self.tasks_config['author_selection_task'],
            output_file='selected_author.md'
        )

    @task
    def quote_curation_task(self) -> Task:
        return Task(
            config=self.tasks_config['quote_curation_task'],
            output_file='quotes.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Quote Generation crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=False
        )