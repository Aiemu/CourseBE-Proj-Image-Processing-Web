from imagenet1000 import labels
import skimage, numpy, torch, torchvision, ssl, PIL, cv2
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw 

ssl._create_default_https_context = ssl._create_unverified_context

def detection(imagedir):
    
    maskrcnn_resnet50_fpn = torchvision.models.detection.maskrcnn_resnet50_fpn(pretrained=True)
    maskrcnn_resnet50_fpn.eval()

    image = PIL.Image.open(imagedir)
    image_tensor = torchvision.transforms.functional.to_tensor(image)

    output = maskrcnn_resnet50_fpn([image_tensor])

    print(output)
    boxes = output[0]['boxes']
    print(output[0]['labels'].numpy().shape())
    labs = output[0]['labels'].numpy().tolist()
    scores = output[0]['scores']
    # masks = output[0]['masks'].numpy().tolist()

    IMAGE = cv2.imread(imagedir)
    for i in range(0, len(labs)):
        print(boxes.data[i].numpy().tolist()[0], boxes.data[i].numpy().tolist()[1])
        cv2.rectangle(IMAGE, (int(boxes.data[i].numpy().tolist()[0]), int(boxes.data[i].numpy().tolist()[1])),
                    (int(boxes.data[i].numpy().tolist()[2]), int(boxes.data[i].numpy().tolist()[3])),
                    (0, 255, 0), 2)

        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(IMAGE, str(labels[labs[i]]) + ' ' + str(scores.data[i].numpy()), 
                    (int(boxes.data[i].numpy().tolist()[0]), int(boxes.data[i].numpy().tolist()[1])), 
                    font, 3, (255,255,255), 2, cv2.LINE_AA)
                    
    path = 'output/'+imagedir
    cv2.imwrite(path, IMAGE)
    return path
