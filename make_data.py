import argparse
import shutil
import natsort
import os

parser = argparse.ArgumentParser()
parser.add_argument('--bp', default='word_data', type=str)
parser.add_argument('--cp', default='data')
parser.add_argument('--c', default=3, type=int)
parser.add_argument('--dr', default=[6, 3, 1], type=list)
args = parser.parse_args()

base_pth = args.bp+'/'
copy_pth = args.cp+'/'
data_file = natsort.natsorted(os.listdir(base_pth))
cnst = args.c
data_rate = list(map(lambda x : x/10, args.dr))

for i in data_file:

    dir1 = base_pth + i
    data_list = os.listdir(dir1)
    file_len = len(data_list)
    if file_len >= cnst:
        test = 1 if round(file_len*data_rate[1]) == 0 else round(file_len*data_rate[1])
        val = 1 if round(file_len*data_rate[2]) == 0 else round(file_len*data_rate[2])
        train = file_len - (test+val)

        train_data = data_list[:train]
        test_data = data_list[train:train+test]
        val_data = data_list[-val:]
        
        dirs = [copy_pth+'train/'+i,
            copy_pth+'test/'+i,
            copy_pth+'validation/'+i
        ]

        for dir_path in dirs:
            if not os.path.isdir(dir_path):
                os.mkdir(dir_path)

        for data in train_data:
            dir2 = dir1+'/'+data
            dir3 = dirs[0]+'/'+data
            shutil.copy(dir2,dir3)

        for data in test_data:
            dir2 = dir1+'/'+data
            dir3 = dirs[1]+'/'+data
            shutil.copy(dir2,dir3)

        for data in val_data:
            dir2 = dir1+'/'+data
            dir3 = dirs[2]+'/'+data
            shutil.copy(dir2,dir3)