import pandas as pd
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import Dataset, DataLoader, TensorDataset
import numpy as np
import math

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# CSV 파일 경로
test_data = 'transformed_lstm_test_data_tf.csv'
test_data_k = 'transformed_lstm_test_data_k_tf.csv'
train_data = 'transformed_lstm_train_data_tf.csv'
train_data_k = 'transformed_lstm_train_data_k_tf.csv'

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

    # globals()[f"new_dataset_train_{team_name[i]}"] = new_dataset_train
    # globals()[f"new_dataset_test_{team_name[i]}"] = new_dataset_test

    # dataset_train = CustomDataset(new_dataset_train)
    # dataset_test = CustomDataset(new_dataset_test)

    datasets_train.append(new_dataset_train)
    datasets_test.append(new_dataset_test)
    
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

new_df_train_np = new_df_train.to_numpy()
new_df_train_y = torch.tensor(new_df_train_np, dtype=torch.float32)
new_df_test_np = new_df_test.to_numpy()
new_df_test_y = torch.tensor(new_df_test_np, dtype=torch.float32)

batch_size = 32
# dataloader_train = DataLoader(dataset_train, batch_size=batch_size, shuffle=True)
# dataloader_test = DataLoader(dataset_test, batch_size=batch_size, shuffle=False)


# columns_to_keep = [all_train_data.columns[0]] + [col for col in all_train_data.columns if any(col.startswith(name) for name in team_name)]
# all_train_data_revised = all_train_data[columns_to_keep]
# print(all_train_data_revised.columns)
# input_train_x = torch.tensor(all_train_data_revised.values, dtype=torch.float32)
# print(input_train_x)
# columns_to_keep = [all_test_data.columns[0]] + [col for col in all_test_data.columns if any(col.startswith(name) for name in team_name)]
# all_test_data_revised = all_test_data[columns_to_keep]
# print(all_test_data_revised.columns)
# input_test_x = torch.tensor(all_test_data_revised.values, dtype=torch.float32)
# print(input_test_x)

columns_to_keep = [col for col in all_train_data.columns if any(col.startswith(name) for name in team_name)]
all_train_data_revised = all_train_data[columns_to_keep]
print(all_train_data_revised.columns)
input_train_x = torch.tensor(all_train_data_revised.values, dtype=torch.float32)
print(input_train_x)
columns_to_keep = [col for col in all_test_data.columns if any(col.startswith(name) for name in team_name)]
all_test_data_revised = all_test_data[columns_to_keep]
print(all_test_data_revised.columns)
input_test_x = torch.tensor(all_test_data_revised.values, dtype=torch.float32)
print(input_test_x)

print("input_train_x shape:", input_train_x.shape)
print("new_df_train_y shape:", new_df_train_y.shape)
print("input_test_x shape:", input_test_x.shape)
print("new_df_test_y shape:", new_df_test_y.shape)

#==preprocessing done==#
class KBO_Dataset(Dataset):
    def __init__(self, input, label):
        self.x = input
        self.y = label
        
    def __len__(self):
        return len(self.x)
    
    def __getitem__(self, idx):
        device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        return torch.tensor(self.x[idx]).to(device),torch.tensor(self.y[idx]).to(device)


train_dataset = KBO_Dataset(input_train_x,new_df_train_y)
test_dataset = KBO_Dataset(input_test_x,new_df_test_y)

# dataset_train_1 = TensorDataset(input_train_x, new_df_train_y)
# dataset_test_1 = TensorDataset(input_test_x, new_df_test_y)
# dataloader_train_1 = DataLoader(dataset_train_1, batch_size=batch_size, shuffle=True)
# dataloader_test_1 = DataLoader(dataset_test_1, batch_size=batch_size, shuffle=False)

train_dataloader = DataLoader(train_dataset,batch_size=batch_size)
test_dataloader = DataLoader(test_dataset,batch_size=batch_size)

# print(dataloader_train_1)


class TransformerModel(nn.Module):
    def __init__(self, input_dim, output_dim, hidden_dim=598, nhead=2, num_layers=8):
        super(TransformerModel, self).__init__()
        self.transformer = nn.Transformer(
            d_model=hidden_dim,  # 수정된 부분
            nhead=nhead,
            num_encoder_layers=num_layers,
            num_decoder_layers=num_layers
        )
        self.fc = nn.Linear(hidden_dim, output_dim)

    def forward(self, x):
        x = self.transformer(x, x)
        x = self.fc(x)
        return x
    
# 모델 및 손실 함수, 옵티마이저 정의
model = TransformerModel(input_dim=598, output_dim=10)
criterion = nn.MSELoss()
optimizer = optim.Adam(model.parameters(), lr=0.001)

# 모델 학습
num_epochs = 100
for epoch in range(num_epochs):
    total_loss = 0
    for batch_x, batch_y in train_dataloader:
        optimizer.zero_grad()
        outputs = model(batch_x)
        loss = criterion(outputs, batch_y)
        loss.backward()
        optimizer.step()
        total_loss += loss.item()
    print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {total_loss:.4f}")

# # 학습된 모델 저장
# torch.save(model.state_dict(), "transformer_model.pth")

# model.load_state_dict(torch.load("transformer_model.pth"))
# model.eval()

# # # 평가 시작
# # with torch.no_grad():
# #     test_outputs = model(input_test_x)
# #     test_loss = criterion(test_outputs, new_df_test_y)
# #     print(f"Test Loss: {test_loss:.4f}")

correct = 0
total = 0

# # torch.set_printoptions(threshold=torch.inf, precision=6, linewidth=200)
# torch.set_printoptions(precision=6, linewidth=200)
# # 평가 시작
# with torch.no_grad():
#     for batch_x, batch_y in test_dataloader:
#         test_outputs = model(batch_x)

