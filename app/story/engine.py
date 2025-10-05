import yaml
from app.config import STORY_YAML, RAG_TOPK
from app.rag.retriever import retrieve
from app.nlp.model import GenModel

MODEL = GenModel()

class StoryState:
    def __init__(self, name: str, node_id: str = "flare_alert"):
        self.name = name
        self.node_id = node_id
        self.step = 0

def _load_story():
    with open(STORY_YAML, "r", encoding="utf-8") as f:
        story = yaml.safe_load(f)
    nodemap = {n["id"]: n for n in story["nodes"]}
    buttons = story.get("buttons", {"button_1": "Button 1", "button_2": "Button 2"})
    return story, nodemap, buttons

STORY, NODEMAP, BUTTONS = _load_story()

def render_node(state: StoryState):
    node = NODEMAP[state.node_id]
    q = node.get("query", "")
    snips = retrieve(q, k=RAG_TOPK) if q else []

    # Clean base text and remove any stray placeholder tokens if present
    base_text = (node["text"] or "").replace("{name}", state.name).replace("{rag_snippets}", "").strip()

    # Let the model compose the final turn (templated or HF)
    body = MODEL.generate_turn(base_text=base_text, rag_snippets=snips, name=state.name)

    # Button labels with optional per-node overrides
    choices = node.get("choices", {})
    lbl1 = choices.get("button_1", {}).get("label_override", BUTTONS.get("button_1", "Button 1"))
    lbl2 = choices.get("button_2", {}).get("label_override", BUTTONS.get("button_2", "Button 2"))

    return body, {"button_1": lbl1, "button_2": lbl2}, node.get("ending")

def advance(state: StoryState, button_key: str):
    node = NODEMAP[state.node_id]
    nxt = node["choices"][button_key]["next"]
    state.node_id = nxt
    state.step += 1
    return state
