from fastapi import FastAPI, Request, Form, Query
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import json
import os
import markdown
import google.generativeai as genai
from fastapi.responses import JSONResponse

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
# ==========================
# Gemini Configuration
# ==========================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)
    gemini_model = genai.GenerativeModel("gemini-2.5-flash")
else:
    gemini_model = None

# ==========================
# Static Files
# ==========================

app.mount(
    "/static",
    StaticFiles(directory=os.path.join(BASE_DIR, "static")),
    name="static"
)

# ==========================
# Templates
# ==========================

templates = Jinja2Templates(
    directory="templates"
)

# ==========================
# Load Schemes
# ==========================


with open(
    os.path.join(BASE_DIR, "static", "data", "schemes.json"),
    "r",
    encoding="utf-8"
) as file:
    schemes = json.load(file)

# ==========================
# Home Page
# ==========================

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):

    # Home
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request
        }
    )

# ==========================
# Eligibility Page
# ==========================

@app.get("/eligibility", response_class=HTMLResponse)
async def eligibility(request: Request):

    return templates.TemplateResponse(
        "eligibility.html",
        {
            "request": request
        }
    )

# ==========================
# Results Page
# ==========================

@app.post("/results", response_class=HTMLResponse)
async def results(

    request: Request,

    age: int = Form(...),

    gender: str = Form(...),

    state: str = Form(...),

    occupation: str = Form(...),

    education: str = Form(...),

    income: int = Form(...),

    category: str = Form(...)

):

    recommended_schemes = []

    for scheme in schemes:

        score = 0

        # Occupation Match
        if occupation.lower() == scheme["occupation"].lower():
            score += 30

        # Income Match
        if income <= scheme["income_limit"]:
            score += 25

        # State Match
        if (
            scheme["state"] == "All"
            or state.lower() == scheme["state"].lower()
        ):
            score += 15

        # Age Match
        if (
            scheme["minimum_age"]
            <= age
            <= scheme["maximum_age"]
        ):
            score += 15

        # Education Match
        if education in scheme["education_required"]:
            score += 10

        # Category Match
        if category in scheme["category"]:
            score += 5

        # Recommendation Status

        if score >= 85:

            status = "Highly Recommended"

        elif score >= 70:

            status = "Recommended"

        elif score >= 50:

            status = "Partially Eligible"

        else:

            status = "Not Eligible"

        # Show only relevant schemes

        if score >= 50:

            scheme_copy = scheme.copy()

            scheme_copy["score"] = score

            scheme_copy["status"] = status

            recommended_schemes.append(
                scheme_copy
            )

    # Sort by score

    recommended_schemes.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    return templates.TemplateResponse(
        "results.html",
        context={
            "request": request,
            "schemes": recommended_schemes
        }
    )

# ==========================
# Scheme Details
# ==========================

@app.get("/scheme/{scheme_id}", response_class=HTMLResponse)
async def scheme_details(

    request: Request,

    scheme_id: int,

    score: int = Query(0),

    status: str = Query("Eligible")

):

    selected_scheme = None

    for scheme in schemes:

        if scheme["id"] == scheme_id:

            selected_scheme = scheme.copy()

            selected_scheme["score"] = score

            selected_scheme["status"] = status

            break

    return templates.TemplateResponse(
        "scheme_details.html",
        {
            "request": request,
            "scheme": selected_scheme
        }
    )

@app.post("/ask-ai")
async def ask_ai(request: Request):

    try:

        data = await request.json()

        question = data.get(
            "question",
            ""
        )

        scheme_name = data.get(
            "scheme_name",
            ""
        )

        benefits = data.get(
            "benefits",
            ""
        )

        if not question:

            return JSONResponse(
                {
                    "response": "Please enter a question."
                }
            )

        if gemini_model is None:

            return JSONResponse(
                {
                    "response": "Gemini API key is not configured."
                }
            )

        prompt = f"""
        You are SchemeAI.

        Answer in plain text only.
        Do NOT use:
        - Markdown
        - **
        - *
        - #
        - tables

        Give clean readable paragraphs and numbered points.

        Scheme Name:
        {scheme_name}

        Scheme Benefits:
        {benefits}

        User Question:
        {question}

        Rules:
        - Answer only regarding this scheme.
        - Give concise answers.
        - Use bullet points when needed.
        - Maximum 150 words.
        - If eligibility is asked, explain who can apply.
        """

        response = gemini_model.generate_content(prompt)

        html_response = markdown.markdown(response.text)

        return JSONResponse({
            "response": html_response
        })

    except Exception as e:

        return JSONResponse(
            {
                "response": f"Error: {str(e)}"
            }
        )