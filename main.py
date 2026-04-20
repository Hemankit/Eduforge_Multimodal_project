"""
FastAPI-based orchestration for educational content generation pipeline.

Endpoints:
- POST /generate - Generate content from topic/audience/constraints
- GET /outputs/{filename} - Download generated files
- GET /health - Health check
"""
from datetime import datetime
import logging
import os
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
    description="AI-powered multimodal educational content generation. Supports local (Mistral 7B) and API (Llama 3.3 70B) inference.",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

llm_client: Optional[LLMClient] = None
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

        create_kwargs = {
            "provider": request.llm_provider,
            "fallback_to_local": False
        }
        if request.llm_provider == "together":
            create_kwargs["api_key"] = request.together_api_key

        client = LLMClient.create(**create_kwargs)
        generator = ContentGenerator(llm_client=client, valid_input=content_input, prompt=prompt)
        content_output = generator.generate_with_repair()

        is_valid, errors = CrossValidator.validate(content_input, content_output)

        generated_files: Dict[str, Any] = {}

        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(exist_ok=True)

        if "slides" in request.render_formats:
            renderer = slide_renderer.SlideRenderer(output_dir=str(session_dir))
            slide_file = renderer.render(content_output, format=request.slide_format)
            generated_files["slides"] = f"/outputs/{session_id}/{slide_file.name}"

        if "diagrams" in request.render_formats:
            renderer = diagram_renderer.DiagramRenderer(output_dir=str(session_dir))
            diagram_files = renderer.render(content_output)
            generated_files["diagrams"] = [f"/outputs/{session_id}/{f.name}" for f in diagram_files]

        if "audio" in request.render_formats:
            renderer = audio_renderer.AudioRenderer(output_dir=str(session_dir))
            audio_files = renderer.render(content_output)
            generated_files["audio"] = [f"/outputs/{session_id}/{f.name}" for f in audio_files]

        generation_time = (datetime.now() - start_time).total_seconds()

        return GenerateResponse(
            success=True,
            message=f"Content generated in {generation_time:.2f}s",
            content_output=content_output.model_dump(),
            generated_files=generated_files,
            validation_warnings=errors if not is_valid else None,
            generation_time_sec=generation_time
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=str(e))
