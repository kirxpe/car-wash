from fastapi import Depends, HTTPException, status
from fastapi_users import fastapi_users, FastAPIUsers

from auth.models import User
from auth.manager import get_user_manager
from auth.base_config import auth_backend


fastapi_users = FastAPIUsers[User, int]( #noqa
    get_user_manager,
    [auth_backend],
)
get_current_user = fastapi_users.current_user()


def require_admin(current_user: User = Depends(get_current_user)):
    if current_user.role_id != 1:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

def require_employee_or_admin(current_user: User = Depends(get_current_user)):
    if current_user.role_id not in (1, 2):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Employee or admin access required")
    
def require_admin_or_employee_or_client(current_user: User = Depends(get_current_user)):
    if current_user.role_id not in (1,2,3):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are nobody")