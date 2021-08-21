from project1.config_project1 import *
#from tensorflow.compat.v1.keras.models import load_model_weights
#print(tf.__version__)
def Model():
    model = tf.keras.models.Sequential([
    tf.keras.layers.Conv2D(64, (3,3), activation='relu', padding= 'same', input_shape= (38,38,3)),
    tf.keras.layers.Conv2D(64, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.MaxPool2D(pool_size=(2,2), strides=(2,2)),
    
    tf.keras.layers.Conv2D(128, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.Conv2D(128, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.MaxPool2D(pool_size=(2,2)),

    tf.keras.layers.Conv2D(256, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.Conv2D(256, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.Conv2D(256, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.MaxPool2D(pool_size=(2,2), strides=(2,2)),

    tf.keras.layers.Conv2D(512, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.Conv2D(512, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.Conv2D(512, (3,3), activation='relu', padding= 'same'),
    tf.keras.layers.MaxPool2D(pool_size=(2,2), strides=(2,2)),

    tf.keras.layers.Flatten(),
    tf.keras.layers.Dense(512, activation= 'relu'),
    tf.keras.layers.Dense(512, activation= 'relu'),
    tf.keras.layers.Dense(31, activation= 'softmax')])
    model.load_weights(WEIGHTS)
    #model.summary()
    return model

class yolotiny(object):
    def __init__(self, image):
        self.image= image
        self.model = Model()
    
    def process_plate(self, image):
        """ ap = argparse.ArgumentParser()
        #ap.add_argument('-i', '--image', required=True,
        #                help='path to input image')
        ap.add_argument('-c', '--config', default=YOLO_CONFIG, help='path to yolo config file')
        ap.add_argument('-w', '--weights', default=YOLO_WEIGHT, help='path to yolo pre-trained weights')
        ap.add_argument('-cl', '--classes', default=YOLO_CLASSES, help='path to text file containing class names')
        args = ap.parse_args() """


        def get_output_layers(net):
            layer_names = net.getLayerNames()

            output_layers = [layer_names[i[0] - 1] for i in net.getUnconnectedOutLayers()]

            return output_layers


        def draw_prediction(img, class_id, confidence, x, y, x_plus_w, y_plus_h):
            label = str(classes[class_id])

            color = COLORS[class_id]

            cv2.rectangle(img, (x, y), (x_plus_w, y_plus_h), color, 2)

            cv2.putText(img, label, (x - 10, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

        Width = image.shape[1]
        Height = image.shape[0]
        scale = 0.00392

        classes = None

        #with open(args.classes, 'r') as f:
        with open(YOLO_CLASSES, 'r') as f:
            classes = [line.strip() for line in f.readlines()]

        COLORS = np.random.uniform(0, 255, size=(len(classes), 3))

        #net = cv2.dnn.readNet(args.weights, args.config)    
        net = cv2.dnn.readNet(YOLO_WEIGHT, YOLO_CONFIG)

        blob = cv2.dnn.blobFromImage(image, scale, (416, 416), (0, 0, 0), True, crop=False)

        net.setInput(blob)

        outs = net.forward(get_output_layers(net))

        class_ids = []
        confidences = []
        boxes = []
        conf_threshold = 0.5
        nms_threshold = 0.4
        x=0
        y=0
        w=0
        h=0
        # Thực hiện xác định bằng HOG và SVM
        start = time.time()
        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5:
                    center_x = int(detection[0] * Width)
                    center_y = int(detection[1] * Height)
                    w = int(detection[2] * Width)
                    h = int(detection[3] * Height)
                    x = center_x - w / 2
                    y = center_y - h / 2
                    class_ids.append(class_id)
                    confidences.append(float(confidence))
                    boxes.append([x, y, w, h])
        indices = cv2.dnn.NMSBoxes(boxes, confidences, conf_threshold, nms_threshold)
        for i in indices:
            i = i[0]
            box = boxes[i]
            x = box[0]
            y = box[1]
            w = box[2]
            h = box[3]
            #draw_prediction(image, class_ids[i], confidences[i], round(x), round(y), round(x + w), round(y + h))
        #print(x,y,w,h)
        top= y
        left= x
        bottom= y+h
        right= x+ w

        #cv2.imshow("object detection", image)
        end = time.time()
        print("YOLO Execution time: " + str(end-start))
        return top, left, bottom, right

    def sort_contours(self, contours):
        reverse = False
        i = 0
        boundingBoxes = [cv2.boundingRect(contour) for contour in contours]
        (contours, boundingBoxes) = zip(*sorted(zip(contours, boundingBoxes),
            key=lambda b:b[1][i], reverse=reverse))
        return contours, boundingBoxes

    def cut_plate(self):
        top, left, bottom, right= self.process_plate(self.image)
        if top==0 and left==0 and bottom==0 and right==0:
            licenses= "Khong tim thay box"
            print("Khong tim thay box")
            return licenses, self.image
        pts1= np.float32([[left, top], [right,top], [left, bottom], [right, bottom]])
        pts2= np.float32([[0, 0], [600,0], [0, 300], [600, 300]])
        img_bird= cv2.getPerspectiveTransform(pts1, pts2)
        result_bird= cv2.warpPerspective(self.image, img_bird, (600, 300))
        #cv2.imshow("cat", result_bird)

        image_split= cv2.cvtColor(result_bird, cv2.COLOR_BGR2GRAY)
        ret, thresh2= cv2.threshold(image_split, 100, 255, cv2.THRESH_BINARY)
        cv2.floodFill(thresh2, None, (0,0), 255)
        thresh_blur = cv2.medianBlur(thresh2, 5)
        thresh2_2 = cv2.bitwise_not(thresh_blur)
        contours, hierarchy = cv2.findContours(thresh2_2, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        countContours = 0
        boxes=[]

        contours_sort, boundingBoxes = self.sort_contours(contours)
        h_list=[]
        for contour in contours_sort:
            x, y, w, h = contourRect = cv2.boundingRect(contour)
            ratio= h/w
            if 2<=ratio<=8:
                if 1.6< thresh2_2.shape[0]/h< 3 and h>100 :
                    h_list.append(h)
        h_avg= sum(h_list)/len(h_list)
        """print(max(h_list))
        print(h_avg)"""

        for contour in contours_sort:
            x, y, w, h = contourRect = cv2.boundingRect(contour)
            """print("\nchua loc")
            print("Trong so x, y, w, h")
            print(x, y, w, h)"""
            ratio= h/w
            if 2<=ratio<=8:
                if 1.6< thresh2_2.shape[0]/h< 3 and 0.9<=h/h_avg<=1.1 :
                    """ print("\nDa loc")
                    print("Trong so x, y, w, h, thresh_shape[0]")
                    print(x, y, w, h, thresh2_2.shape[0]) """
                    countContours += 1
                    #cv2.rectangle(result_bird, (x, y), (x + w, y + h), (0, 255, 0))
                    box_img= thresh2_2[y:y+h,x:x+w]
                    boxes.append(box_img)
        print("So contour tim dc: ", countContours)
        if len(boxes)==0:
            licenses= "Khong tim thay"
            return licenses, thresh2_2
        else:
            num=[]
            licenses=[]
            label_data= LABEL_DATA
            for i in range(countContours):
                #print(str(boxes[i].shape))
                #cv2.imwrite("boxes"+str(i)+".jpg", boxes[i])
                #plt.subplot(1, countContours, i+1), plt.imshow(boxes[i], 'gray') 
                box_img= cv2.resize(boxes[i], (38,38))

                box_img_3=np.stack((box_img,)*3, -1)
                test= box_img_3.reshape(1,38,38,3)
                predict= self.model.predict(test)
                value= np.argmax(predict)
                #if value <31:
                num.append(label_data[value])
                licenses = " ".join(num)
            print(licenses)
            return licenses, thresh2_2

"""path="1070.jpg"
image = cv2.imread(path)

test= yolotiny(image)
test.cut_plate()

cv2.waitKey(0)
#cv2.imwrite("object-detection.jpg", image)
cv2.destroyAllWindows()"""

if __name__== '__main__':
    main()