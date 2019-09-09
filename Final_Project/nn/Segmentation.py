import skimage, numpy, torch, torchvision, ssl, PIL
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw 

ssl._create_default_https_context = ssl._create_unverified_context

def segmentation(ipath):
    image = skimage.io.imread(ipath, plugin='matplotlib')
    image = skimage.transform.resize(image, (400, 400), anti_aliasing=True)
    image = numpy.transpose(image, (2, 0, 1))
    image = image.astype(numpy.float32)
    input = torch.from_numpy(image)

    input = torch.unsqueeze(torchvision.transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])(input), 0)

    fcn_resnet101 = torchvision.models.segmentation.fcn_resnet101(pretrained=True)
    fcn_resnet101.eval()

    IMAGE = fcn_resnet101(input)
    IMAGE = IMAGE['out']
    IMAGE = IMAGE.squeeze(0).argmax(0)

    path = 'output/seg/' + ipath
    plt.imsave(path, IMAGE)
    return path

path = '1.jpg'
segmentation(path)