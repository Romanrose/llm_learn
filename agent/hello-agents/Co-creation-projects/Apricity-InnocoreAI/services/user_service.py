"""
用户服务
"""

from typing import Optional, List
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from ..core.database import get_db
from ..models.user import UserDB, User, UserCreate, UserUpdate
from ..core.exceptions import UserNotFoundError, UserAlreadyExistsError

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class UserService:
    """用户服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """验证密码"""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """获取密码哈希"""
        return pwd_context.hash(password)
    
    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        user_db = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user_db:
            raise UserNotFoundError(f"User with id {user_id} not found")
        return User.from_orm(user_db)
    
    def get_user_by_email(self, email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        user_db = self.db.query(UserDB).filter(UserDB.email == email).first()
        if not user_db:
            raise UserNotFoundError(f"User with email {email} not found")
        return User.from_orm(user_db)
    
    def get_user_by_username(self, username: str) -> Optional[User]:
        """根据用户名获取用户"""
        user_db = self.db.query(UserDB).filter(UserDB.username == username).first()
        if not user_db:
            raise UserNotFoundError(f"User with username {username} not found")
        return User.from_orm(user_db)
    
    def create_user(self, user_create: UserCreate) -> User:
        """创建用户"""
        # 检查邮箱是否已存在
        if self.db.query(UserDB).filter(UserDB.email == user_create.email).first():
            raise UserAlreadyExistsError(f"Email {user_create.email} already registered")
        
        # 检查用户名是否已存在
        if self.db.query(UserDB).filter(UserDB.username == user_create.username).first():
            raise UserAlreadyExistsError(f"Username {user_create.username} already taken")
        
        # 创建新用户
        hashed_password = self.get_password_hash(user_create.password)
        user_db = UserDB(
            username=user_create.username,
            email=user_create.email,
            hashed_password=hashed_password,
            full_name=user_create.full_name,
            institution=user_create.institution,
            research_field=user_create.research_field
        )
        
        self.db.add(user_db)
        self.db.commit()
        self.db.refresh(user_db)
        
        return User.from_orm(user_db)
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> User:
        """更新用户信息"""
        user_db = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user_db:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        # 更新字段
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user_db, field, value)
        
        self.db.commit()
        self.db.refresh(user_db)
        
        return User.from_orm(user_db)
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        user_db = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user_db:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        self.db.delete(user_db)
        self.db.commit()
        
        return True
    
    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """验证用户登录"""
        try:
            user = self.get_user_by_email(email)
            if self.verify_password(password, user.hashed_password):
                return user
        except UserNotFoundError:
            pass
        return None
    
    def change_password(self, user_id: int, current_password: str, new_password: str) -> bool:
        """修改密码"""
        user_db = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not user_db:
            raise UserNotFoundError(f"User with id {user_id} not found")
        
        if not self.verify_password(current_password, user_db.hashed_password):
            return False
        
        user_db.hashed_password = self.get_password_hash(new_password)
        self.db.commit()
        
        return True