from langgraph.graph import END, StateGraph
from typing_extensions import TypedDict
from tavily import TavilyClient
from dotenv import load_dotenv
import os
from openai import OpenAI
from prompts import Prompts
from llm import r1
import json
from structured_output import json_schema
load_dotenv()

class GraphState(TypedDict):
    question: str
    retrieved_context: str
    router_decision: str
    answer_to_question: str
    missing_information: str
    reasoning: str
    useful_information: str

class QAAgent:
    def __init__(self):
        self.client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=os.getenv("NVIDIA_API_KEY")
        )
        self.tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))
        self.workflow = self.create_workflow()

    def retrieve(self, state: GraphState):
        question = state["question"]
        result = self.tavily_client.search(question, max_results=3)    
        retrieved_context = "\n".join([r["content"] for r in result["results"]])
        return {"retrieved_context": retrieved_context}

    def validate_retrieval(self, state: GraphState):
        question = state["question"]
        retrieved_context = state["retrieved_context"]

        validation_chain = Prompts.VALIDATE_RETRIEVAL | r1
        llm_output = validation_chain.invoke({"retrieved_context": retrieved_context, "question": question}).content
        print("llm_output:", llm_output)
        reasoning = llm_output.split("<think>")[1].split("</think>")[0].strip()
        response = llm_output.split("</think>")[1].strip()
        
        strcutured_response = json.loads(response)
        #print("response:", strcutured_response)
        
        router_decision = strcutured_response["status"]
        missing_information = strcutured_response["missing_information"]
        useful_information = strcutured_response["useful_information"]
        print("router_decision:", router_decision)
        print("*****************")
        print("missing_information:", missing_information)
        print("*****************")
        print("useful_information:", useful_information)
        print("*****************")
        #valid_decision = "VALID" if "VALID" in router_decision else "INVALID"
        #print(f"\nRetrieval Validation: {valid_decision}")
        return {"router_decision": router_decision, "retrieved_context": retrieved_context, "useful_information": useful_information, "missing_information": missing_information, "reasoning": reasoning}

    def answer(self, state: GraphState):
        question = state["question"]
        context = state["retrieved_context"]

        answer_chain = Prompts.ANSWER_QUESTION | r1
        llm_output = answer_chain.invoke({"retrieved_context": context, "question": question}).content
        reasoning = llm_output.split("<think>")[1].split("</think>")[0].strip()
        answer = llm_output.split("</think>")[1].strip()
        #print("answer:", answer)
        #print("reasoning:", reasoning)
        return {"answer_to_question": answer}

    def find_missing_information(self, state: GraphState):
        """
        This function is used to find the missing information in the retrieved context.
        it will return a query that will be used to search the web for the missing information.
        """
        missing_information = state["missing_information"]
        tavily_query = self.tavily_client.search(missing_information, max_results=3)
        previously_retrieved_useful_information = state["useful_information"]
        newly_retrieved_context = "\n".join([r["content"] for r in tavily_query["results"]])
        combined_context = f"{previously_retrieved_useful_information}\n{newly_retrieved_context}"
        print("*****************")
        print("combined_context:", combined_context)
        print("*****************")
        return {"retrieved_context": combined_context}

    @staticmethod
    def decide_route(state: GraphState):
        return state["router_decision"]

    def create_workflow(self):
        workflow = StateGraph(GraphState)
        
        workflow.add_node("retrieve", self.retrieve)
        workflow.add_node("validate_retrieval", self.validate_retrieval)
        workflow.add_node("answer", self.answer)
        workflow.add_node("find_missing_information", self.find_missing_information)
        
        workflow.set_entry_point("retrieve")
        workflow.add_edge("retrieve", "validate_retrieval")
        
        workflow.add_conditional_edges(
            "validate_retrieval",
            self.decide_route,
            {
                "VALID": "answer",
                "INVALID": "find_missing_information"
            }
        )
        workflow.add_edge("find_missing_information", "validate_retrieval")
    
        workflow.add_edge("answer", END)
        return workflow.compile()

    def run(self, question: str):
        result = self.workflow.invoke({"question": question})
        print("\nFinal Answer:", result["answer_to_question"])
        return result["answer_to_question"]

if __name__ == "__main__":
    agent = QAAgent()
    agent.run("Who is George Washington?")