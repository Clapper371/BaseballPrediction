import torch
import torch.nn as nn
import tensorflow as tf
import numpy as np
import pandas as pd

TRAIN_URL = 'transformed_lstm_train_data.csv'
TEST_URL = 'transformed_lstm_test_data.csv'

class TransformerModel(nn.Module):
    def __init__(self, input_size, output_size):
        super(TransformerModel, self).__init__()
        
        # 입력, 출력 크기 설정
        self.input_size = input_size
        self.output_size = output_size
        
        # Transformer 레이어 구성 요소 설정
        self.embedding = nn.Embedding(input_size, 128)
        self.transformer = nn.Transformer(128, num_encoder_layers=6, num_decoder_layers=6)
        self.fc = nn.Linear(128, output_size)
    
    def forward(self, input_data):
        # 입력 데이터 임베딩
        embedded_data = self.embedding(input_data)
        
        # Transformer 모델 적용
        output = self.transformer(embedded_data, embedded_data)
        
        # 출력 레이어 적용
        output = self.fc(output[:, 27:595, :])
        
        return output.squeeze()

# 모델 인스턴스 생성
model = TransformerModel(input_size=3, output_size=1)

train_path, test_path = TRAIN_URL, TEST_URL

targets = []
for index in range(10):
    targets.append('win_' + str(index))
train = pd.read_csv(train_path)
train_y = train.pop(targets[0])
for target in targets[1:]:
    train_y = pd.concat((train_y, train.pop(target)), axis=1)
train_x = train

test = pd.read_csv(test_path)
test_y = test.pop(targets[0])
for target in targets[1:]:
    test_y = pd.concat((test_y, test.pop(target)), axis=1)
test_x = test



# 입력 데이터 생성 (예시)
input_data = torch.tensor([[0, 1, 0.5, ...], [0.5, 0, 1, ...], ...])  # shape: (배치 크기, 시퀀스 길이)

# 모델에 입력 데이터 전달
output = model(input_data)

# 결과 출력
print(output)
