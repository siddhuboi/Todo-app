
def test_login(client,test_user):
    response=client.post("/auth/token",
                    data={"username":"testuser",
                          "password":"testpassword"}
                         )
    assert response.status_code==200
    data=response.json()
    assert "access_token" in data
    assert data["token_type"]=="bearer"


def test_login_wrong_password(client,test_user):
    response=client.post("/auth/token",
                         data={"username":"testuser",
                               "password":"wrongpassword"})
    assert response.status_code==401
    data=response.json()
    assert data["detail"]=="Incorrect username or password"


def test_get_me(client,test_user):
    login_response=client.post("/auth/token",
                               data={"username":"testuser",
                                     "password":"testpassword"}
                               )
    assert login_response.status_code==200
    token=login_response.json()["access_token"]
    response=client.get("/auth/me",
                        headers={"Authorization":f"bearer {token}"})
    assert response.status_code==200
    data=response.json()
    assert data["username"]=="testuser"
    assert data["email"]=="test@example.com"
    assert data["role"]=="student"


def test_get_me_without_token(client):
    response=client.get("/auth/me")
    assert response.status_code==401
    data=response.json()
    assert data["detail"]=="Not authenticated"



