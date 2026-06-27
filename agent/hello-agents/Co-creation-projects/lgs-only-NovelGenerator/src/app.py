import sys
import os
import json
import uvicorn
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# Add parent directory to sys.path to import agents
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
# Add agents directory to sys.path so internal imports in agents work
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../agents")))

from agents.outline_agent import OutlineAgent
from agents.chapter_generate_agent import ChapterGenerateAgent
from hello_agents import HelloAgentsLLM

app = FastAPI()

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Data Models
class OutlineRequest(BaseModel):
    novel_id: str
    title: str
    user_input: str
    tags: Optional[List[str]] = []
    target_length: Optional[int] = 3000
    style_tags: Dict[str, str] = {} # e.g. {"style": "dark", "tone": "serious"}

class OutlineUpdateRequest(BaseModel):
    novel_id: str
    title: str
    note_id: str
    content: str
    tags: Optional[List[str]] = None

class ChapterGenerateRequest(BaseModel):
    novel_id: str
    title: str
    user_input: str
    num_chapters: int = 1
    chapter_length: int = 3000

class ChapterUpdateRequest(BaseModel):
    novel_id: str
    title: str
    note_id: str
    content: Optional[str] = None
    chapter_title: Optional[str] = None
    summary: Optional[str] = None
    next_chapter_prediction: Optional[str] = None

# Manager
class ProjectManager:
    def __init__(self, workspace="./outputs"):
        self.workspace = workspace
        if not os.path.exists(workspace):
            os.makedirs(workspace)

    def get_project_dir(self, title, novel_id):
        return os.path.join(self.workspace, f"{title}-{novel_id}")

    def get_mapping_file(self, title, novel_id):
        return os.path.join(self.get_project_dir(title, novel_id), "project_data.json")

    def load_mapping(self, title, novel_id):
        path = self.get_mapping_file(title, novel_id)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        return {"novel_id": novel_id, "title": title, "outline_id": None, "chapters": []}

    def save_mapping(self, title, novel_id, data):
        path = self.get_mapping_file(title, novel_id)
        project_dir = self.get_project_dir(title, novel_id)
        if not os.path.exists(project_dir):
            os.makedirs(project_dir)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def update_outline_mapping(self, title, novel_id, outline_id):
        data = self.load_mapping(title, novel_id)
        data["outline_id"] = outline_id
        self.save_mapping(title, novel_id, data)

    def add_chapter_mapping(self, title, novel_id, chapter_data):
        data = self.load_mapping(title, novel_id)
        data["chapters"].append(chapter_data)
        self.save_mapping(title, novel_id, data)

    def update_chapter_mapping(self, title, novel_id, note_id, update_data):
        data = self.load_mapping(title, novel_id)
        for chapter in data["chapters"]:
            if chapter["id"] == note_id:
                chapter.update(update_data)
                break
        self.save_mapping(title, novel_id, data)

    def remove_chapter_mapping(self, title, novel_id, note_id):
        data = self.load_mapping(title, novel_id)
        data["chapters"] = [c for c in data["chapters"] if c["id"] != note_id]
        self.save_mapping(title, novel_id, data)

project_manager = ProjectManager()

# Agents
llm_instance = HelloAgentsLLM(model=os.getenv("LLM_MODEL_ID"))
outline_agent = OutlineAgent(name="OutlineAgent", llm=llm_instance, workspace="./outputs")
chapter_agent = ChapterGenerateAgent(
    name="ChapterAgent", 
    llm=llm_instance,
    workspace="./outputs", 
    chapter_length=3000 # Default length, can be overridden in run
)

# API Endpoints

@app.get("/projects/{title}/{novel_id}")
def get_project_data(title: str, novel_id: str):
    return project_manager.load_mapping(title, novel_id)

# --- Outline ---

@app.post("/outline/generate")
def generate_outline(req: OutlineRequest):
    # Construct kwargs for run
    run_kwargs = {
        "novel_id": req.novel_id,
        "title": req.title,
        "target_length": req.target_length
    }
    run_kwargs.update(req.style_tags)
    
    response, note_id = outline_agent.run(req.user_input, **run_kwargs)
    
    project_manager.update_outline_mapping(req.title, req.novel_id, note_id)
    
    return {"note_id": note_id, "content": response}

