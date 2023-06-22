import torch
import torch.nn as nn
from torch.nn.utils.rnn import pad_sequence

# Transformer 모델을 정의하는 클래스
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

# 예시로 사용할 입력 데이터
input_data = [
    [1, 2, 3, 4],
    [4, 3, 2],
    [2, 1, 3, 4, 5]
]

# 입력 데이터를 텐서로 변환하고 패딩
padded_input = pad_sequence([torch.tensor(ids) for ids in input_data], batch_first=True)

# TransformerModel 모델 초기화
num_classes = 2  # 분류할 클래스 수
model = TransformerModel(num_classes)

# 모델 추론
model.eval()
with torch.no_grad():
    logits = model(padded_input)
    predictions = torch.argmax(logits, dim=1)

# 예측 결과 출력
print(f'Predictions: {predictions}')
