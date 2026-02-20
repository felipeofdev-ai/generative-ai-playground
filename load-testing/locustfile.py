from locust import HttpUser, task

class NexusUser(HttpUser):
    @task
    def chat(self):
        self.client.post("/api/v1/nexus/chat", json={"prompt": "hello", "mode": "chat"})
