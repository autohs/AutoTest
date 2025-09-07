import cv2
import os

def detectBlink(file):
# 동영상 파일 경로
    video_path = file

    # 동영상 파일 열기
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        print("오류: 동영상 파일을 열 수 없습니다.")
        exit()

    # 깜빡임 감지를 위한 임계값 설정
    # 이 값은 영상의 특성에 따라 조절해야 합니다.
    blink_threshold = 50.0

    # 첫 번째 프레임의 평균 밝기 초기화
    ret, prev_frame = cap.read()
    if not ret:
        print("오류: 첫 프레임을 읽을 수 없습니다.")
        exit()
    prev_gray_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    prev_avg_luminosity = prev_gray_frame.mean()

    frame_count = 1
    number =0
    while True:
        ret, current_frame = cap.read()
        if not ret:
            break
        number+=1
        # 현재 프레임을 회색조로 변환
        current_gray_frame = cv2.cvtColor(current_frame, cv2.COLOR_BGR2GRAY)

        # 현재 프레임의 평균 밝기 계산
        current_avg_luminosity = current_gray_frame.mean()

        # 이전 프레임과의 밝기 차이 계산
        luminosity_diff = abs(current_avg_luminosity - prev_avg_luminosity)

        # 밝기 차이가 임계값을 초과하면 깜빡임으로 간주
        if(luminosity_diff>5):
            print("dif:",number,":",luminosity_diff)
        if luminosity_diff > blink_threshold:
            print(f"[경고] 프레임 {frame_count}에서 깜빡임 감지! 밝기 변화: {luminosity_diff:.2f}")

        # 다음 반복을 위해 현재 프레임을 이전 프레임으로 저장
        prev_avg_luminosity = current_avg_luminosity
        frame_count += 1

    cap.release()
    cv2.destroyAllWindows()
    
    
def checkFoloder():
    # 현재 실행 파일의 경로
    file_path = os.path.abspath(__file__)

    # 파일이 위치한 디렉토리 경로
    directory_path = os.path.dirname(file_path)

    print(directory_path)
    return directory_path
# 사용 예제
if __name__ == "__main__":
    video_file = "input.mp4"  # 처리할 동영상 파일명
    output_folder = "output"  # 이미지를 저장할 폴더명
    foler = checkFoloder()
    print("folder:",foler)
    video_file = foler +"\\input_blink.mp4"
#    output_folder =foler +"\output"
    
    detectBlink(video_file)