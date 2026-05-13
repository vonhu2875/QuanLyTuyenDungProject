import random
import io
from locust import HttpUser, task, between


class MyUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post(
            "/login", data={
                "username": "employer1",
                "password": "123456",
            })

    @task(5)
    def get_management_pages(self):
        self.client.get("/applications")
        self.client.get("/users/jobs")

    @task(2)
    def update_application_status(self):
        statuses = ["INTERVIEW", "ACCEPTED", "REJECTED"]
        data = {"status": random.choice(statuses)}

        self.client.patch("/applications/1/status", data=data)

    @task(2)
    def post_toggle_status(self):
        data = {"action": "toggle"}
        self.client.patch("/jobs/1", data=data)

    @task(1)
    def delete_job_task(self):
        with self.client.delete("/jobs/2", catch_response=True) as res:
            if res.status_code in [200, 302]:
                res.success()
            elif res.status_code == 404:
                res.success()
            else:
                res.failure(f"Lỗi: {res.status_code}")

    @task(2)
    def patch_edit_job(self):
        payload = {
            "title": "Lập trình viên Python Senior (Updated)",
            "salary": "30000000",
            "deadline": "2026-12-31",
            "category_id": "1",
            "description": "Cập nhật yêu cầu kinh nghiệm."
        }

        self.client.patch("/jobs/1", data=payload)