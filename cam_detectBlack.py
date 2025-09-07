import cv2
import os
def detect_black_screen(video_path, threshold=10, duration_frames=10):
    
    cap = cv2.VideoCapture(video_path) # 동영상 파일 열기
    black_frames_count = 0
    is_event_triggered = False
    count=0

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        
        # 흑백 이미지로 변환
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 평균 밝기 계산
        mean_brightness = gray_frame.mean()

        # 블랙화면 감지: 평균 밝기가 임계값 이하이고, 일정 프레임 이상 지속될 때
        if(mean_brightness<60):
            print("checkdata: ",count,":",mean_brightness, threshold)
        count+=1            
        if mean_brightness < threshold:
            black_frames_count += 1
            if black_frames_count >= duration_frames:
                print(f"이벤트 발생: 블랙화면 감지됨 (프레임 {cap.get(cv2.CAP_PROP_POS_FRAMES)})")
                is_event_triggered = True
                # 여기서 이벤트 발생 시 추가 동작을 수행할 수 있습니다.
                # 예: 이벤트 기록, 특정 구간 녹화, 알림 전송 등
                break # 이벤트가 감지되면 루프 종료
        else:
            black_frames_count = 0 # 블랙화면 카운트 초기화

    cap.release()
    return is_event_triggered

# 사용 예시
# video_file = "your_video.mp4" # 분석할 동영상 파일 경로
# if detect_black_screen(video_file):
#     print("이벤트 발생 구간이 처리되었습니다.")
# else:
#     print("이벤트 발생 구간이 감지되지 않았습니다.")

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
    detect_black_screen(video_file,60,1)