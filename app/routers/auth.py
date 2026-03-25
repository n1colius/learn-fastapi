# ============================================================
# app/routers/auth.py — Authentication Routes
#
# Laravel equivalent: routes/api.php auth group + AuthController
#
# Routes defined here (prefix /api/auth is added in main.py):
#   POST /api/auth/register  → register a new user
#   POST /api/auth/login     → login and get a JWT token
# ============================================================

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserResponse, Token
from app.services.auth_service import hash_password, verify_password, create_access_token
from app.config import settings


# -------------------------------------------------------
# APIRouter — the modular router object
#
# Laravel equivalent: Route::prefix('auth')->group(function() { ... })
#
# Each router is registered in main.py with app.include_router().
# -------------------------------------------------------
router = APIRouter()


# -------------------------------------------------------
# POST /api/auth/register
#
# Laravel equivalent:
#   public function register(StoreUserRequest $request) { ... }
#
# `body: UserCreate` = FastAPI reads the JSON body and validates it
#   against the UserCreate schema. If validation fails, it returns
#   422 automatically with a clear error message.
#   (In Laravel, this happens via Form Request injection)
#
# `db: Session = Depends(get_db)` = inject a DB session for this request.
#   (In Laravel, you get DB access via facades, not injection)
#
# `response_model=UserResponse` = FastAPI will serialize the return value
#   using the UserResponse schema, stripping any sensitive fields
#   like hashed_password. (In Laravel, this is your API Resource)
# -------------------------------------------------------
@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,  # Returns 201 Created on success
)
def register(body: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.

    Validates the email is unique, hashes the password, creates the user.
    """
    # Check if email is already taken
    # Laravel: User::where('email', $request->email)->exists()
    existing = db.query(User).filter(User.email == body.email).first()
    if existing:
        # HTTP 400 Bad Request — field-level validation error
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists.",
        )

    # Create the User ORM object
    # Note: we store hashed_password, NOT the plain password
    new_user = User(
        name=body.name,
        email=body.email,
        hashed_password=hash_password(body.password),  # Hash::make($password)
    )

    # Save to database
    # Laravel: $user->save() or User::create([...])
    db.add(new_user)    # Stage the new record
    db.commit()         # Write to DB (like DB::commit())
    db.refresh(new_user)  # Reload from DB to get generated id, created_at, etc.

    # FastAPI uses `response_model=UserResponse` to serialize the return value.
    # The UserResponse schema excludes hashed_password automatically.
    return new_user


# -------------------------------------------------------
# POST /api/auth/login
#
# Laravel equivalent:
#   public function login(Request $request) {
#       if (Auth::attempt($credentials)) {
#           return response()->json(['token' => JWTAuth::fromUser(auth()->user())]);
#       }
#   }
#
# OAuth2PasswordRequestForm is a standard FastAPI form dependency.
# It expects form data (not JSON!) with fields: `username` and `password`.
# Note: OAuth2 standard uses "username" even if you use email.
#       We'll treat `username` as the email field.
# -------------------------------------------------------
@router.post("/login", response_model=Token)
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """
    Login with email and password, returns a JWT access token.

    Send as form data (not JSON):
        username: your@email.com
        password: yourpassword

    In Swagger UI, click "Authorize" at the top to set your token globally.
    """
    # Find user by email (OAuth2 uses 'username' field for the identifier)
    user = db.query(User).filter(User.email == form_data.username).first()

    # Verify password — Hash::check($plainPassword, $user->password)
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Your account has been deactivated.",
        )

    # Create the JWT token
    # "sub" (subject) is the standard JWT claim — we store the user ID as a string
    access_token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.access_token_expire_minutes),
    )

    # Return the Token schema — {"access_token": "...", "token_type": "bearer"}
    return Token(access_token=access_token)
