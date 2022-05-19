from dataclasses import dataclass
import numpy as np
import ffmpeg
import cv2
# import time
from datetime import datetime, timedelta

# width=768
# height=432
# framerate=12.5

width=1280
height=720
framerate=30
fontsize = min(int(np.sqrt(width/2)), int(height/20))

pix_fmt='bgr24' # bgr24 opencv, or rgb24 cv2.cvtColor(image, cv2.COLOR_RGB2BGR)

process1 = (
    ffmpeg
    #.input("video=HD USB Camera", f='dshow', video_pin_name='0', rtbufsize='15M', framerate=framerate, video_size=(width, height), vcodec='mjpeg') # pixel_format='yuyv422')#, show_video_device_dialog='true')
    .input("video=HD Pro Webcam C920", f='dshow', video_pin_name='0', rtbufsize='15M', framerate=framerate, video_size=(width, height), vcodec='mjpeg') # pixel_format='yuyv422')#, show_video_device_dialog='true')
    # .input('FaceTime HD Camera (Built-in)', f='avfoundation', framerate=framerate, video_size=(width, height), pix_fmt='nv12')
    #.input('car-detection.mp4')
    .drawtext(fontfile='arial.ttf', fontsize=fontsize, fontcolor='white', box=1, boxcolor='black@0.9', x=1, y=1, text='''%{localtime} %{pts:hms}''', escape_text=False)
    .output('pipe:', format='rawvideo', pix_fmt=pix_fmt)
    .run_async(pipe_stdout=True)
)

process2 = (
    ffmpeg
    .input('pipe:', format='rawvideo', pix_fmt=pix_fmt, s='{}x{}'.format(width, height), framerate=framerate)
    .output('out.mp4', vcodec='h264_qsv')
    .overwrite_output()
    .run_async(pipe_stdin=True)
)

start_time = datetime.now()

while True:
    now_time = datetime.now()
    if now_time - start_time > timedelta(seconds=100):
        break
    frame_time = datetime.now()
    # print(f'A: {datetime.now()}')
    in_bytes = process1.stdout.read(width * height * 3)

    if not in_bytes:
        print('not in_bytes')
        break
    image = (
        np
        .frombuffer(in_bytes, np.uint8)
        .reshape([height, width, 3])
    )
    frame_process_time = datetime.now() - frame_time
    print(f'FPS: {1/frame_process_time.total_seconds()}, {frame_process_time.total_seconds()*1000}')
    #image_array = np.asarray(bytearray(frame), dtype="uint8")
    #image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    # print(f'B: {datetime.now()}')
    cv2.imshow('frame', image)
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    # time.sleep(1/framerate) # have to wait if read from a video file

    # process2.stdin.write(
    #     image
    #     .astype(np.uint8)
    #     .tobytes()
    # )
    process2.stdin.write(in_bytes)

process2.stdin.close()
process2.wait()

process1.kill()
process1.wait()

