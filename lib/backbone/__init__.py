from .resnet import res18, res50, res101
from .resnet_cifar import res32_cifar
from .oltr_resnet import res10
from .resnext import resnext50
from .resnet_cifar2 import *
from .efficientnet import efinet
from .AFA import afa
__all__ = [
    'res18', 'res50', 'res32_cifar', 'res10', 'resnext50', 'res101', 'resnet110', 'efinet', 'afa'
]