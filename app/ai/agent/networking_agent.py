"""
Pontia Connect Networking Agent.
Built with Google Cloud's Agent Development Kit (ADK) and Gemini 
Enterprise Agent Platform.
"""

from google.adk import Agent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types

from app.ai.agent.tools import get_attendee_info, search_recent_company_news
from app.config import get_settings

USER_ID = "user_1"
APP_NAME = "pontia-connect-app"

class NetworkingAgent:
    """
    The main networking agent orchestrated using the Agent Development Kit (ADK).
    """
    def __init__(self):
        settings = get_settings()
        self.adk_agent = Agent(
            name="PontiaConnectNetworkingAgent",
            model=settings.AGENT_MODEL,
            instruction=settings.AGENT_SYSTEM_PROMPT,
            tools=[get_attendee_info, search_recent_company_news]
        )
        self.sessions = InMemorySessionService()
        self.runner = Runner(
            agent=self.adk_agent, 
            app_name=APP_NAME,
            session_service=self.sessions
        )

    async def generate_networking_strategy(self, attendee_name: str):
        """
        Executes the reasoning loop. In a local testing context, it processes directly.
        """
        prompt = f"Help me create a networking strategy for the attendee named {attendee_name}."
        session = await self.sessions.create_session(
            app_name = APP_NAME, 
            user_id = USER_ID
        )
        message = types.Content(
            role="user", 
            parts=[types.Part(text=prompt)]
        )

        async for event in self.runner.run_async(user_id=USER_ID, session_id=session.id, new_message=message):
            yield event


# ADK Deployment Script Helper
def deploy_agent_to_agent_engine(project_id: str, location: str) -> str:
    """
    Deploys the agent to the Gemini Enterprise Agent Platform.
    In ADK 2.0, deployment is executed via the command-line interface (CLI) 
    rather than a Python class to ensure proper containerization.
    """
    deploy_command = f"adk deploy cloud_run --project {project_id} --region {location}"
    deploy_command = f"adk deploy cloud_run --project {project_id} --region {location}"
    print(f"Deployment command: \n    {deploy_command}\n")
    return deploy_command