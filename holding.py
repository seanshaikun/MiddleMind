from fasthtml.common import *
from passlib.context import CryptContext
from functools import wraps


db = database('data/news2.db')
content = db.t.content
users = db.t.users
curated = db.t.curated

if content not in db.t:
    content.create(id=int, topic=str, title=str, link=str, date=str, pk='id')
    users.create(email=str, name=str, password=str, admin=int, pk='email')
    curated.create(id=int, topic=str, title=str, link=str, user=str, cat=str, pk='id')

# Although you can just use dicts, it can be helpful to have types for your DB objects.
# The `dataclass` method creates that type, and stores it in the object, so it will use it for any returned items.

Content = content.dataclass()
Users = users.dataclass()
Curated = curated.dataclass()

login_redir = RedirectResponse('/curated', status_code=303)

app, rt = fast_app()
tid=f'curated-{Curated.id}'

def Article(s):
    return Div(
        H4(A(s.title, href=s.link)),
        # Img(src=s.image_url) if s.image_url else None,
        # P(s.summary),
        # P(A("HN Comments", href=s.hn_comments)),
        cls="article",
    )

def Food(s):
    return Div(
        H4(A(s.title, href=s.link),f' {s.topic}'),
        # Img(src=s.image_url) if s.image_url else None,
        # P(s.summary),
        # P(A("HN Comments", href=s.hn_comments)),
        cls="article",
    )

@rt("/")
def get():
    return Titled('The Middle Mind Collective',A('News',hx_get="/page1", hx_target="#page-content"),
    A('Curated',hx_get='/page2',hx_target="#page-content"),
    Div(page1(),id='page-content'))
                

@rt("/page1")
def page1():
    stories = content()
    return Div(
        Grid(
            Div(H2('Free Speach'),P(*(Article(s) for s in stories if "Free Speach" in s.topic))),
            Div(H2('AI'),P(*(Article(s) for s in stories if "AI" in s.topic))),
            Div(H2('Health'),P(*(Article(s) for s in stories if "Health" in s.topic)))),
        Grid(
            Div(H2('Boarder Security'),P(*(Article(s) for s in stories if "Boarder Security" in s.topic))),
            Div(H2('Nuclear War'),P(*(Article(s) for s in stories if "Nuclear War" in s.topic))),
            Div(H2('Cosmic Intervention'),P(*(Article(s) for s in stories if "Cosmic Intervention" in s.topic)))))

@rt("/page2")
def page2():
    stories = curated()
    return Div(
        Grid(
            Div(H2('Articles'),P(*(Food(s) for s in stories if "Article" in s.cat))),
            Div(H2('Media'),P(*(Food(s) for s in stories if "Media" in s.cat))),
            Div(H2('Original'),P(*(Food(s) for s in stories if "Original" in s.cat)))))


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

@rt('/register')
def get():
    return Container(
        Div(
            H1("Register"),
            auth_form("Register", "/register"),
            Hr(),
            P("Already have an account? ", A("Login", href="/login"))#,cls="mw-480 mx-auto"
        )
    )

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@rt('/register')
def post(email:str, password:str):
    
    try:
        users[email]
        return "User already exists"
    except NotFoundError:

        new_user = Users(email=email, password=get_password_hash(password))
    
        users.insert(new_user)
        
        return HttpHeader('HX-Redirect', '/login')


@rt('/login')
def get():
    return Container(
        Div(
            H1("Login"),
            auth_form("Login", target="/login"),
            Hr(),
            P("Want to create an Account? ", A("Register", href="/register"))#,cls="mw-480 mx-auto"
        )
    )
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

@rt('/login')
def post(session, email:str, password:str):
    try:
        user = users[email]
    except NotFoundError:
        return "Email or password are incorrect"
    
    if not verify_password(password, user.password):
        return "Email or password are incorrect"

    session['auth'] = user.email
    
    return HttpHeader('HX-Redirect', '/dashboard')

def basic_auth(f):
    @wraps(f)
    def wrapper(session, *args, **kwargs):
        if "auth" not in session:
            return Response('Not Authorized', status_code=401)
        return f(session, *args, **kwargs)
    return wrapper

@rt('/dashboard')
@basic_auth
def get(session):    
    return Container(
        H1("Dashboard"),A('curated',href='/curated'),
        Button("Logout", hx_post="/logout")
    )
@rt('/logout')
def post(session):
    del session['auth']
    return HttpHeader('HX-Redirect', '/login')

# def render(currated):
#     tid = f'curated-{curated.id}'
#     delete = A('Delete', hx_delete=f'/curated/{Curated.id}', hx_swap='outerHTML', taget_id=tid)
#     return Li(delete, curated.title, id=tid)

@patch
def __ft__(self:Curated):
    show = AX(self.title, f'/curated/{self.id}', target_id=tid)
    delete = AX(f'Delete {self.title}', f'/curated/{self.id}', hx_swap='outerHTML', target_id=tid)
    # edit = AX('edit',     f'/edit/{self.id}' , taget_id=tid)
    # dt = ' (done)' if self.done else ''
    return Li(delete, id=tid)

# @patch
# def __ft__(self:Curated):
#     tid = f'curated-{Curated.id}'
#     delete = AX('Delete', hx_delete=f'/curated/{Curated.id}', hx_swap='outerHTML', taget_id=tid)
#     return Li(delete, f'{Curated.title}', id=tid)

def mk_input(**kw): return Input(id="new-title", name="title", placeholder="New Currated", **kw)

@rt("/curated")
@basic_auth
def get(session):
    return Titled('Curated',
                  Card(
                      Ul(*curated(), id='curated_list'), header = sub_form('Add', '/curated'))
                      )
        

@rt('/curated')
def post(topic:str, title:str,link:str,cat:str,user:str):
    new_article = Curated(topic=topic, title=title, link=link, user=user, cat=cat)
    curated.insert(new_article)
    return HttpHeader('HX-Redirect', '/curated')

# def replace(curated: Curated): return curated.update(curated), clear('current-curated')

@rt('/curated/{tid}')
def get(tid:int):
    curated.delete(tid)
    return Title({tid})


serve()