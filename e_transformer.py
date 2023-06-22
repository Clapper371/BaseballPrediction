import torch
from torch.utils.data import Dataset, DataLoader
from sklearn.preprocessing import StandardScaler
from c2 import load_data
import pandas as pd
import numpy as np

# 1. 데이터 불러오기
# 2. 트랜스포머 모델에 넣을 수 있는 형태로 편집
# 2-1. 맞붙는 팀, 그 팀의 선수들에 대한 정보만 넣기
# 2-2. 
# 3. 트랜스포머 모델에 넣고 돌리기
# 4. 나온 결과를 실제 결과와 비교하고 데이터 프레임에 맞춰서 출력/내보내기

# Define a custom dataset class
class MyDataset(Dataset):
    def __init__(self, features, labels):
        self.features = features
        self.labels = labels

    def __len__(self):
        return len(self.features)

    def __getitem__(self, index):
        x = torch.tensor(self.features[index], dtype=torch.float32)
        y = torch.tensor(self.labels[index], dtype=torch.long)
        return x, y

# pd.set_option('display.max_rows', None)  # 모든 행 출력
# pd.set_option('display.max_columns', None)  # 모든 열 출력
# np.set_printoptions(threshold=np.inf)

# Load the data
(train_x, train_y), (test_x, test_y, k_test_df) = load_data()
print('train_x')
print(train_x)
print('train_y')
print(train_y)
print('test_x')
print(test_x)
print('test_y')
print(test_y)
print('k_test_df')
print(k_test_df)

# np.savetxt('check_train_x.csv', train_x, delimiter=',', fmt='%d')
# np.savetxt('check_train_y.csv', train_y, delimiter=',', fmt='%d')
# np.savetxt('check_test_x.csv', test_x, delimiter=',', fmt='%d')
# np.savetxt('check_test_y.csv', test_y, delimiter=',', fmt='%d')
k_test_df.to_csv('check_k_test_df.csv', encoding='ms949')

result_df = pd.DataFrame(columns=['날짜', 'home team', 'away team', 'home team 승리 확률', 'away team 승리 확률', '예측 승리 팀', '실제 승리 팀', '적중 여부'])

# Preprocess the data
scaler = StandardScaler()
train_x = scaler.fit_transform(train_x)
test_x = scaler.transform(test_x)

# Create dataset objects
train_dataset = MyDataset(train_x, train_y)
test_dataset = MyDataset(test_x, test_y)

# Create data loaders
batch_size = 32
train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True)
test_loader = DataLoader(test_dataset, batch_size=batch_size)

# Example usage of data loaders in a training loop
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# Define your transformer model and other necessary components

num_epochs = 50

for epoch in range(num_epochs):
    # Training loop
    for batch_x, batch_y in train_loader:
        batch_x = batch_x.to(device)
        batch_y = batch_y.to(device)

        # Forward pass, backward pass, optimization, etc.

    # Validation loop
    with torch.no_grad():
        for batch_x, batch_y in test_loader:
            batch_x = batch_x.to(device)
            batch_y = batch_y.to(device)

            # Forward pass and calculate metrics

    # Rest of the training loop
    print('number: ', epoch)

print(batch_x)
print(batch_y)
