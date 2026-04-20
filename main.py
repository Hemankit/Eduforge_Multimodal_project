"""
FastAPI-based orchestration for educational content generation pipeline.

Endpoints:
- POST /generate - Generate content from topic/audience/constraints
- GET /outputs/{filename} - Download generated files
- GET /health - Health check
"""
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import traceback
import os
from datetime import datetime
from dotenv import load_dotenv

from input_schema import ContentInput, Constraints
from output_schema import ContentOutput
from llm_client import LLMClient
from content_generator import ContentGenerator
from prompt_templates import build_prompt
from cross_validation import CrossValidator
from media_renderers import slide_renderer, diagram_renderer, audio_renderer

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="EduForge - Educational Content Generator",
    description="AI-powered multimodal educational content generation. Supports local (Mistral 7B) and API (Llama 3.3 70B) inference.",
    version="2.0.0"
)

# CORS middleware for web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global state for LLM client (lazy loading)
llm_client: Optional[LLMClient] = None
OUTPUT_DIR = Path("generated_outputs")
OUTPUT_DIR.mkdir(exist_ok=True)


# API Models
class GenerateRequest(BaseModel):
    """Request model for content generation."""
    topic: str
    audience: str = "beginner"
    max_duration_sec: int = 180
    example_count: Optional[int] = None
    render_formats: List[str] = ["slides", "diagrams"]
    slide_format: str = "html"
    optimize_for_format: bool = True
    include_few_shot: bool = False
    llm_provider: str = "together"  # "local" or "together"
    together_api_key: Optional[str] = None  # Only required if llm_provider="together". NOT needed for local models.
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "Binary Search Algorithm",
                "audience": "intermediate",
                "max_duration_sec": 240,
                "example_count": 2,
                "render_formats": ["slides", "diagrams", "audio"],
                "optimize_for_format": True,
                "include_few_shot": False,
                "llm_provider": "together",
                "together_api_key": "your_together_api_key_here"
            }
        }


class GenerateResponse(BaseModel):
    """Response model for content generation."""
    success: bool
    message: str
    content_output: Optional[Dict[str, Any]] = None
    generated_files: Optional[Dict[str, str]] = None
    validation_warnings: Optional[List[str]] = None
    generation_time_sec: Optional[float] = None


def get_llm_client() -> LLMClient:
    """
    Lazy load LLM client with simple provider selection.
    
    Respects environment variables:
    - LLM_PROVIDER: "local" or "together" (default: "local")
    - TOGETHER_API_KEY: Required if using Together AI
    """
    global llm_client
    if llm_client is None:
        provider = os.getenv("LLM_PROVIDER", "local")
        
        logger.info(f"Initializing LLM client with provider: {provider}")
        
        try:
            llm_client = LLMClient.create(
                provider=provider,
                fallback_to_local=True  # Falls back to local if API fails
            )
            logger.info(f"✅ LLM client initialized: {llm_client.provider.get_name()}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM client: {e}")
            # Last resort: try local
            logger.info("Attempting fallback to local provider...")
            llm_client = LLMClient.create(provider="local")
    
    return llm_client


@app.get("/")
async def root():
    """Welcome page with API information."""
    return {
        "name": "EduForge - Educational Content Generator",
        "version": "2.0.0",
        "status": "running",
        "endpoints": {
            "health": "/health - Check system status",
            "generate": "/generate - Generate educational content (POST)",
            "docs": "/docs - Interactive API documentation",
            "openapi": "/openapi.json - OpenAPI schema"
        },
        "usage": {
            "example": {
                "topic": "Binary Search Algorithm",
                "llm_provider": "together",
                "together_api_key": "your_api_key_here"
            },
            "get_api_key": "https://api.together.xyz/"
        },
        "features": [
            "Multi-modal content generation (slides, diagrams, audio)",
            "Two LLM modes: Local (Mistral 7B) or API (Llama 3.3 70B)",
            "User-provided API keys (no billing to Space owner)",
            "Schema validation and cross-validation"
        ]
    }


@app.get("/health")
async def health_check():
    """Health check endpoint with provider information."""
    health_info = {
        "status": "healthy",
        "model_loaded": llm_client is not None,
        "output_dir": str(OUTPUT_DIR.absolute())
    }
    
    # Add provider info if client is loaded
    if llm_client is not None:
        health_info["provider"] = llm_client.provider.get_name()
        health_info["model"] = llm_client.provider.model
        health_info["stats"] = llm_client.get_stats()
    
    return health_info


