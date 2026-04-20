"""
FastAPI-based orchestration for educational content generation pipeline.

Endpoints:
- GET / - Basic service info
- GET /health - Health check
- POST /generate - Generate content
- GET /outputs/{session_id}/{filename} - Download files
- GET /sessions - List sessions
"""
from datetime import datetime
import logging
from pathlib import Path
import traceback
from typing import Optional, List, Dict, Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from content_generator import ContentGenerator
from cross_validation import CrossValidator
from input_schema import ContentInput, Constraints
from llm_client import LLMClient
from media_renderers import slide_renderer, diagram_renderer, audio_renderer
from prompt_templates import build_prompt

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="EduForge - Educational Content Generator",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OUTPUT_DIR = Path("generated_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


class GenerateRequest(BaseModel):
    topic: str
    audience: str = "beginner"
    max_duration_sec: int = 180
    example_count: Optional[int] = None
    render_formats: List[str] = ["slides", "diagrams"]
    slide_format: str = "html"
    optimize_for_format: bool = True
    include_few_shot: bool = False
    llm_provider: str = "together"
    together_api_key: Optional[str] = None


class GenerateResponse(BaseModel):
    success: bool
    message: str
    content_output: Optional[Dict[str, Any]] = None
    generated_files: Optional[Dict[str, Any]] = None
    validation_warnings: Optional[List[str]] = None
    generation_time_sec: Optional[float] = None


@app.get("/")
async def root():
    return {"status": "running", "service": "EduForge"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    start_time = datetime.now()

    try:
        content_input = ContentInput(
            topic=request.topic,
            audience=request.audience,
            constraints=Constraints(
                max_duration_sec=request.max_duration_sec,
                examples=request.example_count,
                render_formats=request.render_formats,
                slide_format=request.slide_format,
                optimize_for_format=request.optimize_for_format
            )
        )

        prompt = build_prompt(content_input, include_few_shot=request.include_few_shot)

        if request.llm_provider == "together" and not request.together_api_key:
            raise HTTPException(status_code=400, detail="Missing Together API key")

        client = LLMClient.create(
            provider=request.llm_provider,
            api_key=request.together_api_key,
            fallback_to_local=False
        )

        generator = ContentGenerator(client, content_input, prompt)
        content_output = generator.generate_with_repair()

        is_valid, errors = CrossValidator.validate(content_input, content_output)

        generated_files = {}

        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(exist_ok=True)

        if "slides" in request.render_formats:
            slide_file = slide_renderer.SlideRenderer(str(session_dir)).render(content_output)
            generated_files["slides"] = f"/outputs/{session_id}/{slide_file.name}"

        if "diagrams" in request.render_formats:
            files = diagram_renderer.DiagramRenderer(str(session_dir)).render(content_output)
            generated_files["diagrams"] = [f"/outputs/{session_id}/{f.name}" for f in files]

        if "audio" in request.render_formats:
            files = audio_renderer.AudioRenderer(str(session_dir)).render(content_output)
            generated_files["audio"] = [f"/outputs/{session_id}/{f.name}" for f in files]

        return GenerateResponse(
            success=True,
            message="Generated successfully",
            content_output=content_output.model_dump(),
            generated_files=generated_files,
            validation_warnings=errors if not is_valid else None,
            generation_time_sec=(datetime.now() - start_time).total_seconds()
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/outputs/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    path = OUTPUT_DIR / session_id / filename
    if not path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse(path)


@app.get("/sessions")
async def sessions():
    data = []
    for d in OUTPUT_DIR.iterdir():
        if d.is_dir():
            files = list(d.glob("*"))
            data.append({"session_id": d.name, "file_count": len(files)})
    return {"sessions": data}
