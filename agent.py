from google.adk import Agent, Workflow, Context, Event
from pydantic import BaseModel, Field

class DesignInput(BaseModel):
    product_name: str
    material: str
    target_load_kg: int

class SimulationCode(BaseModel):
    c_code: str
    logic_explanation: str

# Agents
math_engine_agent = Agent(name="math_engine_agent", model="gemini-2.5-flash", instruction="Analyze structural integrity. Return as string.")
coder_agent = Agent(name="coder_agent", model="gemini-2.5-flash", instruction="Write C code for stress test.", output_schema=SimulationCode)
publisher_agent = Agent(name="publisher_agent", model="gemini-2.5-flash", instruction="Format report as Markdown.")

# Logic
def ingest_design(ctx: Context, node_input: DesignInput):
    ctx.state["raw_design"] = node_input.product_name
    return "Design Ingested"

def route_to_coder(ctx: Context, node_input: str):
    ctx.state["math_analysis"] = node_input
    return "Triggering coder"

def compile_report(ctx: Context, node_input: SimulationCode):
    ctx.state["c_code"] = node_input.c_code
    report = f"Report: {ctx.state['raw_design']}\nMath: {ctx.state['math_analysis']}\nCode: {ctx.state['c_code']}"
    ctx.state["final_markdown"] = report
    return report

def save_report_to_disk(ctx: Context, node_input: str):
    ctx.artifacts.add("Chair_Technical_Report.md", node_input)
    return node_input

root_agent = Workflow(
    name="auto_engineer_workflow",
    input_schema=DesignInput,
    edges=[
        ("START", ingest_design),
        (ingest_design, math_engine_agent),
        (math_engine_agent, route_to_coder),
        (route_to_coder, coder_agent),
        (coder_agent, compile_report),
        (compile_report, publisher_agent),
        (publisher_agent, save_report_to_disk),
    ]
)