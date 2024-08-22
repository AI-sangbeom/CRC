import timm
import torch.nn as nn

def efinet(cfg,
    pretrain=True,
    pretrained_model="",
    last_layer_stride=2,):
    model = timm.create_model("hf_hub:timm/efficientnetv2_rw_m.agc_in1k", pretrained=False, features_only=True)
    feature_extractor = nn.Sequential()
    
    for name, param in model.named_children():    
        if name=='global_pool':
            break
        feature_extractor.append(param)    

    return feature_extractor