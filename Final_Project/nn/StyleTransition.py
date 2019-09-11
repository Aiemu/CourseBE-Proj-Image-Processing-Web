import numpy as np
import torch
import torch.nn as nn
from torch.autograd import Variable
import torch.optim as optim
import PIL
from PIL import Image
import matplotlib.pyplot as plt
import torchvision.transforms as transforms
import torchvision.models as models

use_cuda = torch.cuda.is_available()
dtype = torch.cuda.FloatTensor if use_cuda else torch.FloatTensor

imsize = 200

loader = transforms.Compose([transforms.Resize(imsize), transforms.ToTensor()])

unloader = transforms.ToPILImage()

def image_loader(image_name):
    image = Image.open(image_name)
    image = Variable(loader(image))
    image = image.unsqueeze(0)
    return image

def toimage(tensor):
    image = tensor.clone().cpu()
    image = image.view(3, imsize, imsize)
    image = unloader(image)
    return image

# content loss

class ContentLoss(nn.Module):
    def __init__(self, target, weight):
        super(ContentLoss, self).__init__()
        self.target = target.detach() * weight
        self.weight = weight
        self.criterion = nn.MSELoss()

    def forward(self, input):
        self.loss = self.criterion.forward(input * self.weight, self.target)
        self.output = input
        return self.output

    def backward(self, retain_graph=True):
        self.loss.backward(retain_graph=retain_graph)
        return self.loss

# style loss


class GramMatrix(nn.Module):
    def forward(self, input):
        a, b, c, d = input.size()

        features = input.view(a * b, c * d)

        G = torch.mm(features, features.t())
        return G.div(a * b * c * d)


class StyleLoss(nn.Module):
    def __init__(self, target, weight):
        super(StyleLoss, self).__init__()
        self.target = target.detach() * weight
        self.weight = weight
        self.gram = GramMatrix()
        self.criterion = nn.MSELoss()

    def forward(self, input):
        self.output = input.clone()
        self.G = self.gram.forward(input)
        self.G.mul_(self.weight)
        self.loss = self.criterion.forward(self.G, self.target)
        return self.output

    def backward(self, retain_graph=True):
        self.loss.backward(retain_graph=retain_graph)
        return self.loss

def styletransition(ipath_c):
    ipath_c = "media/" + ipath_c
    ipath_s = "nn/images/style.jpg"
    style = image_loader(ipath_s).type(dtype)
    content = image_loader(ipath_c).type(dtype)

    assert style.size() == content.size(),"we need to import style and content images of the same size"

    cnn = models.vgg19(pretrained=True).features

    if use_cuda:
        cnn = cnn.cuda()

    content_layers = ['conv_4']
    style_layers = ['conv_1', 'conv_2', 'conv_3', 'conv_4', 'conv_5']

    content_losses = []
    style_losses = []

    model = nn.Sequential()
    gram = GramMatrix()

    if use_cuda:
        model = model.cuda()
        gram = gram.cuda()

    content_weight = 1
    style_weight = 1000

    i = 1
    for layer in list(cnn):
        if isinstance(layer, nn.Conv2d):
            name = "conv_" + str(i)
            model.add_module(name, layer)

            if name in content_layers:
                target = model.forward(content).clone()
                content_loss = ContentLoss(target, content_weight)
                model.add_module("content_loss_" + str(i), content_loss)
                content_losses.append(content_loss)

            if name in style_layers:
                target_feature = model.forward(style).clone()
                target_feature_gram = gram.forward(target_feature)
                style_loss = StyleLoss(target_feature_gram, style_weight)
                model.add_module("style_loss_" + str(i), style_loss)
                style_losses.append(style_loss)

        if isinstance(layer, nn.ReLU):
            name = "relu_" + str(i)
            model.add_module(name, layer)

            if name in content_layers:
                target = model.forward(content).clone()
                content_loss = ContentLoss(target, content_weight)
                model.add_module("content_loss_" + str(i), content_loss)
                content_losses.append(content_loss)

            if name in style_layers:
                target_feature = model.forward(style).clone()
                target_feature_gram = gram.forward(target_feature)
                style_loss = StyleLoss(target_feature_gram, style_weight)
                model.add_module("style_loss_" + str(i), style_loss)
                style_losses.append(style_loss)

            i += 1

        if isinstance(layer, nn.MaxPool2d):
            name = "pool_" + str(i)
            model.add_module(name, layer)

    print(model)

    input = image_loader(ipath_c).type(dtype)
    input.data = torch.randn(input.data.size()).type(dtype)
    input_image = toimage(input.data)
    input = nn.Parameter(input.data)
    optimizer = optim.LBFGS([input])

    run = [0]
    while run[0] <= 300:
        def closure():
            input.data.clamp_(0, 1)

            optimizer.zero_grad()
            model.forward(input)
            style_score = 0
            content_score = 0

            for sl in style_losses:
                style_score += sl.backward()
            for cl in content_losses:
                content_score += cl.backward()

            run[0]+=1
            if run[0] % 10 == 0:
                print("run " + str(run) + ":")
                print(style_score.item())
                print(content_score.item())

            return content_score+style_score
        optimizer.step(closure)

    input.data.clamp_(0, 1)

    output_image = input.data.clone().cpu() 
    output_image = output_image.view(3, imsize, imsize)
    output_image = unloader(output_image)

    content_image = content.data.clone().cpu()
    content_image = content_image.view(3, imsize, imsize)
    content_image = unloader(content_image)

    style_image = content.data.clone().cpu()
    style_image = style_image.view(3, imsize, imsize)
    style_image = unloader(style_image)

    ipath_c_list = ipath_c.split('/')
    iname_list = ipath_c_list[-1].split('.')
    iname = iname_list[0]
    outpath = 'media/sty/' + iname + '.PNG'
    output_image.save(outpath)
    ret = 'sty/' + iname + '.PNG'
    return ret

# print(styletransition(input('c:'), input('s:')))