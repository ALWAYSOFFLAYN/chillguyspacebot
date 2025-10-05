import yaml
from jinja2 import Template
from app.config import STORY_YAML, TEMPLATE_TURN, RAG_TOPK
from app.rag.retriever import retrieve

class StoryState:
    def __init__(self, name: str, node_id: str = "flare_alert"):
        self.name = name
        self.node_id = node_id
        self.step = 0

def _load_story():
    with open(STORY_YAML, "r", encoding="utf-8") as f:
        story = yaml.safe_load(f)
    with open(TEMPLATE_TURN, "r", encoding="utf-8") as f:
        turn_tpl = Template(f.read())
    nodemap = {n["id"]: n for n in story["nodes"]}
    buttons = story.get("buttons", {"button_1": "Button 1", "button_2": "Button 2"})
    return story, nodemap, turn_tpl, buttons

STORY, NODEMAP, TURN_TPL, BUTTONS = _load_story()

def render_node(state: StoryState):
    node = NODEMAP[state.node_id]
    q = node.get("query", "")
    snips = retrieve(q, k=RAG_TOPK) if q else []
    text = node["text"].replace("{name}", state.name).replace("{rag_snippets}", "")
    body = TURN_TPL.render(base_text=text, rag_snippets=snips)

    # Visible labels per-node override (optional)
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

