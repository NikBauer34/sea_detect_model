from ultralytics import YOLO
import cv2
import cvzone
model = YOLO('epoch99 (2).pt')
classNames = ["clean", "mazut"]
def get_bird(image_path: str):
    result: list = model(image_path)[0]
    print(result)
    xyxy: list = result.boxes.xyxy.tolist()
    clss: list = result.boxes.cls.tolist()
    print(clss)

    print(xyxy)
    if len(xyxy) == 0:
        print('no')
        return [False, 'no mazut detected']

    else:
        let_go = False
        f_ind = -1
        for ind, elem in enumerate(clss):
            if elem == 1:
              let_go = True
              break
        if let_go:
            img = cv2.imread(image_path)
            for ind, box in enumerate(xyxy):
            # Bounding Box
                x1, y1, x2, y2 = box
                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
                w, h = x2 - x1, y2 - y1
                # Class Name
                cls = int(clss[ind])
                cvzone.cornerRect(img, (x1 - 10, y1 - 10, w+25, h+25), rt=3, colorC = (0, 0, 255) if cls == 1 else (0, 255, 0))
            # Confidence
            
                # cvzone.putTextRect(img, f'{classNames[cls]}', (max(0, x1-10), max(35, y1-10)), scale=1, thickness=1, colorB = (0, 0, 255) if cls == 1 else (0, 255, 0), colorR = (0, 0, 255) if cls == 1 else (0, 255, 0), border=2)

            cv2.imwrite(image_path, img)

            return [True, f'mazut detected']
        else:
            return [False, f'only clean detected']