import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader
import numpy as np

# 사용자 정의 Dataset 클래스 생성
class CustomDataset(Dataset):
    def __init__(self, data):
        self.data = data
        
    def __len__(self):
        return len(self.data)
    
    def __getitem__(self, idx):
        sample = self.data.iloc[idx]
        
        return sample
    
class TransformerModel(nn.Module):
    def __init__(self, num_classes):
        super(TransformerModel, self).__init__()
        self.embedding = nn.Embedding(num_embeddings=10000, embedding_dim=128)
        self.transformer_layer = nn.TransformerEncoderLayer(
            d_model=128, nhead=8, dim_feedforward=256
        )
        self.transformer = nn.TransformerEncoder(self.transformer_layer, num_layers=6)
        self.fc = nn.Linear(128, num_classes)

    def forward(self, input_ids):
        embedded = self.embedding(input_ids)
        embedded = embedded.permute(1, 0, 2)
        transformer_output = self.transformer(embedded)
        pooled_output = transformer_output.mean(dim=0)
        logits = self.fc(pooled_output)
        return logits

# CSV 파일 경로
test_data = 'transformed_lstm_test_data.csv'
test_data_k = 'transformed_lstm_test_data_k.csv'
train_data = 'transformed_lstm_train_data.csv'
train_data_k = 'transformed_lstm_train_data_k.csv'

all_train_data = pd.read_csv(train_data_k)
all_test_data = pd.read_csv(test_data_k)

team_name = ['키움', '두산', 'KIA', 'KT', 'NC', 'SSG', 'LG', '롯데', '한화', '삼성']

datasets_train = []
datasets_test = []
for i in range(10):
    selected_columns_train = [all_train_data.columns[0]] + [col for col in all_train_data.columns if col.startswith(team_name[i])]
    selected_columns_train = selected_columns_train[:-3]
    new_dataset_train = all_train_data[selected_columns_train]
    selected_columns_test = [all_test_data.columns[0]] + [col for col in all_test_data.columns if col.startswith(team_name[i])]
    selected_columns_test = selected_columns_test[:-3]
    new_dataset_test = all_test_data[selected_columns_test]
    # print(new_dataset_train)
    # print(new_dataset_test)

    globals()[f"new_dataset_train_{team_name[i]}"] = new_dataset_train
    globals()[f"new_dataset_test_{team_name[i]}"] = new_dataset_test

    dataset_train = CustomDataset(new_dataset_train)
    dataset_test = CustomDataset(new_dataset_test)

    datasets_train.append(dataset_train)
    datasets_test.append(dataset_test)
    
# print(datasets_train[7].data)
# print(datasets_test[3].data)

# new_df 이름으로 경기 결과 표시 생성
all_train_data = all_train_data[all_train_data['only_starter'] != 1].reset_index(drop=True)
new_df_train = pd.DataFrame(np.full((len(all_train_data), 10), -1), columns=team_name)
for index, row in all_train_data.iterrows():
    home_score = row['home_score']
    away_score = row['away_score']
    home_team = row['home team']
    away_team = row['away team']
    if home_score > away_score:
        new_df_train.at[index, home_team] = 1
        new_df_train.at[index, away_team] = 0
    elif home_score < away_score:
        new_df_train.at[index, home_team] = 0
        new_df_train.at[index, away_team] = 1
    else:
        new_df_train.at[index, home_team] = 0
        new_df_train.at[index, away_team] = 0
print(new_df_train)
all_test_data = all_test_data[all_test_data['only_starter'] != 1].reset_index(drop=True)
new_df_test = pd.DataFrame(np.full((len(all_test_data), 10), -1), columns=team_name)
for index, row in all_test_data.iterrows():
    home_score = row['home_score']
    away_score = row['away_score']
    home_team = row['home team']
    away_team = row['away team']
    if home_score > away_score:
        new_df_test.at[index, home_team] = 1
        new_df_test.at[index, away_team] = 0
    elif home_score < away_score:
        new_df_test.at[index, home_team] = 0
        new_df_test.at[index, away_team] = 1
    else:
        new_df_test.at[index, home_team] = 0
        new_df_test.at[index, away_team] = 0
print(new_df_test)

batch_size = 64
dataloader_train = DataLoader(dataset_train, batch_size=batch_size, shuffle=True)
dataloader_test = DataLoader(dataset_test, batch_size=batch_size, shuffle=False)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

dataset_train_1 = CustomDataset(all_train_data)
dataset_test_1 = CustomDataset(all_test_data)
dataloader_train_1 = DataLoader(dataset_train_1, batch_size=batch_size, shuffle=True)
dataloader_test_1 = DataLoader(dataset_test_1, batch_size=batch_size, shuffle=False)



# 한 행마다 어떤 팀 간의 경기인지 확인
# 승, 패 정보 불러와서 [입력 값 - 선수 정보, 출력 값 - 승, 패]로 학습시키기
# 

# # DataLoader 생성
# batch_size = 64
# dataloader = DataLoader(dataset_test, batch_size=batch_size, shuffle=True)

# print(dataloader.__dict__)

# # 데이터 사용 예시
# for batch in dataloader:
#     # batch는 입력 데이터의 배치를 나타냅니다.
#     inputs = batch
#     # inputs를 사용하여 모델 학습 또는 예측 수행