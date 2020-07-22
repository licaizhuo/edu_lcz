from bz_task.main import app


@app.task(name="upload_file")
def upload_file():
    print("我是第三个任务")

    return "upload_file"
