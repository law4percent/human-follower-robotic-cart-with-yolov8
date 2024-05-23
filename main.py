import cv2
from ultralytics import YOLO
import cvzone
import numpy as np
import pandas as pd
import serial
import time

ShowOnFrame_BoundingBoxAndClsID = False
ShowFrame = True
DEBUG_CMD = True
DEBUG_FRAME = True
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

    VIDEO_SOURCE_PATH = "inference/Videos/Sample_Video.mp4"
    yolov8_weights = "weights/best.pt"
    COCO_FILE_PATH = "utils/coco.names"

    model = YOLO(yolov8_weights, "v8")
    cap = cv2.VideoCapture(VIDEO_SOURCE_PATH)
    
    class_list = Split_Class_List(COCO_FILE_PATH) 

    count = 0
    frame_width = 1280 # 1020
    frame_height = 720 # 500

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    LeftSideArea = [(0, 0), (0, 720), (400, 720), (400, 0)]
    RightSideArea = [(880, 0), (880, 720), (1280, 720), (1280, 0)]
    CenterArea = [(400, 0), (400, 720), (880, 720), (880, 0)]
    CursorLeft = [(450, 200), (400, 200), (400, 520), (450, 520)]
    CursorRight = [(830, 200), (880, 200), (880, 520), (830, 520)]
    Area = [LeftSideArea, CenterArea, RightSideArea]

    # frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    # frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    # Print the frame size
    # print(f"Frame width: {frame_width}")
    # print(f"Frame height: {frame_height}")
    # break
    while True:
        success, frame = cap.read()

        if not success:
            cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
            continue
        
        count += 1
        if count % 3 != 0:
            continue
        
        frame = cv2.resize(frame, (frame_width, frame_height))
        norm_frame_Pred_result = model.predict(source=[frame], conf=0.45, save=False)
        
        PX_Zones = pd.DataFrame(norm_frame_Pred_result[0].boxes.data).astype("float")
        PX_convertToNumpy_NormV = norm_frame_Pred_result[0].numpy()

        LeftSide = []
        RightSide = []
        Center = []
        path_lists = (LeftSide, Center, RightSide)

        """
        if len(PX_convertToNumpy_NormV) != 0 and ShowOnFrame_BoundingBoxAndClsID:
            obstacle_color = (220, 150, 160)
            text_color = (255, 255, 255)

            for i in range(len(norm_frame_Pred_result[0])):
                boxes = norm_frame_Pred_result[0].boxes
                box = boxes[i]  # returns one box
                clsID = box.cls.numpy()[0]
                conf = box.conf.numpy()[0]
                bb = box.xyxy.numpy()[0]
                cls_name = class_list[int(clsID)]

                font = cv2.FONT_HERSHEY_COMPLEX
                if cls_name == "alga":
                    cv2.putText(frame, cls_name + " " + str(round(conf, 3)) + "%", (int(bb[0]), int(bb[1]) - 10), font, fontScale=0.5, color=text_color, thickness=2)
                    cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), cls_color[3], 2)
                elif cls_name == "marie":
                    cv2.putText(frame, cls_name + " " + str(round(conf, 3)) + "%", (int(bb[0]), int(bb[1]) - 10), font, fontScale=0.5, color=text_color, thickness=2)
                    cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), cls_color[2], 2)
                elif cls_name == "marisa":
                    cv2.putText(frame, cls_name + " " + str(round(conf, 3)) + "%", (int(bb[0]), int(bb[1]) - 10), font, fontScale=0.5, color=text_color, thickness=2)
                    cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), cls_color[1], 2)
                elif cls_name == "memet":
                    cv2.putText(frame, cls_name + " " + str(round(conf, 3)) + "%", (int(bb[0]), int(bb[1]) - 10), font, fontScale=0.5, color=text_color, thickness=2)
                    cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), cls_color[0], 2)
                else:
                    cv2.putText(frame, cls_name + " " + str(round(conf, 3)) + "%", (int(bb[0]), int(bb[1]) - 10), font, fontScale=0.5, color=text_color, thickness=2)
                    cv2.rectangle(frame, (int(bb[0]), int(bb[1])), (int(bb[2]), int(bb[3])), obstacle_color, 2)
        """
        obstacle_color = (220, 150, 160)
        text_color = (255, 255, 255)
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
                        cv2.circle(frame, cls_center_pnt, 25, cls_color[1], thickness=3)
                    
                    # sum_of_cls += len(list_to_append)

        SideZoneColor = (0, 255, 0)
        WarningColor = (0, 0, 255)
        TextColor = (255, 255, 255)
        # Nor
        # cv2.polylines(frame, [np.array(LeftSideArea, np.int32)], True, SideZoneColor, 2)
        # cv2.polylines(frame, [np.array(RightSideArea, np.int32)], True, SideZoneColor, 2)
        cv2.polylines(frame, [np.array(CursorLeft, np.int32)], False, SideZoneColor, 3)
        cv2.polylines(frame, [np.array(CursorRight, np.int32)], False, SideZoneColor, 3)

        font = cv2.FONT_HERSHEY_COMPLEX
        # cv2.putText(frame, f"Right Side: {len(RightSide)}", (35, 35), font, fontScale=0.5, color=(0, 255, 0), thickness=2)
        # cv2.putText(frame, f"Center: {len(Center)}", (35, 35+35), font, fontScale=0.5, color=(0, 255, 0), thickness=2)
        # cv2.putText(frame, f"Left Side: {len(LeftSide)}", (35, 35+35+35), font, fontScale=0.5, color=(0, 255, 0), thickness=2)
        if len(RightSide): # Turn Left
            cv2.putText(frame, "Turn Right", (35, 35), font, fontScale=1, color=TextColor, thickness=2)
            cv2.polylines(frame, [np.array(CursorRight, np.int32)], False, WarningColor, 10)
        elif len(LeftSide): # Turn Right
            cv2.putText(frame, "Turn Left", (35, 35), font, fontScale=1, color=TextColor, thickness=2)
            cv2.polylines(frame, [np.array(CursorLeft, np.int32)], False, WarningColor, 10)
        else: # Stable
            cv2.putText(frame, "Move Forward", (35, 35), font, fontScale=1, color=TextColor, thickness=2)

        if ShowFrame:
            cv2.imshow(window_frame_name, frame)

        if cv2.waitKey(1) & 0xFF == 27: # ESC
            break


    cap.release()
    cv2.destroyAllWindows()
    
if __name__ == "__main__":
    main()