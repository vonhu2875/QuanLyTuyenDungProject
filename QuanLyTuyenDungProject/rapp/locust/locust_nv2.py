from locust import HttpUser, task, between

class ApplyJobPerformanceTest(HttpUser):
    wait_time = between(2, 5)

    def on_start(self):
        self.client.post("/login", data={
            "username": "candidate1",
            "password": "123456"
        })

    @task(4)
    def get_job_detail(self):
        self.client.get("/jobs/1")

    @task(2)
    def get_apply_job(self):
        self.client.get("/jobs/1/applications")

    @task(1)
    def get_my_application(self):
        self.client.get("/profile/applications")