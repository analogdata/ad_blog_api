from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
import enum
from sqlmodel import SQLModel, Field, Relationship

if TYPE_CHECKING:
    from app.db.models.user import User


class PermissionName(str, enum.Enum):
    # Article permissions
    CREATE_ARTICLE = "create_article"
    EDIT_OWN_ARTICLE = "edit_own_article"
    EDIT_ANY_ARTICLE = "edit_any_article"
    DELETE_OWN_ARTICLE = "delete_own_article"
    DELETE_ANY_ARTICLE = "delete_any_article"
    PUBLISH_ARTICLE = "publish_article"
    SCHEDULE_ARTICLE = "schedule_article"
    FEATURE_ARTICLE = "feature_article"

    # User management
    CREATE_USER = "create_user"
    EDIT_OWN_PROFILE = "edit_own_profile"
    EDIT_ANY_PROFILE = "edit_any_profile"
    DELETE_USER = "delete_user"

    # Categories and tags
    MANAGE_CATEGORIES = "manage_categories"
    MANAGE_TAGS = "manage_tags"

    # Analytics
    VIEW_OWN_ANALYTICS = "view_own_analytics"
    VIEW_ALL_ANALYTICS = "view_all_analytics"


class Permission(SQLModel, table=True):
    __tablename__ = "permissions"
    id: int = Field(default=None, primary_key=True)
    name: PermissionName = Field(index=True)
    description: Optional[str] = Field(default=None)
    user_id: int = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

    # Relationship
    user: "User" = Relationship(back_populates="permissions")
