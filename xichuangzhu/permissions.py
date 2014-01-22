# coding: utf-8
from flask import request, g
from functools import wraps
from flask import abort, redirect, url_for, flash
from .models import Topic, WorkReview
import roles


def require_visitor(func):
    """Check if no user login"""
    @wraps(func)
    def decorator(*args, **kwargs):
        if g.current_user:
            return redirect(url_for('forum.index'))
        return func(*args, **kwargs)
    return decorator


class Permission(object):
    def __init__(self, role, extra=True, super_extra=True):
        self.role = role
        self.extra = extra
        self.super_extra = super_extra

    def __call__(self, func):
        @wraps(func)
        def decorator(*args, **kwargs):
            if not self.check():
                return self.deny()
            return func(*args, **kwargs)
        return decorator

    def check(self):
        """判断是否满足权限条件"""
        if g.current_role < self.role:
            return False
        elif g.current_role == self.role:
            return self.extra
        return self.super_extra

    def deny(self, next_url=""):
        """针对不同的role进行不同的处理"""
        if g.current_role == roles.VisitorRole:
            flash('此操作需要登录账户')
            return redirect(url_for('site.index', next=next_url or request.url))
        elif g.current_role == roles.NewUserRole:
            flash('请登录邮箱激活账户')
            return redirect(url_for('account.send_active_email'))
        abort(403)


new_user_permission = Permission(roles.NewUserRole)
user_permission = Permission(roles.UserRole)
admin_permission = Permission(roles.AdminRole)
super_admin_permission = Permission(roles.SuperAdminRole)


class TopicOwnerPermission(Permission):
    def __init__(self, topic_id):
        own = g.current_user and Topic.query.filter(Topic.id == topic_id).filter(
            Topic.user_id == g.current_user.id).count() > 0
        Permission.__init__(self, roles.UserRole, own)


class WorkReviewOwnerPermission(Permission):
    def __init__(self, review_id):
        own = g.current_user and WorkReview.query.filter(WorkReview.id == review_id).filter(
            WorkReview.user_id == g.current_user.id).count() > 0
        Permission.__init__(self, roles.UserRole, own)