@app.get("/outline/{title}/{novel_id}/{note_id}")
def get_outline(title: str, novel_id: str, note_id: str):
    content = outline_agent.get_outline(novel_id, note_id, title=title)
    # Remove frontmatter if present (simple check)
    # NoteTool returns raw content usually.
    # Frontmatter format: --- ... ---
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    return {"content": content}

@app.put("/outline/update")
def update_outline(req: OutlineUpdateRequest):
    outline_agent.update_outline(req.novel_id, req.note_id, title=req.title, content=req.content, tags=req.tags)
    return {"status": "success"}

@app.delete("/outline/delete")
def delete_outline(novel_id: str, title: str, note_id: str):
    outline_agent.del_outline(novel_id, note_id, title=title)
    
    data = project_manager.load_mapping(title, novel_id)
    if data["outline_id"] == note_id:
        data["outline_id"] = None
        project_manager.save_mapping(title, novel_id, data)
    return {"status": "success"}

# --- Chapters ---

@app.post("/chapter/generate")
def generate_chapters(req: ChapterGenerateRequest):
    generated_chapters = []
    current_input = req.user_input
    
    for i in range(req.num_chapters):
        try:
            chapter_data, note_id = chapter_agent.run(
                user_input=current_input, 
                novel_id=req.novel_id, 
                novel_title=req.title,
                chapter_length=req.chapter_length
            )
            
            # Clear input for subsequent chapters to rely on context/prediction
            if i == 0:
                current_input = "" 
            
            chapter_info = {
                "id": note_id,
                "title": chapter_data.get("title", "Unknown"),
                "summary": chapter_data.get("summary", "")
            }
            generated_chapters.append(chapter_info)
            project_manager.add_chapter_mapping(req.title, req.novel_id, chapter_info)
        except Exception as e:
            print(f"Error generating chapter {i+1}: {e}")
            # Stop generating if one fails? Or continue?
            # Probably stop and return what we have.
            break
        
    return {"generated_chapters": generated_chapters}

@app.get("/chapter/{title}/{novel_id}/{note_id}")
def get_chapter(title: str, novel_id: str, note_id: str):
    path = os.path.join("./outputs", f"{title}-{novel_id}", "chapters", f"{note_id}.md")
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        
        # Remove frontmatter
        if content.startswith("---"):
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[2].strip()
        
        return {"content": content}
    raise HTTPException(status_code=404, detail="Chapter not found")

@app.put("/chapter/update")
def update_chapter(req: ChapterUpdateRequest):
    update_kwargs = {}
    if req.content is not None:
        update_kwargs["content"] = req.content
    if req.chapter_title is not None:
        update_kwargs["title"] = req.chapter_title
    if req.summary is not None:
        update_kwargs["summary"] = req.summary
    if req.next_chapter_prediction is not None:
        update_kwargs["next_chapter_prediction"] = req.next_chapter_prediction
        
    chapter_agent.update_chapter(req.novel_id, req.note_id, novel_title=req.title, **update_kwargs)
    
    # Update mapping if title/summary changed
    mapping_update = {}
    if req.chapter_title:
        mapping_update["title"] = req.chapter_title
    if req.summary:
        mapping_update["summary"] = req.summary
    
    if mapping_update:
        project_manager.update_chapter_mapping(req.title, req.novel_id, req.note_id, mapping_update)

    return {"status": "success"}

@app.delete("/chapter/delete")
def delete_chapter(novel_id: str, title: str, note_id: str):
    chapter_agent.del_chapter(novel_id, note_id, novel_title=title)
    
    project_manager.remove_chapter_mapping(title, novel_id, note_id)
    return {"status": "success"}

if __name__ == "__main__":
    uvicorn.run(app, host=os.getenv("HOST"), port=int(os.getenv("PORT")))
