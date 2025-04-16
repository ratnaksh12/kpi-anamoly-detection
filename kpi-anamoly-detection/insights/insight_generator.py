import os
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(model="llama3-8b-8192", api_key=os.getenv("GROQ_API_KEY"))

prompt = PromptTemplate.from_template(
    """
    A KPI named {kpi_name} has changed by {change}% compared to the previous period.
    Previous value: {previous}
    Current value: {current}

    Analyze this change. Why might it have happened? Suggest 2-3 next steps a business could take.
    """
)

def generate_insight(kpi_name, change, previous, current):
    chain = prompt | llm
    return chain.invoke({
        "kpi_name": kpi_name,
        "change": round(change, 2),
        "previous": previous,
        "current": current
    })
