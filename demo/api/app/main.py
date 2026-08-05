from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from app.routers import (
    auth,
    contact_groups,
    contacts,
    email,
    fax,
    group_contacts,
    groups,
    health,
    optout,
    rcs,
    settings,
    sms,
    tts,
    voice,
    whatsapp,
    workflow,
)

app = FastAPI(title="tnzapi-python demo API")


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"Result": "Failed", "ErrorMessage": [str(exc)]})


app.include_router(health.router)
app.include_router(auth.router)
app.include_router(contact_groups.router)
app.include_router(contacts.router)
app.include_router(email.router)
app.include_router(fax.router)
app.include_router(group_contacts.router)
app.include_router(groups.router)
app.include_router(optout.router)
app.include_router(rcs.router)
app.include_router(settings.router)
app.include_router(sms.router)
app.include_router(tts.router)
app.include_router(voice.router)
app.include_router(whatsapp.router)
app.include_router(workflow.router)
