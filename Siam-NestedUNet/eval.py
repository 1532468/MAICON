import torch.utils.data
from utils.parser import get_parser_with_args
from utils.helpers import get_test_loaders
from tqdm import tqdm
from sklearn.metrics import confusion_matrix

# The Evaluation Methods in our paper are slightly different from this file.
# In our paper, we use the evaluation methods in train.py. specifically, batch size is considered.
# And the evaluation methods in this file usually produce higher numerical indicators.

if __name__ == '__main__' :
    parser, metadata = get_parser_with_args()
    opt = parser.parse_args()

    dev = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

    test_loader = get_test_loaders(opt)

    path = 'tmp/checkpoint_epoch_9.pt'   # the path of the model
    model = torch.load(path)

    c_matrix = {'tn': 0, 'fp': 0, 'fn': 0, 'tp': 0}
    model.eval()


    with torch.no_grad():
        tbar = tqdm(test_loader)
        for batch_img1, batch_img2, labels in tbar:

            batch_img1 = batch_img1.float().to(dev)
            batch_img2 = batch_img2.float().to(dev)
            labels = labels.long().to(dev)

            # print("...디버깅중...")
            # print(batch_img1.size())
            # print(batch_img2.size())
            # print(labels.size())

            cd_preds = model(batch_img1, batch_img2)
            cd_preds = cd_preds[-1]
            _, cd_preds = torch.max(cd_preds, 1)
            # print(cd_preds.size())

            # print("...디버깅중...")
            # print(labels.data.cpu().numpy().flatten().shape)
            # print(cd_preds.data.cpu().numpy().flatten().shape)

            tn, fp, fn, tp = confusion_matrix(labels.data.cpu().numpy().flatten(),
                            cd_preds.data.cpu().numpy().flatten()).ravel()

            c_matrix['tn'] += tn
            c_matrix['fp'] += fp
            c_matrix['fn'] += fn
            c_matrix['tp'] += tp

    tn, fp, fn, tp = c_matrix['tn'], c_matrix['fp'], c_matrix['fn'], c_matrix['tp']
    P = tp / (tp + fp)
    R = tp / (tp + fn)
    F1 = 2 * P * R / (R + P)
    IoU = tp / (tp + fp + fn)

    print('Precision: {}\nRecall: {}\nF1-Score: {}\nIoU: {}'.format(P, R, F1,IoU))
