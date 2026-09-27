from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from celery_tasks import send_task_email
from database import get_session
from models import User, Task
from security import get_current_user, require_admin
from schemas import Taskcreate, Taskresponse, TaskReview

router = APIRouter(
    tags=["Tasks"]
)

@router.post(
    "/admin/tasks",
    response_model=Taskresponse
)
def create_task(
    task_data: Taskcreate,
    current_user: User = Depends(require_admin),
    session: Session = Depends(get_session)
):
    user = session.exec(
    select(User).where(
        User.username == task_data.assign_to_User)).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Assigned user not found"
        )

    if user.role != "student":
        raise HTTPException(
            status_code=400,
            detail="Tasks can only be assigned to students"
        )

    # Create task
    task = Task(
        title=task_data.title,
        assigned_to=user.id,
        assigned_by=current_user.id,
        status="pending"
    )

    session.add(task)
    session.commit()
    session.refresh(task)

    # Email the student
    send_task_email.delay(
        receiver_mail=user.email,
        subject="New Task Assigned",
        body=f"""
Hello {user.username},

A new task has been assigned to you.

Task ID: {task.id}
Task: {task.title}
Status: {task.status}

Please complete the task and submit it once finished.

Thank you,
Todo App
"""
    )

    return Taskresponse(
    id=task.id,
    title=task.title,
    assigned_to=user.username,
    assigned_by=task.assigned_by,
    status=task.status
)


@router.get("/tasks")
def get_my_tasks(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    statement = select(Task).where(
        Task.assigned_to == current_user.id
    )

    tasks = session.exec(statement).all()

    if not tasks:
        return {
            "message": "No tasks assigned to you",
            "tasks": []
        }

    return {
        "message": "Tasks retrieved successfully",
        "tasks": tasks
    }


@router.patch(
    "/tasks/{task_id}/submit",
    response_model=Taskresponse
)
def submit_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    if task.assigned_to != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to submit this task"
        )

    # Only pending tasks can be submitted
    if task.status != "pending":
        raise HTTPException(
            status_code=400,
            detail="Only pending tasks can be submitted"
        )

    # Update status
    task.status = "submitted"

    session.add(task)
    session.commit()
    session.refresh(task)

    # Find the admin who assigned this task
    admin = session.get(
        User,
        task.assigned_by
    )

    # Email the respective admin
    if admin:
        send_task_email.delay(
            receiver_mail=admin.email,
            subject="Task Submitted",
            body=f"""
Hello {admin.username},

The following task has been submitted.

Task ID: {task.id}
Task: {task.title}
Submitted by: {current_user.username}
Student Email: {current_user.email}

Please review the task.

Thank you,
Todo App
"""
        )

    return task


# Admin reviews a submitted task
@router.patch(
    "/admin/tasks/{task_id}/review",
    response_model=Taskresponse
)
def review_task(
    task_id: int,
    review_data: TaskReview,
    session: Session = Depends(get_session),
    current_user: User = Depends(require_admin)
):
    # Find task
    task = session.get(Task, task_id)

    if not task:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    # Task must be submitted first
    if task.status != "submitted":
        raise HTTPException(
            status_code=400,
            detail="Task has not been submitted"
        )

    # Only the admin who assigned the task can review it
    if task.assigned_by != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You are not allowed to review this task"
        )

    # Update status
    task.status = review_data.status

    session.add(task)
    session.commit()
    session.refresh(task)

    # Find student
    student = session.get(
        User,
        task.assigned_to
    )

    # Email student
    if student:
        send_task_email.delay(
            receiver_mail=student.email,
            subject="Task Review Update",
            body=f"""
Hello {student.username},

Your task has been reviewed by the admin.

Task ID: {task.id}
Task: {task.title}
Status: {task.status}

Thank you,
Todo App
"""
        )

    return task