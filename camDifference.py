import cv2
import os


def camDifference(testfile):
    # 동영상 파일 로드
    cap = cv2.VideoCapture(testfile)

    # 첫 번째 프레임을 읽어서 회색조로 변환
    ret, first_frame = cap.read()
    first_gray = cv2.cvtColor(first_frame, cv2.COLOR_BGR2GRAY)
    first_gray = cv2.GaussianBlur(first_gray, (21, 21), 0)

    while True:
        # 다음 프레임을 읽어옴
        ret, frame = cap.read()
        if not ret:
            break

        # 현재 프레임을 회색조로 변환하고 블러 처리
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)

        # 첫 프레임과 현재 프레임의 차이를 계산
        frame_delta = cv2.absdiff(first_gray, gray)

        # 차이 이미지를 이진화하여 임계값 적용
        thresh = cv2.threshold(frame_delta, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)

        # 변화가 있는 영역(윤곽선) 찾기
        contours, _ = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # 변화가 감지된 영역에 사각형 그리기
        for contour in contours:
            if cv2.contourArea(contour) > 500:  # 일정 크기 이상의 변화만 감지
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

        cv2.imshow('Frame Difference', frame)

        if cv2.waitKey(30) & 0xFF == ord('q'):
            break

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
    camDifference(video_file)