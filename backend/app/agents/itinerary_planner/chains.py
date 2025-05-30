from datetime import datetime
from typing import Optional, List, Any
from pydantic import BaseModel, Field
from langchain_core.prompts import load_prompt, ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from langchain_google_genai import ChatGoogleGenerativeAI
from app.config import config


class ItineraryInformation(BaseModel):
    """Information about the itinerary."""

    places: List[str] = Field(
        description="Which places does the user want to visit. A minimum of 5 locations is required. Be sure to have users select at least five places.",
        min_length=5,
    )
    departure: str = Field(description="When does the user want to leave")
    durations: int = Field(description="How many days will the user be traveling")
    companions: bool = Field(description="Who will be joining the user on this trip")


def create_itinerary_info_gather_chain(
    model_name: str, selected_places: Any
) -> RunnableSequence:

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    elif model_name == "gemini-1.5-flash":
        model = ChatGoogleGenerativeAI(model=model_name, temperature=0.1)
    elif model_name == "gpt-4.1-mini":
        model = ChatOpenAI(model=model_name, temperature=0.1)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)

    model = model.bind_tools([ItineraryInformation])

    prompt = load_prompt("app/prompts/itinerary_gather.yaml").template

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("messages"),
        ]
    )

    prompt = prompt.partial(
        current_date=datetime.now().strftime("%Y-%m-%d"),
        current_time=datetime.now().strftime("%H:%M:%S"),
        selected_places=selected_places,
    )

    chain = prompt | model

    return chain


def create_itinerary_planner_chain(
    model_name: str, selected_places: Any
) -> RunnableSequence:

    if model_name == "o3-mini":
        model = ChatOpenAI(model=model_name, temperature=1.0)
    else:
        model = ChatOpenAI(model=model_name, temperature=0.2)

    prompt = load_prompt("app/prompts/itinerary_planner.yaml").template

    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", prompt),
            MessagesPlaceholder("messages"),
        ]
    )

    prompt = prompt.partial(
        current_date=datetime.now().strftime("%Y-%m-%d"),
        current_time=datetime.now().strftime("%H:%M:%S"),
        selected_places=selected_places,
    )

    chain = prompt | model

    return chain
