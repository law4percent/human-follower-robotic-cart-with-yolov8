import cv2
from ultralytics import YOLO
import cvzone
import numpy as np
import pandas as pd
import serial
import time
from picamera2 import Picamera2


ShowOnFrame_BoundingBoxAndClsID = False
ShowFrame = True
DEBUG_CMD = True
DEBUG_FRAME = False
MouseCallBack = False

cls_color = [(0, 187, 255), (188, 214, 152), (250, 0, 106), (255, 161, 150)] #255, 187, 0

def videoFrame(event, x, y, flags, param):
    if event == cv2.EVENT_MOUSEMOVE:
        point = [x, y]
        print(point)

def Split_Class_List(file_path):
    myFile = open(file_path, "r")
    data = myFile.read()
    class_list = data.split("\n")
    myFile.close()
    
    return class_list

def boundingBox_ClsID_display(Frame, Rec_pos, Color, Text, Text_pos):
    cvzone.cornerRect(Frame, Rec_pos, l=0, t=2, rt=2, colorR=Color, colorC=Color)
    cvzone.putTextRect(Frame, Text, Text_pos, 1, 1, colorR=Color)
    
def PolygonTest(Area, XY):
    return cv2.pointPolygonTest(np.array(Area, np.int32), XY, False)

def main():
    window_frame_name = "FRAME"
    
    if MouseCallBack:
        cv2.namedWindow(window_frame_name)
        cv2.setMouseCallback(window_frame_name, videoFrame)

    yolov8_weights = "weights/weights_yolov8n.pt"
    COCO_FILE_PATH = "utils/coco.names"

    model = YOLO(yolov8_weights, "v8")
    picam2 = Picamera2()
    picam2.preview_configuration.main.size = (640,480)
    picam2.preview_configuration.main.format = "RGB888"
    picam2.preview_configuration.align()
    picam2.configure("preview")
    picam2.start()
    
    class_list = Split_Class_List(COCO_FILE_PATH) 

    count = 0
    frame_width = 1280 # 1020
    frame_height = 720 # 500

    '''
    if not cap.isOpened():
        print("Cannot open camera")
        exit()
    '''
    
    LeftSideArea = [(0, 0), (0, 720), (400, 720), (400, 0)]
    RightSideArea = [(880, 0), (880, 720), (1280, 720), (1280, 0)]
    CenterArea = [(400, 0), (400, 720), (880, 720), (880, 0)]
    
    CursorLeft = [(450, 200), (400, 200), (400, 520), (450, 520)]
    CursorRight = [(830, 200), (880, 200), (880, 520), (830, 520)]
    Area = [LeftSideArea, CenterArea, RightSideArea]

    while True:
        frame = picam2.capture_array()
        
        count += 1
        if count % 50 != 0:
            continue
        
        frame = cv2.resize(frame, (frame_width, frame_height))
        frame = cv2.flip(frame,1)
        norm_frame_Pred_result = model.predict(source=[frame], conf=0.45, save=False)
        
        PX_Zones = pd.DataFrame(norm_frame_Pred_result[0].boxes.data).astype("float")
        PX_convertToNumpy_NormV = norm_frame_Pred_result[0].numpy()

        LeftSide = []
        RightSide = []
        Center = []
        path_lists = (LeftSide, Center, RightSide)

        for index_, row in PX_Zones.iterrows():
            x1 = int(row[0])
            y1 = int(row[1])
            x2 = int(row[2])
            y2 = int(row[3])

            confidence = round(row[4], 5)
            detected_class_index = int(row[5])
            class_ID_name = class_list[detected_class_index]

            cls_center_x = int(x1 + x2) // 2
            cls_center_y = int(y1 + y2) // 2
            cls_center_pnt = (cls_center_x, cls_center_y)
            w, h = x2 - x1, y2 - y1

            rec_pos = (x1, y1, w, h)
            text_pos = (x1, y1)
            clsID_and_Conf = f"{class_ID_name} {confidence}%"

            for area_indx in range(len(Area)):
                if PolygonTest(Area=Area[area_indx], XY=cls_center_pnt) >= 0:
                    if class_ID_name == "marisa":
                        list_to_append = path_lists[area_indx]
                        list_to_append.append(cls_center_x)
                        if ShowOnFrame_BoundingBoxAndClsID:
                            boundingBox_ClsID_display(Frame=frame, Rec_pos=rec_pos, Color=cls_color[1], Text=clsID_and_Conf, Text_pos=text_pos)
                        cv2.circle(frame, cls_center_pnt, 25, cls_color[1], thickness=10)
                    
        SideZoneColor = (0, 255, 0)
        WarningColor = (0, 0, 255)
        TextColor = (255, 255, 255)
        
        if DEBUG_FRAME:
            sum_of_cls = len(LeftSide) + len(RightSide) + len(Center)
            if DEBUG_CMD:
                print(f"Total class: {sum_of_cls}")
            # cv2.polylines(frame, [np.array(RightSideArea, np.int32)], True, SideZoneColor, 2)
            # cv2.polylines(frame, [np.array(LeftSideArea, np.int32)], True, SideZoneColor, 2)
            cv2.polylines(frame, [np.array(CursorLeft, np.int32)], False, SideZoneColor, 3)
            cv2.polylines(frame, [np.array(CursorRight, np.int32)], False, SideZoneColor, 3)

        font = cv2.FONT_HERSHEY_COMPLEX
        if len(RightSide):
            if DEBUG_CMD:
                print("Turn Left")

            if DEBUG_FRAME:
                cv2.putText(frame, "Turn Left", (35, 35), font, fontScale=1, color=TextColor, thickness=2)
                cv2.polylines(frame, [np.array(CursorRight, np.int32)], False, WarningColor, 10)
        
        elif len(LeftSide):
            if DEBUG_CMD:
                print("Turn Right")

            if DEBUG_FRAME:
                cv2.putText(frame, "Turn Right", (35, 35), font, fontScale=1, color=TextColor, thickness=2)
                cv2.polylines(frame, [np.array(CursorLeft, np.int32)], False, WarningColor, 10)
        
        elif len(Center):
            if DEBUG_CMD:
                print("Move Forward")

            if DEBUG_FRAME:
                cv2.putText(frame, "Move Forward", (35, 35), font, fontScale=1, color=TextColor, thickness=2)
        
        else:
            if DEBUG_CMD:
                print("Stop")

            if DEBUG_FRAME:
                cv2.putText(frame, "Stop", (35, 35), font, fontScale=1, color=TextColor, thickness=2)

        if ShowFrame:
            cv2.imshow(window_frame_name, frame)

        if cv2.waitKey(1) & 0xFF == 27: # ESC
            break


    #cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()