#         print(batch_x)
#         print(batch_x.size())
#         print(test_outputs)
#         print(test_outputs.size())
#         # 예측값 후처리 (분류 문제인 경우)
#         predicted_labels = test_outputs.argmax(dim=1)
#         print(predicted_labels)
#         print(batch_y.argmax(dim=1))

#         # 정확도 계산
#         total += batch_y.size(0)  # 배치 내 샘플 수 추가
#         correct += (predicted_labels == batch_y.argmax(dim=1)).sum().item()

# accuracy = correct / total
# print(f"Test Accuracy: {accuracy * 100:.4f}%")


with torch.no_grad():
    for batch_x, batch_y in test_dataloader:
        for i in range(batch_x.size(0)):  # 각 행마다 따로 처리
            input_x = batch_x[i:i+1]
            target_y = batch_y[i:i+1]

            test_outputs = model(input_x)

            zero_or_one_indices = torch.where((target_y == 0) | (target_y == 1))[1]
            t1 = zero_or_one_indices[0].item()
            t2 = zero_or_one_indices[1].item()
            print(t1, t2)

            if test_outputs[0, t1] > test_outputs[0, t2]:
                predicted_label = torch.tensor(t1)
            else:
                predicted_label = torch.tensor(t2)

            true_label = target_y.argmax(dim=1)
            print('Number:', i+1)
            print(len(test_outputs))
            print(test_outputs)
            print(predicted_label)
            print(target_y)
            print(true_label)
            
            print(zero_or_one_indices)

            total += 1
            correct += (predicted_label == true_label).item()

accuracy = correct / total
print("Correct: ", correct, "/ Total: ", total)
print(f"Test Accuracy: {accuracy * 100:.4f}%")



# 데이터 생성 및 전처리
# 실제 데이터를 사용해야 합니다.
# batch_size = 32
# input_data = torch.randn(batch_size, 599)  # 실제 데이터로 대체
# labels = torch.randint(output_size, (batch_size,))
# input_size = 598
# output_size = 10
# model = TransformerEncoderModel(input_size, output_size)

# # 손실 함수 및 옵티마이저 설정
# criterion = nn.BCEWithLogitsLoss()

# optimizer = optim.Adam(model.parameters(), lr=0.001)

# c = 0
# # 모델 학습
# num_epochs = 10
# for epoch in range(num_epochs):
#     total_loss = 0
#     for inputs, targets in train_dataloader:
#         optimizer.zero_grad()
#         outputs = model(inputs)
#         sigmoid_outputs = torch.sigmoid(outputs)
#         loss = criterion(sigmoid_outputs, targets)
#         loss.backward()
#         optimizer.step()
#         total_loss += loss.item()
#         c = c + 1
#         print(c)
#         print(inputs)
#         print(targets)

#     avg_loss = total_loss / len(train_dataloader)
#     print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")

# # 모델 평가
# model.eval()  # 모델을 평가 모드로 설정
# with torch.no_grad():
#     total_correct = 0
#     total_samples = 0
#     for inputs, targets in test_dataloader:
#         outputs = model(inputs)
#         sigmoid_outputs = torch.sigmoid(outputs)  # 확률값으로 변환
#         predicted_labels = (sigmoid_outputs > 0.5).float()  # 확률값을 임계치 0.5 기준으로 이진 레이블로 변환
#         correct_predictions = (predicted_labels == targets).float()
#         total_correct += correct_predictions.sum().item()
#         total_samples += targets.size(0)
#     print(total_samples)
#     print(total_correct)
#     accuracy = total_correct / total_samples
#     print(f"Test Accuracy: {accuracy:.4f}")



# # Initialize your model, criterion, and optimizer
# model = TransformerEncoderModel(input_size=598, output_size=10)
# criterion = nn.CrossEntropyLoss()
# optimizer = optim.Adam(model.parameters(), lr=0.001)

# num_epochs = 10
# for epoch in range(num_epochs):
#     total_loss = 0
#     for inputs, targets in train_dataloader:
#         optimizer.zero_grad()
#         outputs = model(inputs)
#         loss = criterion(outputs, targets)
#         loss.backward()
#         optimizer.step()
#         total_loss += loss.item()

#     avg_loss = total_loss / len(train_dataloader)
#     print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")

# correct_predictions = 0
# total_samples = 0

# model.eval()

# with torch.no_grad():
#     for inputs, targets in test_dataloader:
#         outputs = model(inputs)
#         _, predicted = torch.max(outputs, dim=1)
#         total_samples += targets.size(0)
#         correct_predictions += (predicted == targets).sum().item()

# accuracy = correct_predictions / total_samples
# print(f"Test Accuracy: {accuracy * 100:.2f}%")


# model = TransformerModel(input_size=512, output_size=10)
# criterion = nn.CrossEntropyLoss()
# optimizer = optim.Adam(model.parameters(), lr=0.001)

# num_epochs = 10
# for epoch in range(num_epochs):
#     total_loss = 0
#     for inputs, targets in dataloader_train_1:
#         optimizer.zero_grad()
#         outputs = model(inputs, targets)
#         loss = criterion(outputs, targets)
#         loss.backward()
#         optimizer.step()
#         total_loss += loss.item()

#     avg_loss = total_loss / len(dataloader_train_1)
#     print(f"Epoch [{epoch+1}/{num_epochs}], Loss: {avg_loss:.4f}")

# for epoch in range(num_epochs):
#     model.eval()
#     with torch.no_grad():
#         logits = model(inputs, targets)