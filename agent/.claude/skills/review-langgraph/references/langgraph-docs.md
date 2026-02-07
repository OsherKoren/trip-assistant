# LangGraph Documentation References

Quick links to official LangGraph documentation. Use WebFetch to retrieve these when needed.

## Core Concepts

### StateGraph
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#stategraph
- **When**: Understanding graph initialization and compilation
- **Key Points**: StateGraph replaces MessageGraph in LangGraph 1.x

### State Management
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#state
- **When**: Defining state schema, reducers, updates
- **Key Points**: Use TypedDict, nodes return partial updates, immutability

### Nodes
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#nodes
- **When**: Creating node functions, understanding signatures
- **Key Points**: Nodes are functions that take state and return partial state

### Edges
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#edges
- **When**: Connecting nodes, defining flow
- **Key Points**: Normal edges vs conditional edges

### Conditional Edges
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#conditional-edges
- **When**: Implementing routing logic
- **Key Points**: Routing function returns next node name

## Advanced Patterns

### Structured Output
- **Docs**: https://python.langchain.com/docs/how_to/structured_output/
- **When**: Replacing string parsing with type-safe outputs
- **Key Points**: Use with_structured_output() + Pydantic models

### Message Reducers
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#reducers
- **When**: Managing message lists in state
- **Key Points**: Use add_messages from langgraph.graph.message

### Streaming
- **Docs**: https://langchain-ai.github.io/langgraph/how-tos/stream-updates/
- **When**: Implementing real-time responses
- **Key Points**: app.stream() for token-by-token streaming

### Checkpoints
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#checkpointer
- **When**: Adding persistence and replay
- **Key Points**: Memory checkpointers for testing, DB for production

## Migration

### From MessageGraph
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/low_level/#from-messagegraph
- **When**: Upgrading legacy code
- **Key Points**: MessageGraph deprecated, use StateGraph

### From LangChain Agents
- **Docs**: https://langchain-ai.github.io/langgraph/concepts/agentic_concepts/
- **When**: Replacing old LangChain agent patterns
- **Key Points**: LangGraph provides more control and debuggability

## Examples

### Multi-Agent Systems
- **Docs**: https://langchain-ai.github.io/langgraph/tutorials/multi_agent/multi_agent_collaboration/
- **When**: Building coordinator + specialist patterns
- **Key Points**: Similar to trip assistant classifier → router → specialists

### RAG
- **Docs**: https://langchain-ai.github.io/langgraph/tutorials/rag/langgraph_agentic_rag/
- **When**: Integrating document retrieval
- **Key Points**: Conditional routing to retrieval vs direct answer

### Human-in-the-Loop
- **Docs**: https://langchain-ai.github.io/langgraph/how-tos/human_in_the_loop/
- **When**: Adding approval workflows
- **Key Points**: Interrupt nodes for user input

## API Reference

### StateGraph API
- **Docs**: https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.StateGraph
- **When**: Looking up specific methods
- **Key Points**: add_node, add_edge, add_conditional_edges, compile

### MessageGraph (Legacy)
- **Docs**: https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.MessageGraph
- **When**: Understanding what to avoid
- **Key Points**: Deprecated, use StateGraph instead

## How to Fetch in Review

When you need to reference a pattern during review:

```python
# Example: User has outdated MessageGraph code
# Fetch migration guide to show proper StateGraph pattern

WebFetch(
    url="https://langchain-ai.github.io/langgraph/concepts/low_level/#stategraph",
    prompt="Extract the proper way to initialize and compile a StateGraph, including imports and basic structure"
)
```

## Common Patterns to Reference

| Issue Found | Fetch This Doc | Search For |
|-------------|----------------|------------|
| Using MessageGraph | Low Level Concepts | StateGraph basics |
| State mutations | State Management | Immutability, reducers |
| Wrong node signature | Nodes | Function signature |
| Routing issues | Conditional Edges | Routing functions |
| String parsing LLM output | Structured Output | with_structured_output |
| Message list handling | Reducers | add_messages |

---

## Documentation Structure

LangGraph docs organized as:
- **Concepts**: High-level understanding
- **How-to Guides**: Specific tasks
- **Tutorials**: End-to-end examples
- **Reference**: API documentation

Use **Concepts** for understanding patterns, **How-to** for specific fixes.
