
def test_create_user(client):
    response=client.post("/create-user",
                         json={
                             "username":"newuser",
                             "email":"newuser@gmail.com",
                             "password":"newpassword",
                             "role":"student"
                         })
    assert response.status_code==200
    data=response.json()
    assert data["username"]=="newuser"
    assert data["email"]=="newuser@gmail.com"
    assert data["role"]=="student"

    assert "password" not in data

def test_create_user_duplicate_user(client,test_user):
    response=client.post("/create-user",
                         json={
                             "username":"testuser",
                             "email":"another@example.com",
                             "password":"anotherpassword",
                             "role":"student"
                         })
    assert response.status_code==400
    assert response.json()["detail"]=="Username already exists"

def test_get_user_me(client,test_user):
    login_response=client.post("/auth/token",
                               data={
                                   "username":"testuser",
                                   "password":"testpassword",
                               })
    assert login_response.status_code==200
    token=login_response.json()["access_token"]
    response=client.get("/users/me",
                        headers={
                            "Authorization":f"bearer {token}"
                        })
    assert response.status_code==200
    data=response.json()
    assert data["username"]=="testuser"
    assert data["email"]=="test@example.com"
    assert data["role"]=="student"

    assert 'password' not in data

def test_patch_user(client, test_admin, test_user):

    admin_login = client.post(
        "/auth/token",
        data={
            "username": "testadmin",
            "password": "adminpassword"
        }
    )

    assert admin_login.status_code == 200

    admin_token = admin_login.json()["access_token"]

    response = client.patch(
        f"/admin/users/{test_user.id}",
        headers={
            "Authorization": f"Bearer {admin_token}"
        },
        json={
            "email": "updated@example.com"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == test_user.id
    assert data["username"] == "testuser"
    assert data["email"] == "updated@example.com"
    assert data["role"] == "student"

    # Password should not be exposed
    assert "password" not in data

def test_update_user(client,test_user,test_admin):
    admin_response=client.post("/auth/token",
                               data={
                                   "username":"testadmin",
                                   "password":"adminpassword"
                               })
    assert admin_response.status_code==200
    token=admin_response.json()["access_token"]
    response=client.put(f"/admin/users/{test_user.id}",
                        headers={"Authorization":f"bearer {token}"},
                        json={
                            "username":"updatedusername",
                            "email":"updatedname@example.com",
                            "role":"student"
                        })
    assert response.status_code==200
    data=response.json()
    assert data["username"]=="updatedusername"
    assert data["email"]=="updatedname@example.com"
    assert data["role"]=="student"
    assert data["id"]==test_user.id

    assert "password" not in data


def test_delete_user(client,test_admin,test_user):
    admin_response=client.post("/auth/token",
                               data={
                                   "username":"testadmin",
                                   "password":"adminpassword"
                               })
    assert admin_response.status_code==200
    token=admin_response.json()["access_token"]
    response=client.delete(f"/admin/users/{test_user.id}",
                           headers={"Authorization":f"bearer {token}"})
    assert response.status_code==200
    assert response.json()["message"]=="User deleted successfully"

