import click
from sqlalchemy.orm import Session
from .database import SessionLocal
from .models import User
from .core.security import get_password_hash


@click.command('create-admin')
@click.option('--email', prompt=True)
@click.option('--password', prompt=True, hide_input=True, confirmation_prompt=True)
@click.option('--name', prompt=True)
def create_admin(email: str, password: str, name: str):
    db = SessionLocal()
    try:
        user = User(
            email=email,
            hashed_password=get_password_hash(password),
            name=name,
            role="admin"
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        click.echo(f"Admin user {email} created successfully.")
    except Exception as e:
        click.echo(f"Error creating admin user: {str(e)}")
    finally:
        db.close()

if __name__ == '__main__':
    create_admin()