"""
=============================================================================
Vivia Mobility Parking Agent - LangSmith Evaluation
=============================================================================
Evaluates the parking agent with:
  - correctness
  - groundedness
  - relevance
  - retrieval_relevance
=============================================================================
"""

import os
from dotenv import load_dotenv
load_dotenv()
from schemas.agent_schema import ModeResponse

os.environ["LANGSMITH_API_KEY"] = os.getenv("LANGSMITH_API_KEY")
os.environ["GROQ_API_KEY"] = os.getenv("GROQ_API_KEY")
os.environ["LANGSMITH_TRACING"] = "true"

# =============================================================================
# Dataset
# =============================================================================

from langsmith import Client

client = Client()

# Define dataset: these are your test cases
dataset_name = "Parking  Evaluation"
dataset = client.create_dataset(dataset_name)
client.create_examples(
    dataset_id=dataset.id,
    examples=[
        {
            "inputs": {"question": "What are the priority tiers for parking reservations?"},
            "outputs": {
                "answer": "Tier 1: Essential Access (medical needs, disabilities, expectant mothers in third trimester). Tier 2: Carpoolers (3+ employees). Tier 3: Distance Commuters (residence >30 miles from office, no viable public transport). Tier 4: General Staff."
            }
        },
        {
            "inputs": {"question": "How many days per week can General Staff (Tier 4) reserve a parking space?"},
            "outputs": {"answer": "General Staff may reserve a parking space for a maximum of three (3) days per week."}
        },
        {
            "inputs": {"question": "What is the cancellation deadline for a parking reservation?"},
            "outputs": {
                "answer": "Employees must cancel their reservation no later than 8:00 AM on the day of the reservation."}
        },
        {
            "inputs": {"question": "What happens on the third no‑show offense within 60 days?"},
            "outputs": {"answer": "Suspension of parking reservation privileges for thirty (30) days."}
        },
        {
            "inputs": {
                "question": "Can I park an electric vehicle in a standard spot if the EV charging station is occupied?"},
            "outputs": {
                "answer": "The policy does not explicitly forbid an EV from parking in a standard spot. However, EV spaces may only be reserved by users actively driving an EV, and the space may only be occupied while the vehicle is actively charging."}
        },
        {
            "inputs": {
                "question": "What are the backup methods for entering the facility if license plate recognition fails?"},
            "outputs": {
                "answer": "Use the digital QR code from the EFFIA app (My Passes) and scan it on the optical reader, or press the Intercom/Help button for remote operator assistance."}
        },
        {
            "inputs": {"question": "How do I register my vehicle in the EFFIA system?"},
            "outputs": {
                "answer": "Log into your account, go to My Account > My Vehicles, click Add a Vehicle, enter the license plate number exactly as it appears (without spaces or dashes), select vehicle type, and click Save. Up to three vehicles can be registered."}
        },
        {
            "inputs": {"question": "When does the booking window open for the following work week?"},
            "outputs": {
                "answer": "Reservations open every Friday at 12:00 PM (Noon) for Monday through Sunday of the following week."}
        },
        {
            "inputs": {"question": "Is overnight parking allowed?"},
            "outputs": {
                "answer": "Overnight parking is strictly prohibited unless pre‑authorized by Facilities Management for business travel purposes."}
        },
        {
            "inputs": {
                "question": "What should I do if I drive a different car (e.g., a rental) on the day of my reservation?"},
            "outputs": {
                "answer": "Before arriving at the parking lot, go to My Reservations, select the active booking, click Change Vehicle, and enter the new license plate number."}
        },
        {
            "inputs": {"question": "How are overstay fees calculated?"},
            "outputs": {
                "answer": "If a vehicle remains past the reserved exit time, an overstay fee is charged at the standard hourly rate of the specific parking facility and automatically billed to the credit card on file upon exit."}
        },
        {
            "inputs": {"question": "Who is responsible for theft or damage to a vehicle parked in company facilities?"},
            "outputs": {
                "answer": "The company is not responsible for theft, vandalism, fire, or damage to any vehicle or personal property left inside a vehicle while on company premises."}
        },
        {
            "inputs": {"question": "Where can I dispute a no‑show strike?"},
            "outputs": {
                "answer": "Contact the Facilities Helpdesk at facilities@company.com or HR for medical exemptions at hr-benefits@company.com."}
        },
        {
            "inputs": {"question": "Can visitors park in employee spaces?"},
            "outputs": {
                "answer": "No. A designated percentage of the lot is reserved for visitors, and employees are strictly prohibited from parking in visitor spaces. Department heads must log visitor license plates into the Visitor Management Portal at least 24 hours in advance."}
        },
        {
            "inputs": {"question": "What types of vehicles are covered under the scope of this policy?"},
            "outputs": {
                "answer": "All full‑time employees, part‑time employees, contractors, and registered visitors who intend to park a motorized vehicle (car, motorcycle, or scooter) in company‑owned or leased parking facilities."}
        },
        {
            "inputs": {"question": "How do I book an EFFIA Park & Charge EV spot?"},
            "outputs": {
                "answer": "On the app or web portal, select your desired location, choose entry/exit date and time, then select the space type 'EFFIA Park & Charge for EVs', and choose an electric vehicle from your saved list."}
        },
        {
            "inputs": {"question": "Is there a penalty for not moving an EV after it is fully charged?"},
            "outputs": {
                "answer": "The policy encourages the driver to move to a standard spot if available, but it is not strictly required until the reservation ends. No explicit penalty is stated."}
        },
        {
            "inputs": {"question": "What is the speed limit inside company parking structures?"},
            "outputs": {"answer": "Strictly 10 mph (15 km/h)."}
        },
        {
            "inputs": {"question": "How can I access the EFFIA online reservation system?"},
            "outputs": {
                "answer": "Via the official effia.com portal or the EFFIA mobile application. Internal employees use Single Sign‑On (SSO) corporate credentials; external subscribers use their registered accounts."}
        },
        {
            "inputs": {"question": "What should I do if the barrier does not open and I don't have a QR code?"},
            "outputs": {
                "answer": "Do not pull a paper ticket. Press the Intercom/Help button on the terminal. A remote operator will verify your reservation and open the gate manually."}
        }
    ])

