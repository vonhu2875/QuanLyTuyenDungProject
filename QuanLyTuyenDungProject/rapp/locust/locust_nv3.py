import random

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
        self.client.get("/manage-applications")
        self.client.get("/manage_jobs")

    @task(3)
    def get_manage_applications(self):
        self.client.get("/jobs/1/manage-applications")

    @task(2)
    def update_update_status(self):
        statuses = ["INTERVIEW", "ACCEPTED", "REJECTED"]
        data = {"status": random.choice(statuses)}
        method = random.choice(["POST", "PATCH"])

        if method == "POST":
            self.client.post("/jobs/1/applications/1/status", data=data)
        else:
            self.client.patch("/jobs/1/applications/1/status", data=data)

    @task(2)
    def post_toggle_status(self):
        self.client.post("/toggle_job_status/1")

    @task(1)
    def delete_job_task(self):
        with self.client.delete("/delete_job/2", catch_response=True) as res:
            if res.status_code in [200, 302]:
                res.success()
            elif res.status_code == 404:
                res.success()
            else:
                res.failure(f"Lỗi không xác định: {res.status_code}")

    @task(2)
    def get_edit_job(self):
        payload = {
            "title": "Lập trình viên Python Senior",
            "salary": "25000000",
            "deadline": "2026-12-31",
            "category": "1",
            "description": "Cần người có kinh nghiệm thực chiến."
        }
        self.client.patch("/edit_job/1", data=payload)

