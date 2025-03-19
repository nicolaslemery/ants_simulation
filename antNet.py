import torch
import torch.nn as nn

class AntNet(nn.Module):
    def __init__(self, input_size=5, hidden_size=16, output_size=4):
        super(AntNet, self).__init__()
        self.fc1 = nn.Linear(input_size, hidden_size)
        self.relu = nn.ReLU()
        self.fc2 = nn.Linear(hidden_size, output_size)
    
    def forward(self, x):
        out = self.fc1(x)
        out = self.relu(out)
        out = self.fc2(out)
        return out
