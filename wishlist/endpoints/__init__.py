from fastapi import APIRouter, Security

from wishlist.endpoints.auth import get_current_user
from wishlist.endpoints.auth import router as auth_router
from wishlist.endpoints.myself import router as myself_router
from wishlist.endpoints.user import router as user_router

router = APIRouter()
router.include_router(user_router, tags=["User"])
router.include_router(auth_router, tags=["Authentication"])
router.include_router(myself_router, tags=["Myself"], prefix="/me")
