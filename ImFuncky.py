from fasthtml.common import *
from passlib.context import CryptContext
from functools import wraps


def auth_form(btn_text, target):
    return Form(
        Input(id="email", type="email", placeholder="Email", required=True),
        Input(id="password", type="password", placeholder="Password", required=True),
        Input(id="name", type = "name", placeholder="Handle", required=True),
        Button(btn_text, type="submit"),
        Span(id="error", style="color:red"),
        hx_post=target,
        hx_target="#error",
    )

def sub_form(btn_text, target):
    return Form(
        Input(id="topic", type="topic", placeholder="topic", required=True),
        Input(id="title", type="title", placeholder="title", required=True),
        Input(id="link", type = "link", placeholder="link", required=True),
        Input(id="cat", type = "cat", placeholder="category", required=True),
        Input(id="user", type = "user", placeholder="Handle", required=True),
        Button(btn_text, type="submit"),
        Span(id="error", style="color:red"),
        hx_post=target,
        hx_target="#error",)
