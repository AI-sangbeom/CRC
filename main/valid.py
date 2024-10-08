import _init_paths
from net import Network
from config import cfg, update_config
from dataset import *
import numpy as np
import torch
import os
from torch.utils.data import DataLoader
from tqdm import tqdm
import argparse
from core.evaluate import FusionMatrix
from sklearn.metrics import confusion_matrix, f1_score
import matplotlib.pyplot as plt
import pickle
import natsort
def parse_args():
    parser = argparse.ArgumentParser(description="tricks evaluation")

    parser.add_argument(
        "--cfg",
        help="decide which cfg to use",
        required=True,
        default="configs/cifar10_im100.yaml",
        type=str,
    )
    parser.add_argument(
        "--gpus",
        help="decide which gpus to use",
        required=True,
        default='0',
        type=str,
    )
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )

    args = parser.parse_args()
    return args

def valid_model(dataLoader, model, cfg, device, num_classes):
    result_list = []
    pbar = tqdm(total=len(dataLoader))
    model.eval()
    top1_count, top2_count, top3_count, index, fusion_matrix = (
        [],
        [],
        [],
        0,
        FusionMatrix(num_classes),
    )

    func = torch.nn.Sigmoid() \
        if cfg.LOSS.LOSS_TYPE in ['FocalLoss', 'ClassBalanceFocal'] else \
        torch.nn.Softmax(dim=1)
##############################################################################################

    path = 'dataset/crc/data3/test'
    data_file = natsort.natsorted(os.listdir(path))
    data_name = data_file
    data_len = np.array([len(os.listdir(os.path.join(path, dirs)))for dirs in data_name])
    data_idx = [i for i in range(len(data_file))]
    data_dict = dict(zip(data_idx, data_name))
    sd = {key : value for value, key in sorted(data_dict.items(), key = lambda item: item[1], reverse=True)}
    sdk = list(sd.keys())
    head, tail = [], []
    
    for i, key in enumerate(sdk):
        if sd[key] >= 100:
            head.append(key)
        else:
            tail = sdk[i:]        
            break
    y_pred, y_true, tail_pred, tail_true, head_true, head_pred = [], [], [], [], [], []
    
##############################################################################################
    with torch.no_grad():
        for i, (image, image_labels, meta) in enumerate(dataLoader):
            image = image.to(device)
            output = model(image)
            result = func(output)
            _, top_k = result.topk(5, 1, True, True)
            score_result = result.cpu().numpy()

            fusion_matrix.update(score_result.argmax(axis=1), image_labels.numpy())
            topk_result = top_k.cpu().tolist()
            if not "image_id" in meta:
                meta["image_id"] = [0] * image.shape[0]
            image_ids = meta["image_id"]
            # for num, label in enumerate(list(image_labels.numpy())):
            #     label = int(label)
            #     y_true[label].append(list(score_result.argmax(axis=1))[num])
            for i, lbe in enumerate(list(image_labels.numpy())):
                if data_dict[lbe] in head:
                    head_true.append(lbe)
                    head_pred.append(list(score_result.argmax(axis=1))[i])
                else:
                    tail_true.append(lbe)
                    tail_pred.append(list(score_result.argmax(axis=1))[i])
                    
            y_pred = y_pred + list(score_result.argmax(axis=1))
            y_true = y_true + list(image_labels.numpy())
            
            for i, image_id in enumerate(image_ids):
                result_list.append(
                    {
                        "image_id": image_id,
                        "image_label": int(image_labels[i]),
                        "top_3": topk_result[i],
                    }
                )
                top1_count += [topk_result[i][0] == image_labels[i]]
                top2_count += [image_labels[i] in topk_result[i][0:2]]
                top3_count += [image_labels[i] in topk_result[i][0:3]]
                index += 1
            now_acc = np.sum(top1_count) / index
            pbar.set_description("Now Top1:{:>5.2f}%".format(now_acc * 100))
            pbar.update(1)
    top1_acc = float(np.sum(top1_count) / len(top1_count))
    top2_acc = float(np.sum(top2_count) / len(top1_count))
    top3_acc = float(np.sum(top3_count) / len(top1_count))
    print(
        "Top1:{:>5.2f}%  Top2:{:>5.2f}%  Top3:{:>5.2f}%".format(
            top1_acc * 100, top2_acc * 100, top3_acc * 100
        )
    )
    pbar.close()
    # print("F1-score :", f1_score(y_true, y_pred, average=None))
    print('\nhead')
    print("F1-score(micro) :", f1_score(head_true, head_pred, average='micro'))
    print("F1-score(macro) :", f1_score(head_true, head_pred, average='macro'))
    print("F1-score(weighted) :", f1_score(head_true, head_pred, average='weighted'))
    print('\ntail')
    print("F1-score(micro) :", f1_score(tail_true, tail_pred, average='micro'))
    print("F1-score(macro) :", f1_score(tail_true, tail_pred, average='macro'))
    print("F1-score(weighted) :", f1_score(tail_true, tail_pred, average='weighted'))
    print('\nwhole F1-score')
    print("F1-score(micro) :", f1_score(y_true, y_pred, average='micro'))
    print("F1-score(macro) :", f1_score(y_true, y_pred, average='macro'))
    print("F1-score(weighted) :", f1_score(y_true, y_pred, average='weighted'))
    # accuracy_per_classes = []
    # value_sort = dict(sorted(y_true.items(), key=lambda x : len(x[1]), reverse=True))
    
    # for label in value_sort:
    #     accuracy_per_classes.append(value_sort[label].count(label)/len(value_sort[label]))

    # with open(file='apcr.pickle', mode='wb') as f:
    #     pickle.dump(accuracy_per_classes, f)

    # with open(file='value_sort.pickle', mode='wb') as f:
    #     pickle.dump(value_sort, f)
    
    # fig = fusion_matrix.plot_confusion_matrix()
    # plt.savefig('confusion_matrix.png')


if __name__ == "__main__":
    args = parse_args()
    update_config(cfg, args)

    os.environ['CUDA_VISIBLE_DEVICES'] = args.gpus

    test_set = eval(cfg.DATASET.DATASET)("valid", cfg)
    num_classes = test_set.get_num_classes()
    device = torch.device("cuda")
    model = Network(cfg, mode="test", num_classes=num_classes)

    model_file = os.path.join(cfg.OUTPUT_DIR, cfg.NAME, 'models', cfg.TEST.MODEL_FILE)
    model.load_model(model_file, tau_norm=cfg.TEST.TAU_NORM.USE_TAU_NORM, tau=cfg.TEST.TAU_NORM.TAU)

    model = torch.nn.DataParallel(model).cuda()

    testLoader = DataLoader(
        test_set,
        batch_size=cfg.TEST.BATCH_SIZE,
        shuffle=False,
        num_workers=cfg.TEST.NUM_WORKERS,
        pin_memory=cfg.PIN_MEMORY,
    )
    valid_model(testLoader, model, cfg, device, num_classes)
