from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import pandas as pd

app = FastAPI()

# Mount static folder for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")

# Load templates
templates = Jinja2Templates(directory="templates")

# Load Excel into memory
def load_error_data(file_path="err_codes.xlsx"):
    all_sheets = pd.read_excel(file_path, sheet_name=None)
    dfs = []
    for df in all_sheets.values():
        df = df.copy()
        df.columns = (
            df.columns.str.strip()
            .str.lower()
            .str.replace(" ", "_")
            .str.replace("my_action_plan", "action_plan")
            .str.replace("action_plan_recommended", "action_plan")
        )
        dfs.append(df)
    merged = pd.concat(dfs, ignore_index=True)
    return merged

df = load_error_data()


# -------- API ROUTES -------- #
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/lookup")
async def lookup_code(code: str):
    code = code.strip().upper()
    row = df[df["code"].str.upper() == code]

    if row.empty:
        return JSONResponse({"error": f"Code {code} not found"}, status_code=404)

    return row.iloc[0].to_dict()
