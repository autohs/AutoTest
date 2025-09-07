import cv2
import numpy as np
import os

def detect_screen_glitch(prev_frame, current_frame, threshold=25, min_change_percent=0.1):
    """
    연속된 두 프레임의 픽셀 변화율을 감지하여 화면 깨짐을 판단합니다.

    Args:
        prev_frame (np.array): 이전 프레임 이미지 (흑백).
        current_frame (np.array): 현재 프레임 이미지 (흑백).
        threshold (int): 두 프레임의 픽셀값 차이를 판단하는 임계값 (0-255).
        min_change_percent (float): 전체 화면 픽셀 대비 변화율 최소 기준 (%).

    Returns:
        bool: 화면 깨짐 감지 시 True, 아니면 False.
    """
    if prev_frame is None:
        return False

    # 1. 두 프레임의 차분 이미지 계산
    # cv2.absdiff는 두 이미지의 픽셀별 절대값 차이를 계산합니다.
    diff_image = cv2.absdiff(prev_frame, current_frame)
    
    # 2. 임계값 처리: 변화가 큰 픽셀만 남김
    # _는 반환 값 중 하나를 무시할 때 사용합니다.
    _, thresh_diff = cv2.threshold(diff_image, threshold, 255, cv2.THRESH_BINARY)

    # 3. 변화된 픽셀의 개수 계산
    # np.count_nonzero는 0이 아닌 픽셀의 개수를 셉니다.
    changed_pixels = np.count_nonzero(thresh_diff)
    
    # 4. 전체 픽셀 수 대비 변화율 계산
    total_pixels = thresh_diff.size
    change_rate = (changed_pixels / total_pixels) * 100

    result = None
    # 5. 변화율을 기준으로 화면 깨짐 여부 판단
    if change_rate > min_change_percent:
        #print(f"화면 깨짐 감지! 픽셀 변화율: {change_rate:.2f}%")
        result = f"화면 깨짐 감지! 픽셀 변화율: {change_rate:.2f}%"
        return result
    
    return result

def checkSignal(videoFile):

    # 비디오 캡처 객체 생성 (0은 기본 웹캠)
#    cap = cv2.VideoCapture(0)
    cap = cv2.VideoCapture(videoFile)

    # 첫 번째 프레임 초기화
    ret, prev_frame = cap.read()
    if ret:
        prev_frame = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY) # 흑백 변환

    count =0
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # 현재 프레임을 흑백으로 변환
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # 화면 깨짐 감지 함수 호출
        glitch_detected = detect_screen_glitch(prev_frame, gray_frame)
        if(glitch_detected !=None):
            print("count :",count,"-",glitch_detected)

        # 이전 프레임 업데이트
        prev_frame = gray_frame.copy()

        # 화면에 현재 프레임 표시
        cv2.imshow("Original Frame", frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        count +=1

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
    video_file = foler +"\input.mp4"
    output_folder =foler +"\output"
    checkSignal(video_file)    