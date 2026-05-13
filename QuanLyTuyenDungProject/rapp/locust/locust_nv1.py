import random

from locust import HttpUser, task, between


class PostJobUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        self.client.post("/login", data={
            "username": "employer1",
            "password": "123456",
        })

    @task(5)
    def get_home_page(self):
        keywords = ["Python", "Java", "Kế toán", "Marketing"]
        kw = random.choice(keywords)
        self.client.get(f"/?kw={kw}")

    @task(3)
    def get_job_create_form(self):
        self.client.get("/jobs/create")

    @task(4)
    def post_create_job(self):
        self.client.post("/jobs", data={
            "title": f"Lập trình viên Python Senior {random.randint(1, 9999)}",
            "description": "Yêu cầu kinh nghiệm thực chiến từ 2 năm trở lên.",
            "salary": str(random.randint(5000000, 50000000)),
            "deadline": "2026-12-31",
            "category_id": str(random.randint(1, 3)),
        })