# =============================================================================
# Define the Agent target (RAG bot equivalent)
# =============================================================================

from services.agent_service import graph_builder, vector_store
from langsmith import traceable


@traceable()
def parking_agent_bot(question: str) -> dict:
    """Invoke the parking agent and return answer + retrieved documents."""
    result = graph_builder.run_graph(
        question=question,
        user_id=None,
        roleUser=None,
        mode_response=ModeResponse.reclamation_response,
        number_vectors=vector_store.count_vectors(),
    )

    answer = result.get("answer", "")
    documents = result.get("documents", [])

    return {"answer": answer, "documents": documents}


# =============================================================================
# Define Metrics (LLM As A Judge)
# =============================================================================

from typing_extensions import Annotated, TypedDict
from langchain_groq import ChatGroq

grader_model = ChatGroq(model="openai/gpt-oss-120b", temperature=0, max_retries=2)

# ── Correctness: Response vs reference answer ───────────────────────────────

class CorrectnessGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    correct: Annotated[bool, ..., "True if the answer is correct, False otherwise."]


correctness_instructions = """You are a teacher grading a quiz. 

You will be given a QUESTION, the GROUND TRUTH (correct) ANSWER, and the STUDENT ANSWER. 

Here is the grade criteria to follow:
(1) Grade the student answers based ONLY on their factual accuracy relative to the ground truth answer. 
(2) Ensure that the student answer does not contain any conflicting statements.
(3) It is OK if the student answer contains more information than the ground truth answer, as long as it is factually accurate relative to the ground truth answer.

Correctness:
A correctness value of True means that the student's answer meets all of the criteria.
A correctness value of False means that the student's answer does not meet all of the criteria.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset."""

correctness_grader = grader_model.with_structured_output(
    CorrectnessGrade, method="json_schema", strict=True
)


def correctness(inputs: dict, outputs: dict, reference_outputs: dict) -> bool:
    """An evaluator for RAG answer accuracy"""
    answers = f"""\
QUESTION: {inputs['question']}
GROUND TRUTH ANSWER: {reference_outputs['answer']}
STUDENT ANSWER: {outputs['answer']}"""

    grade = correctness_grader.invoke([
        {"role": "system", "content": correctness_instructions},
        {"role": "user", "content": answers},
    ])
    return grade["correct"]


# ── Relevance: Response vs input ────────────────────────────────────────────

class RelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[bool, ..., "Provide the score on whether the answer addresses the question"]


relevance_instructions = """You are a teacher grading a quiz. 

You will be given a QUESTION and a STUDENT ANSWER. 

Here is the grade criteria to follow:
(1) Ensure the STUDENT ANSWER is concise and relevant to the QUESTION
(2) Ensure the STUDENT ANSWER helps to answer the QUESTION

Relevance:
A relevance value of True means that the student's answer meets all of the criteria.
A relevance value of False means that the student's answer does not meet all of the criteria.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset."""

relevance_grader = grader_model.with_structured_output(
    RelevanceGrade, method="json_schema", strict=True
)


def relevance(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer helpfulness."""
    answer = f"QUESTION: {inputs['question']}\nSTUDENT ANSWER: {outputs['answer']}"
    grade = relevance_grader.invoke([
        {"role": "system", "content": relevance_instructions},
        {"role": "user", "content": answer},
    ])
    return grade["relevant"]


# ── Groundedness: Response vs retrieved docs ────────────────────────────────

class GroundedGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    grounded: Annotated[bool, ..., "Provide the score on if the answer hallucinates from the documents"]


grounded_instructions = """You are a teacher grading a quiz. 

You will be given FACTS and a STUDENT ANSWER. 

Here is the grade criteria to follow:
(1) Ensure the STUDENT ANSWER is grounded in the FACTS. 
(2) Ensure the STUDENT ANSWER does not contain "hallucinated" information outside the scope of the FACTS.

Grounded:
A grounded value of True means that the student's answer meets all of the criteria.
A grounded value of False means that the student's answer does not meet all of the criteria.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset."""

grounded_grader = grader_model.with_structured_output(
    GroundedGrade, method="json_schema", strict=True
)


def groundedness(inputs: dict, outputs: dict) -> bool:
    """A simple evaluator for RAG answer groundedness."""
    doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
    answer = f"FACTS: {doc_string}\nSTUDENT ANSWER: {outputs['answer']}"
    grade = grounded_grader.invoke([
        {"role": "system", "content": grounded_instructions},
        {"role": "user", "content": answer},
    ])
    return grade["grounded"]


# ── Retrieval Relevance: Retrieved docs vs input ────────────────────────────

class RetrievalRelevanceGrade(TypedDict):
    explanation: Annotated[str, ..., "Explain your reasoning for the score"]
    relevant: Annotated[bool, ..., "True if the retrieved documents are relevant to the question, False otherwise"]


retrieval_relevance_instructions = """You are a teacher grading a quiz. 

You will be given a QUESTION and a set of FACTS provided by the student. 

Here is the grade criteria to follow:
(1) You goal is to identify FACTS that are completely unrelated to the QUESTION
(2) If the facts contain ANY keywords or semantic meaning related to the question, consider them relevant
(3) It is OK if the facts have SOME information that is unrelated to the question as long as (2) is met

Relevance:
A relevance value of True means that the FACTS contain ANY keywords or semantic meaning related to the QUESTION and are therefore relevant.
A relevance value of False means that the FACTS are completely unrelated to the QUESTION.

Explain your reasoning in a step-by-step manner to ensure your reasoning and conclusion are correct. 

Avoid simply stating the correct answer at the outset."""

retrieval_relevance_grader = grader_model.with_structured_output(
    RetrievalRelevanceGrade, method="json_schema", strict=True
)


def retrieval_relevance(inputs: dict, outputs: dict) -> bool:
    """An evaluator for document relevance"""
    doc_string = "\n\n".join(doc.page_content for doc in outputs["documents"])
    answer = f"FACTS: {doc_string}\nQUESTION: {inputs['question']}"

    grade = retrieval_relevance_grader.invoke([
        {"role": "system", "content": retrieval_relevance_instructions},
        {"role": "user", "content": answer},
    ])
    return grade["relevant"]


# =============================================================================
# Run the evaluation
# =============================================================================

def target(inputs: dict) -> dict:
    return parking_agent_bot(inputs["question"])


experiment_results = client.evaluate(
    target,
    data=dataset_name,
    evaluators=[correctness, groundedness, relevance, retrieval_relevance],
    experiment_prefix="parking-agent-eval",
    metadata={"version": "v1", "model": "openai/gpt-oss-120b"},
)

# Explore results locally as a dataframe
experiment_results.to_pandas()
