from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from medcare.adapters.db.user_manager import (
    UserManager,
    auth_backend,
    current_active_user,
    fastapi_users,
    get_user_manager,
)
from medcare.api.schemas import CPFLoginRequest, UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/auth", tags=["auth"])

router.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/jwt",
)
router.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/register",
)
router.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
)


@router.post("/cpf-login")
async def cpf_login(
    data: CPFLoginRequest,
    user_manager: UserManager = Depends(get_user_manager),
):
    user = await user_manager.authenticate_cpf(data.cpf, data.password)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="CPF ou senha inválidos",
        )

    from medcare.adapters.db.user_manager import auth_backend as backend

    strategy = backend.get_strategy()
    token = await strategy.write_token(user)
    return {"access_token": token, "token_type": "bearer"}