@app.post("/generate", response_model=GenerateResponse)
async def generate_content(request: GenerateRequest):
    """
    Generate educational content with multimodal outputs.
    
    Users provide their own Together AI API key to avoid billing the deployment owner.
    Supports both local (Mistral 7B) and API (Llama 3.3 70B) inference.
    
    This endpoint:
    1. Validates input and API key
    2. Builds prompt with schema injection
    3. Generates content using user's LLM provider
    4. Validates output
    5. Renders media files (slides, diagrams, audio)
    6. Returns content + file paths
    """
    start_time = datetime.now()
    
    try:
        # Step 1: Build ContentInput
        logger.info(f"Generating content for topic: {request.topic}")
        content_input = ContentInput(
            topic=request.topic,
            audience=request.audience,
            constraints=Constraints(
                max_duration_sec=request.max_duration_sec,
                example_count=request.example_count,
                render_formats=request.render_formats,
                slide_format=request.slide_format,
                optimize_for_format=request.optimize_for_format
            )
        )
        
        # Step 2: Build prompt
        logger.info("Building prompt with schema injection...")
        prompt = build_prompt(content_input, include_few_shot=request.include_few_shot)
        logger.info(f"Prompt built: {len(prompt)} characters")
        
        # Step 3: Validate provider choice and API key
        if request.llm_provider == "local":
            import torch
            if not torch.cuda.is_available():
                logger.warning(
                    "No GPU detected — local model will run on CPU. "
                    "This may be slow for large generation requests."
                )
        if request.llm_provider == "together" and not request.together_api_key:
            raise HTTPException(
                status_code=400,
                detail="together_api_key is required when llm_provider='together'. "
                       "Get your free key at https://api.together.xyz/"
            )
        
        # Step 4: Create LLM client with user's API key (only for API providers)
        logger.info(f"Creating LLM client with provider: {request.llm_provider}")
        create_kwargs = {
            "provider": request.llm_provider,
            "fallback_to_local": False  # No fallback - use what user specified
        }
        # Only pass API key for Together AI provider, not for local
        if request.llm_provider == "together":
            create_kwargs["api_key"] = request.together_api_key
        
        client = LLMClient.create(**create_kwargs)
        
        # Step 5: Generate content with LLM
        logger.info("Generating content with LLM...")
        generator = ContentGenerator(llm_client=client, valid_input=content_input, prompt=prompt)
        
        # Generate with repair loop
        content_output = generator.generate_with_repair()
        logger.info(f"✅ Content generated: {len(content_output.sections)} sections")
        
        # Step 6: Cross-validation
        logger.info("Running cross-validation...")
        is_valid, errors = CrossValidator.validate(content_input, content_output)
        if not is_valid:
            logger.warning(f"Validation errors: {errors}")
        
        # Step 7: Render media files
        logger.info("Rendering media files...")
        generated_files = {}
        
        # Create session output directory
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = OUTPUT_DIR / session_id
        session_dir.mkdir(exist_ok=True)
        
        # Render slides
        if "slides" in request.render_formats:
            try:
                renderer = slide_renderer.SlideRenderer(output_dir=str(session_dir))
                slide_file = renderer.render(content_output, format="html")
                generated_files["slides"] = f"/outputs/{session_id}/{slide_file.name}"
                logger.info(f"✅ Slides rendered: {slide_file.name}")
            except Exception as e:
                logger.error(f"Slide rendering failed: {e}")
                generated_files["slides_error"] = str(e)
        
        # Render diagrams
        if "diagrams" in request.render_formats:
            try:
                renderer = diagram_renderer.DiagramRenderer(output_dir=str(session_dir))
                diagram_files = renderer.render(content_output, format="svg")
                generated_files["diagrams"] = [
                    f"/outputs/{session_id}/{f.name}" for f in diagram_files
                ]
                logger.info(f"✅ Diagrams rendered: {len(diagram_files)} files")
            except Exception as e:
                logger.error(f"Diagram rendering failed: {e}")
                generated_files["diagrams_error"] = str(e)
        
        # Render audio
        if "audio" in request.render_formats:
            try:
                renderer = audio_renderer.AudioRenderer(output_dir=str(session_dir))
                audio_files = renderer.render(content_output)
                generated_files["audio"] = [
                    f"/outputs/{session_id}/{f.name}" for f in audio_files
                ]
                logger.info(f"✅ Audio rendered: {len(audio_files)} files")
            except Exception as e:
                logger.error(f"Audio rendering failed: {e}")
                generated_files["audio_error"] = str(e)
        
        # Calculate generation time
        generation_time = (datetime.now() - start_time).total_seconds()
        
        # Return response
        return GenerateResponse(
            success=True,
            message=f"Content generated successfully in {generation_time:.2f}s",
            content_output=content_output.model_dump(),
            generated_files=generated_files,
            validation_warnings=errors if not is_valid else None,
            generation_time_sec=generation_time
        )
    
    except Exception as e:
        logger.error(f"Content generation failed: {e}")
        logger.error(traceback.format_exc())
        raise HTTPException(
            status_code=500,
            detail=f"Content generation failed: {str(e)}"
        )


@app.get("/outputs/{session_id}/{filename}")
async def download_file(session_id: str, filename: str):
    """Download a generated output file."""
    file_path = OUTPUT_DIR / session_id / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=file_path,
        filename=filename,
        media_type="application/octet-stream"
    )


@app.get("/sessions")
async def list_sessions():
    """List all generation sessions."""
    sessions = []
    for session_dir in OUTPUT_DIR.iterdir():
        if session_dir.is_dir():
            files = [f.name for f in session_dir.iterdir() if f.is_file()]
            sessions.append({
                "session_id": session_dir.name,
                "file_count": len(files),
                "files": files
            })
    return {"sessions": sessions}


if __name__ == "__main__":
    import uvicorn
    
    print("=" * 70)
    print("STARTING EDUFORGE API SERVER")
    print("=" * 70)
    print("\n📚 Educational Content Generation API")
    print("\nEndpoints:")
    print("  - POST   http://localhost:8000/generate")
    print("  - GET    http://localhost:8000/health")
    print("  - GET    http://localhost:8000/sessions")
    print("  - GET    http://localhost:8000/outputs/{session_id}/{filename}")
    print("\n📖 Interactive API docs: http://localhost:8000/docs")
    print("\n" + "=" * 70 + "\n")
    
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
