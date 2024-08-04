from fastapi import FastAPI
from database import engine
from app.auth.routes import auth_entre,auth,admin,users
from app.reviews.routes import reviews
from app.blog.routes import blog,comments
from app.booking.router import booking,resources
from app.event.routes import events
from app.todos.routes import todos
from app.models import *
from database import Base

#from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(auth_entre.router)
app.include_router(events.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(users.router)
app.include_router(blog.router)
app.include_router(reviews.router)
app.include_router(comments.router)
app.include_router(resources.router)
app.include_router(booking.router)
