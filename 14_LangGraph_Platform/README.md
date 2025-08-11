<p align="center" draggable="false"><img src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719" 
     width="200px"
     height="auto"/>
</p>

<h1 align="center" id="heading">Session 14: Build & Serve Agentic Graphs with LangGraph</h1>

| 🤓 Pre-work | 📰 Session Sheet | ⏺️ Recording     | 🖼️ Slides        | 👨‍💻 Repo         | 📝 Homework      | 📁 Feedback       |
|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|:-----------------|
| [Session 14: Pre-Work](https://www.notion.so/Session-14-Deploying-Agents-to-Production-21dcd547af3d80aba092fcb6c649c150?source=copy_link#247cd547af3d80709683ff380f4cba62)| [Session 14: Deploying Agents to Production](https://www.notion.so/Session-14-Deploying-Agents-to-Production-21dcd547af3d80aba092fcb6c649c150) | [Recording](https://us02web.zoom.us/rec/share/1YepNUK3kqQnYLY8InMfHv84JeiOMyjMRWOZQ9jfjY86dDPvHMhyoz5Zo04w_tn-.91KwoSPyP6K6u0DC) | [Session 14 Slides](https://www.canva.com/design/DAGvVPg7-mw/IRwoSgDXPEqU-PKeIw8zLg/edit?utm_content=DAGvVPg7-mw&utm_campaign=designshare&utm_medium=link2&utm_source=sharebutton) | You are here! | [Session 14 Assignment: Production Agents](https://forms.gle/nZ7ugE4W9VsC1zXE8) | [AIE7 Feedback 8/7](https://forms.gle/juo8SF5y5XiojFyC9)

# Build 🏗️

Run the repository and complete the following:

- 🤝 Breakout Room Part #1 — Building and serving your LangGraph Agent Graph
  - Task 1: Getting Dependencies & Environment
    - Configure `.env` (OpenAI, Tavily, optional LangSmith)
  - Task 2: Serve the Graph Locally
    - `uv run langgraph dev` (API on `http://localhost:2024`)
  - Task 3: Call the API
    - `uv run test_served_graph.py` (sync SDK example)
  - Task 4: Explore assistants (from `langgraph.json`)
    - `agent` → `simple_agent` (tool-using agent)
    - `agent_helpful` → `agent_with_helpfulness` (separate helpfulness node)

- 🤝 Breakout Room Part #2 — Using LangGraph Studio to visualize the graph
  - Task 1: Open Studio while the server is running
    - [LangGraph Studio](https://smith.langchain.com/studio?baseUrl=http://localhost:2024)
  - Task 2: Visualize & Stream
    - Start a run and observe node-by-node updates
  - Task 3: Compare Flows
    - Contrast `agent` vs `agent_helpful` (tool calls vs helpfulness decision)

<details>
<summary>🚧 Advanced Build 🚧 (OPTIONAL - <i>open this section for the requirements</i>)</summary>

- Create and deploy a locally hosted MCP server with FastMCP.
- Extend your tools in `tools.py` to allow your LangGraph to consume the MCP Server.
</details>

# Ship 🚢

- Running local server (`langgraph dev`)
- Short demo showing both assistants responding

# Share 🚀
- Walk through your graph in Studio
- Share 3 lessons learned and 3 lessons not learned


#### ❓ Question:

What is the purpose of the `chunk_overlap` parameter when using `RecursiveCharacterTextSplitter` to prepare documents for RAG, and what trade-offs arise as you increase or decrease its value?

##### ✅ Answer:

- **Purpose**: `chunk_overlap` reuses a portion of the previous chunk at the start of the next chunk so information that spans a boundary is preserved in at least one chunk, improving retrieval recall and answer quality.
- **Trade‑off when increasing overlap**:
  - **Pros**: Better recall for boundary‑spanning facts; smoother context continuity.
  - **Cons**: More duplicated content → higher embedding/storage cost, larger index, slower ingestion/querying, more duplicate retrievals, and more prompt tokens without adding much new information.
- **Trade‑off when decreasing overlap**:
  - **Pros**: Faster and cheaper ingestion/querying; smaller index.
  - **Cons**: Higher chance of cutting facts across boundaries, lowering recall and answer quality.
- **Practical guidance**:
  - Start around **10–20% of `chunk_size`** (e.g., ~50–200 tokens) and tune based on evals.
  - Use higher overlap for narrative/long sentences; lower for highly structured/self‑contained text.
  - With a token length function (as in this repo), both `chunk_size` and `chunk_overlap` are effectively in tokens.

```python
# app/rag.py
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=750, chunk_overlap=0, length_function=_tiktoken_len
)
```

- In this project, overlap is `0` (fast/cheap) but may miss cross‑boundary context; consider a small positive overlap if you observe recall issues.

- Summary:
  - `chunk_overlap` preserves cross‑chunk context.
  - More overlap → better recall but higher cost/duplication.
  - Less overlap → cheaper/faster but risk of missed context.


#### ❓ Question:

Your retriever is configured with `search_kwargs={"k": 5}`. How would adjusting `k` likely affect RAGAS metrics such as Context Precision and Context Recall in practice, and why?

##### ✅ Answer:

- **Increase k (>5)**
  - **Context Recall**: Likely increases (more chances to include the needed facts) until it plateaus.
  - **Context Precision**: Likely decreases (tail results add noise/irrelevant chunks).
  - **Context Relevancy**: Typically decreases on average (lower-ranked items are less relevant).
  - **Net**: Better coverage, but more noise; may help multi-fact questions, can hurt if ranking is weak or context gets bloated.

- **Decrease k (<5)**
  - **Context Recall**: Likely decreases (greater risk of missing required facts).
  - **Context Precision**: Likely increases (fewer, more relevant chunks).
  - **Context Relevancy**: Typically increases on average.
  - **Net**: Cleaner, focused context; can hurt if the answer depends on facts not in top few chunks.

- **Practical guidance**
  - Tune k with evals; many setups land in the 3–10 range.
  - Prefer smarter retrieval over just larger k: use MMR/diversification, score thresholds, or adaptive stopping by similarity drop-off.
  - Watch context-window limits: very large k can cause truncation, reducing effective recall despite higher retrieved count.

- **Why this happens**
  - Rankers aren’t perfect; as k grows you include lower-similarity items, increasing noise. Smaller k leverages the ranker’s best bets, improving precision but risking missing necessary evidence.

- Summary
  - More k → higher Context Recall, lower Context Precision.
  - Less k → higher Context Precision, lower Context Recall.
  - Optimize k with RAGAS-driven tuning and retrieval diversification/thresholds.


#### ❓ Question:

Compare the `agent` and `agent_helpful` assistants defined in `langgraph.json`. Where does the helpfulness evaluator fit in the graph, and under what condition should execution route back to the agent vs. terminate?

##### ✅ Answer:

- The `agent` assistant (simple agent):
  - After the model runs, if there are tool calls → go to `action`; otherwise → terminate.
```python
# app/graphs/simple_agent.py
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if getattr(last_message, "tool_calls", None):
        return "action"
    return END
```

- The `agent_helpful` assistant:
  - After the model runs, if there are tool calls → `action`; otherwise → run the `helpfulness` evaluator. This evaluator sits immediately after the `agent` node as a post-response gate.
  ```python
  # app/graphs/agent_with_helpfulness.py
  def route_to_action_or_helpfulness(state: AgentState):
      last_message = state["messages"][-1]
      if getattr(last_message, "tool_calls", None):
          return "action"
      return "helpfulness"
  ```
  - Routing and termination:
    - If the evaluator returns Y → terminate.
    - If it returns N → route back to `agent` to try again, unless a loop-limit sentinel is present.

  ```python
  # app/graphs/agent_with_helpfulness.py
  def helpfulness_decision(state: AgentState):
      if any(getattr(m, "content", "") == "HELPFULNESS:END" for m in state["messages"][-1:]):
          return END
      last = state["messages"][-1]
      text = getattr(last, "content", "")
      if "HELPFULNESS:Y" in text:
          return "end"
      return "continue"
  ```
  - The wiring:
  ```python
  # app/graphs/agent_with_helpfulness.py
  graph.add_conditional_edges(
      "agent",
      route_to_action_or_helpfulness,
      {"action": "action", "helpfulness": "helpfulness"},
  )
  graph.add_conditional_edges(
      "helpfulness",
      helpfulness_decision,
      {"continue": "agent", "end": END, END: END},
  )
  ```

- In short: In `agent_helpful`, the helpfulness evaluator runs after the agent when no tools are called. Route back to `agent` on an unhelpful decision (N) and no loop-limit; terminate on a helpful decision (Y) or when the loop-limit sentinel is triggered.

- The evaluator also short-circuits with `HELPFULNESS:END` when message count exceeds the limit:
```python
# app/graphs/agent_with_helpfulness.py
if len(state["messages"]) > 10:
    return {"messages": [AIMessage(content="HELPFULNESS:END")]}
```

- Summary
  - `agent`: tool calls → `action`, else END.
  - `agent_helpful`: tool calls → `action`, else `helpfulness`; Y → END; N → back to `agent`; loop-limit → END.