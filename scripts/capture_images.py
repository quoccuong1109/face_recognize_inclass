import cv2
import os

def capture_images_from_camera(output_dir, num_images=100):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    cap = cv2.VideoCapture(0)
    count = 0

    while count < num_images:
        ret, frame = cap.read()
        if not ret:
            break

        cv2.imshow('Capture', frame)
        cv2.imwrite(os.path.join(output_dir, f'image_{count}.jpg'), frame)
        count += 1

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    capture_images_from_camera('data\\raw_images')