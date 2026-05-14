from locust import HttpUser, task, between
import io
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

    @task(1)
    def post_apply_job(self):
        try:
            with open(r"D:\KiemThuTH\QuanLyTuyenDungProject\QuanLyTuyenDungProject\rapp\locust\MB0_2.pdf", "rb") as f:
                files = {
                    'cv_file': ("MB0_2.pdf", f, "application/pdf")
                }
                with self.client.post("/jobs/1/applications", files=files, catch_response=True) as response:
                    if response.status_code == 200 or response.status_code == 302:
                        response.success()
                    else:
                        response.failure(f"Lỗi nộp hồ sơ: {response.status_code}")
        except FileNotFoundError:
            print("Lỗi: Không tìm thấy file MB0_2.pdf trong thư mục!")