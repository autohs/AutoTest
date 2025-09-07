import cv2
import os

def detect_screen_anomaly(frame):
    # 프레임의 평균 밝기 계산
    avg_brightness = cv2.mean(frame)[0]
    if avg_brightness < 10:  # 임계값 10 이하 (어두운 화면)
        return "화면 출력 안됨 (Black Screen)"

    # 프레임의 표준 편차 계산 (노이즈 감지)
    mean, std_dev = cv2.meanStdDev(frame)
    if std_dev[0][0] > 100 : #50 : # 표준 편차 임계값
        result = " 화면 노이즈 ( Noise)" + str(std_dev[0][0])
        return result
        
    return "정상"

def assessment(video_path):
    # 예시: 웹캠(0)으로부터 영상 스트리밍
#    cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(video_path) # 동영상 파일 열기
    count =0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        status = detect_screen_anomaly(frame)
        if status != "정상":
            print(f"이상 감지: {count},{status}")
            # 여기에 알림 로직 추가 (e.g., notice.show())

        cv2.imshow('Screen Analysis', frame)
        count +=1
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


def checkFoloder():
    # 현재 실행 파일의 경로
    file_path = os.path.abspath(__file__)

    # 파일이 위치한 디렉토리 경로
    directory_path = os.path.dirname(file_path)

    print("checkFoloder:",directory_path)
    return directory_path    


# 사용 예제
if __name__ == "__main__":
    video_file = "input.mp4"  # 처리할 동영상 파일명
    output_folder = "output"  # 이미지를 저장할 폴더명
    folder = checkFoloder()
    video_file = folder +"\\input.mp4"
#    output_folder =folder +"\output"
    print("target file:",video_file)
    assessment(video_file)