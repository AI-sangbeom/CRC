import timm
import torch.nn as nn
import torch


def afa(cfg,
    pretrain=True,
    pretrained_model="",
    last_layer_stride=2,):
    path = 'afa_model_nancho.pth'
    params = torch.load('afa_parameters_nancho.pth')
    model = torch.load(path)
    model.load_state_dict(params['model'])
    feature_extractor = nn.Sequential()
    for name, param in model.named_children():    
        
        if name=='avgpool':
            break
        feature_extractor.append(param)  

    return feature_extractor