def register_and_login(client):
    response=client.post("/register",data={"email":"test@example.com","full_name":"Test User","password":"password123"},follow_redirects=False)
    assert response.status_code==303
    return response

def test_health(client):
    response=client.get("/health")
    assert response.status_code==200
    assert response.json()["status"]=="ok"

def test_register_login_session(client):
    register_and_login(client)
    session=client.get("/session-info")
    assert session.status_code==200
    assert session.json()["email"]=="test@example.com"

def test_home_fallback_and_history(client):
    register_and_login(client)
    payload={"total_budget":50000,"rooms":["Living Room"],"items":[{"category":"ceiling light","quantity":2},{"category":"curtain","quantity":2}],"style":"modern","additional_requirements":""}
    response=client.post("/generate-home",json=payload)
    assert response.status_code==200
    body=response.json()
    assert body["result"]["planner_type"]=="home"
    assert body["result"]["mode"]=="demo"
    assert body["id"]>0
    history=client.get("/history")
    assert history.status_code==200
    assert len(history.json())==1

def test_party_fallback(client):
    register_and_login(client)
    payload={"total_budget":30000,"guest_count":30,"event_type":"birthday","venue_type":"hall","catering_needed":True,"decoration_needed":True,"entertainment_needed":False,"city":"Palakkad","additional_requirements":""}
    response=client.post("/generate-party",json=payload)
    assert response.status_code==200
    assert response.json()["result"]["planner_type"]=="party"

def test_jewelry_fallback(client):
    register_and_login(client)
    response=client.post("/generate-jewelry",data={"total_budget":"15000","occasion":"wedding","style_preferences":"elegant","metal_preference":"gold","color_preference":"gold","additional_requirements":""})
    assert response.status_code==200
    assert response.json()["result"]["planner_type"]=="jewelry"


def test_recommendation_detail_and_history_page(client):
    register_and_login(client)
    payload={"total_budget":10000,"rooms":["Bedroom"],"items":[{"category":"lamp","quantity":1}],"style":"minimal","additional_requirements":""}
    created=client.post("/generate-home",json=payload).json()
    rid=created["id"]
    detail=client.get(f"/recommendations-details/{rid}")
    assert detail.status_code==200
    assert detail.json()["id"]==rid
    page=client.get(f"/recommendation/{rid}")
    assert page.status_code==200
    history_page=client.get("/history-page")
    assert history_page.status_code==200
