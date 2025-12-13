# middleware.py
from flask import session, redirect, url_for, request, flash
from functools import wraps

def login_required(role=None):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # Verificar si el usuario está logueado
            if 'user_id' not in session:
                flash('Debes iniciar sesión para acceder a esta página', 'error')
                return redirect(url_for('login'))
            
            # Verificar rol si se especifica
            if role and session.get('user_role') != role:
                flash('No tienes permisos para acceder a esta página', 'error')
                return redirect(url_for("inicio"))
            
            # Headers para prevenir cache
            response = f(*args, **kwargs)
            if hasattr(response, 'headers'):
                response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
                response.headers['Pragma'] = 'no-cache'
                response.headers['Expires'] = '0'
            return response
        return decorated_function
    return decorator