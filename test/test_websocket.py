from starlette.testclient import TestClient
from main import app
# from starlette.websockets import WebSocket


@app.get("/")
async def read_main():
    return {"msg": "Hello World"}
#
#
# @app.websocket_route("/ws")
# async def websocket(websocket: WebSocket):
#     await websocket.accept()
#     await websocket.send_json({"msg": "Hello WebSocket"})
#     await websocket.close()


def test_read_main():
    client = TestClient(app)
    response = client.get("/")
    assert response.status_code == 200
    print(response.text)
    # assert response.text == "hello"


def test_websocket():
    client = TestClient(app)
    with client.websocket_connect("/ws") as websocket:
        data = websocket.receive_json()
        print(data)
