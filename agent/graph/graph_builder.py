from langgraph.checkpoint.mysql.pymysql import PyMySQLSaver
from langgraph.constants import END
from langgraph.graph import StateGraph

from agent.node.node import AgentNode
from agent.state.agent_state import AgentState
import os

from schemas.user_schemas import Role


class GraphBuilder:



    def __init__(self,llm,vector_store):
        self.node=AgentNode(llm,vector_store)
        self.graph=None

    def build_graph(self):

        builder=StateGraph(AgentState)


        builder.add_node("react_agent",self.node.generate_answer)


        builder.set_entry_point("react_agent")

        builder.add_edge("react_agent",END)
        self.graph=builder.compile()
        return self.graph

    def run_graph(self, question: str,mode_response,user_id: int=None,roleUser: Role=None ,reclamation_id :int=None,session_id: str=None,number_vectors:int=None) -> dict:
        if self.graph is None:
            self.build_graph()


        initial_state = AgentState(question=question,mode_response=mode_response,user_id=user_id,roleUser=roleUser,reclamation_id=reclamation_id,session_id=session_id,number_vectors=number_vectors)
        return self.graph.invoke(initial_state)
