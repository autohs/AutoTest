import cv2
import os

def extract_frames(video_path, output_dir):
    """
    동영상 파일에서 프레임을 추출하여 이미지로 저장합니다.

    Args:
        video_path (str): 입력 동영상 파일의 경로
        output_dir (str): 추출된 이미지를 저장할 디렉터리
    """
    # 동영상 파일 열기
    vidcap = cv2.VideoCapture(video_path)
    if not vidcap.isOpened():
        print(f"Error: Could not open video file {video_path}")
        return

    # 출력 디렉터리가 없으면 생성
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        print(f"Created directory: {output_dir}")

    success, image = vidcap.read()
    count = 0

    while success:
        # 프레임 이미지를 JPEG 파일로 저장
        frame_filename = os.path.join(output_dir, f"frame_{count}.jpg")
        cv2.imwrite(frame_filename, image)
        
        # 다음 프레임 읽기
        success, image = vidcap.read()
        count += 1

    vidcap.release()
    print(f"Successfully extracted {count} frames to {output_dir}")

def checkFoloder():
    # 현재 실행 파일의 경로
    file_path = os.path.abspath(__file__)

    # 파일이 위치한 디렉토리 경로
    directory_path = os.path.dirname(file_path)

    print(directory_path)
    return directory_path
# 사용 예제
if __name__ == "__main__":
    video_file = "input_blink.mp4"  # 처리할 동영상 파일명
    output_folder = "output"  # 이미지를 저장할 폴더명
    foler = checkFoloder()
    video_file = foler +"\input_blink.mp4"
    output_folder =foler +"\output"
    extract_frames(video_file, output_folder)