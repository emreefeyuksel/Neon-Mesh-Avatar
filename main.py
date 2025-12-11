import cv2
import mediapipe as mp
import numpy as np
import pyvirtualcam
from pyvirtualcam import PixelFormat

#Settings
BLACK_BACKGROUND = True  #True: Black Screen (Avatar), False: With background

#Colors RGB format
COLOR_FACE = (0, 255, 0)  # Yüz: Matrix Yeşili
COLOR_HANDS = (0, 255, 255)  # Eller: Neon Sarı
COLOR_IRIS = (0, 0, 255)  # Göz Bebekleri: Kırmızı

#Mediapipe setup
mp_holistic = mp.solutions.holistic
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles

#start cam
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
width = 640
height = 480
cap.set(3, width)
cap.set(4, height)

#Holistic model (face+hands)
holistic = mp_holistic.Holistic(
    refine_face_landmarks=True,
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)

#Drawing styles
face_spec = mp_drawing.DrawingSpec(thickness=1, circle_radius=1, color=COLOR_FACE)
hand_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=2, color=COLOR_HANDS)
iris_spec = mp_drawing.DrawingSpec(thickness=2, circle_radius=1, color=COLOR_IRIS)

print(f"Cyberpunk Kamera Başlatılıyor... ({width}x{height})")
print("Discord/Zoom'dan 'OBS Virtual Camera'yı seç!")

#Vircam loop
# fmt=PixelFormat.BGR so you can directly send opencv, no need to convert
with pyvirtualcam.Camera(width=width, height=height, fps=30, fmt=PixelFormat.BGR) as cam:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("Kamera hatası.")
            break

        #Mediapipe process
        rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = holistic.process(rgb_frame)

        #Preparing background
        #If avatar mode on turn background to black
        if BLACK_BACKGROUND:
            frame = np.zeros(frame.shape, dtype=np.uint8)

        #--DRAWINGS--
        #Face mesh
        if results.face_landmarks:
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=results.face_landmarks,
                connections=mp_holistic.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=face_spec
            )
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=results.face_landmarks,
                connections=mp_holistic.FACEMESH_CONTOURS,
                landmark_drawing_spec=None,
                connection_drawing_spec=iris_spec
            )

        #Left hand
        if results.left_hand_landmarks:
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=results.left_hand_landmarks,
                connections=mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=hand_spec,
                connection_drawing_spec=hand_spec
            )

        #Right hand
        if results.right_hand_landmarks:
            mp_drawing.draw_landmarks(
                image=frame,
                landmark_list=results.right_hand_landmarks,
                connections=mp_holistic.HAND_CONNECTIONS,
                landmark_drawing_spec=hand_spec,
                connection_drawing_spec=hand_spec
            )

        #Mirroring
        frame = cv2.flip(frame, 1)
        cam.send(frame) #send frame to vircam
        cv2.imshow("Cyberpunk Avatar Preview", frame) #show at screen to check

        #Fps sync
        cam.sleep_until_next_frame()

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()