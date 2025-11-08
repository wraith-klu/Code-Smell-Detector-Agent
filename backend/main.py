from fastapi import FastAPI, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from agent_logic import analyze_user_query

app = FastAPI(title="Code Smell Detection API")

# Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "API is running"}

@app.post("/analyze")
async def analyze_code(user_query: str = Form(...), file: UploadFile = None):
    if file is None:
        raise HTTPException(status_code=400, detail="No file uploaded")
    try:
        code = (await file.read()).decode("utf-8")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to read file: {e}")

    try:
        llm_result = analyze_user_query(user_query, code)
        return JSONResponse(content=llm_result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {e}")


@app.post("/followup")
async def followup_query(user_query: str = Form(...), session_id: str = Form(...)):
    try:
        result = analyze_user_query(user_query, "")
        return JSONResponse(content={"followup_response": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Follow-up failed: {e}")
