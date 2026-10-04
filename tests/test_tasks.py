from unittest.mock import patch


@patch("routers.tasks.send_task_email.delay")
def test_create_task(mock_send_email,client,test_admin,test_user):
    login_response=client.post("/auth/token",
                               data={"username":"testadmin",
                                     "password":"adminpassword"})
    assert login_response.status_code==200

    token=login_response.json()["access_token"]
    response=client.post("/admin/tasks",
                         headers={"Authorization":f"bearer {token}"},
                         json={"title":"complete fastapi docs",
                               "assign_to_User":"testuser"})
    assert response.status_code==200
    data=response.json()
    assert data["title"]=="complete fastapi docs"
    assert data["assigned_to"]=="testuser"
    assert data["status"]=="pending"
    mock_send_email.assert_called_once()

def test_student_cannot_create_task(client,test_user):
    login_response=client.post("/auth/token",
                               data={
                                   "username":"testuser",
                                   "password":"testpassword"
                               })
    assert login_response.status_code==200
    token=login_response.json()["access_token"]
    response=client.post("/admin/tasks",
                         headers={"Authorization":f"bearer {token}"},
                         json={"title":"try to create a task",
                               "assign_to_User":"testuser"})
    assert response.status_code==403

def test_create_task_user_not_found(client,test_admin):
    login_response=client.post("/auth/token",
                               data={
                                     "username":"testadmin",
                                     "password":"adminpassword"})
    assert login_response.status_code==200
    token=login_response.json()["access_token"]
    response=client.post("/admin/tasks",
                         headers={"Authorization":f"bearer {token}"},
                         json={"title":"assigning a task to unknownuser",
                               "assign_to_User":"userdoesnotexist"})
    assert response.status_code==404
    data=response.json()
    assert data["detail"]=="Assigned user not found"


def test_task_cannot__assign_to_admin(client,test_admin):
    login_response=client.post("/auth/token",
                               data={"username":"testadmin",
                                     "password":"adminpassword"})
    assert login_response.status_code==200
    token=login_response.json()["access_token"]
    response=client.post("/admin/tasks",
                         headers={"Authorization":f"bearer {token}"},
                         json={"title":"complete fastapi todo api",
                               "assign_to_User":"testadmin"})
    assert response.status_code==400
    data=response.json()
    assert data["detail"]=="Tasks can only be assigned to students"

@patch("routers.tasks.send_task_email.delay")
def test_get_my_tasks(mock_send_email,client,test_admin,test_user):
    admin_login=client.post("/auth/token",
                            data={"username":"testadmin",
                                  "password":"adminpassword"})
    assert admin_login.status_code==200
    admin_token=admin_login.json()["access_token"]

    create_response=client.post("/admin/tasks",
                                headers={"Authorization":f"bearer {admin_token}"},
                                json={"title":"complete fastapi docs",
                                      "assign_to_User":"testuser"})
    assert create_response.status_code==200

    student_login=client.post("/auth/token",
                              data={"username":"testuser",
                                    "password":"testpassword"})
    assert student_login.status_code==200
    student_token=student_login.json()["access_token"]
    response=client.get("/tasks",
                        headers={"Authorization":f"bearer {student_token}"},)
    assert response.status_code==200

    data=response.json()
    assert data["message"]=="Tasks retrieved successfully"
    assert len(data["tasks"])==1
    assert data["tasks"][0]["title"]=="complete fastapi docs"

def test_get_my_tasks_no_tasks(client,test_user):
    login_response=client.post("/auth/token",
                               data={
                                   "username":"testuser",
                                   "password":"testpassword"
                               })
    assert login_response.status_code==200
    token=login_response.json()["access_token"]
    response=client.get("/tasks",
                        headers={"Authorization":f"bearer {token}"},)
    assert response.status_code==200
    data=response.json()
    assert data["message"]=="No tasks assigned to you"
    assert data["tasks"]==[]



@patch("routers.tasks.send_task_email.delay")
def test_submit_task(mock_send_email,client,test_user,test_admin):
    admin_login=client.post("/auth/token",
                            data={
                                "username":"testadmin",
                                "password":"adminpassword"
                            })
    assert admin_login.status_code==200
    admin_token=admin_login.json()["access_token"]
    create_response=client.post("/admin/tasks",
                               headers={"Authorization":f"bearer {admin_token}"},
                               json={"title":"complete fastapi docs",
                                     "assign_to_User":"testuser"})
    assert create_response.status_code==200
    task_id=create_response.json()["id"]
    mock_send_email.reset_mock()
    student_login=client.post("/auth/token",
                              data={
                                  "username":"testuser",
                                  "password":"testpassword"
                              })
    assert student_login.status_code==200
    student_token=student_login.json()["access_token"]
    response=client.patch(f"/tasks/{task_id}/submit",
                          headers={
                              "Authorization":f"Bearer {student_token}"
                          })
    assert response.status_code==200
    data=response.json()
    assert data["status"]=="submitted"
    assert data["id"]==task_id
    mock_send_email.assert_called_once()
def test_submit_task_not_found(client, test_user):
    student_login = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )
    assert student_login.status_code == 200
    token = student_login.json()["access_token"]
    response = client.patch(
        "/tasks/99999/submit",
        headers={
            "Authorization": f"Bearer {token}"
        }
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Task not found"

@patch("routers.tasks.send_task_email.delay")
def test_review_task(
    mock_send_email,
    client,
    test_user,
    test_admin
):
    # 1. Admin login
    admin_login = client.post(
        "/auth/token",
        data={
            "username": "testadmin",
            "password": "adminpassword"
        }
    )

    assert admin_login.status_code == 200

    admin_token = admin_login.json()["access_token"]

    # 2. Admin creates task
    create_response = client.post(
        "/admin/tasks",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "title": "Complete FastAPI docs",
            "assign_to_User": "testuser"
        }
    )

    assert create_response.status_code == 200

    task_id = create_response.json()["id"]

    # Ignore email sent when task was created
    mock_send_email.reset_mock()

    # 3. Student login
    student_login = client.post(
        "/auth/token",
        data={
            "username": "testuser",
            "password": "testpassword"
        }
    )

    assert student_login.status_code == 200

    student_token = student_login.json()["access_token"]

    # 4. Student submits task
    submit_response = client.patch(
        f"/tasks/{task_id}/submit",
        headers={
            "Authorization": f"Bearer {student_token}"
        }
    )

    assert submit_response.status_code == 200

    # Ignore email sent when student submitted
    mock_send_email.reset_mock()

    # 5. Admin reviews task
    review_response = client.patch(
        f"/admin/tasks/{task_id}/review",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "status": "completed"
        }
    )

    assert review_response.status_code == 200

    data = review_response.json()

    # 6. Check response
    assert data["id"] == task_id
    assert data["status"] == "completed"

    mock_send_email.assert_called_once()
