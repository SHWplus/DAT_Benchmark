import torch
import torch as th
import torch.nn as nn
import torchvision.models as models
from torchvision import transforms
import gymnasium
import numpy as np

class CustomCNN(nn.Module):
    """
    :param observation_space: (gym.Space)
    :param features_dim: (int) Number of features extracted.
        This corresponds to the number of unit for the last layer.
        file originale messo nei modelli di Sistema unreal
    """

    def __init__(self, observation_space: gymnasium.spaces.Box, features_dim: int = 512):
        super(CustomCNN, self).__init__()
        # We assume CxHxW images (channels first)
        # Re-ordering will be done by pre-preprocessing or wrapper

        ''' Resnet18 da pytorch '''
        resnet18 = models.resnet18(pretrained=True)
        self.resnet = th.nn.Sequential(*(list(resnet18.children()))[:-1])
        for param in self.resnet.parameters():
            param.requires_grad = True

        # get device
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.preprocess = transforms.Compose([
            transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
        ])

        # Compute shape by doing one forward pass
        with th.no_grad():
            dims = self.resnet(
                th.as_tensor(np.zeros(observation_space.shape)).float()
            ).shape

            self.n_flatten = int(np.prod(dims))

        self.linear = nn.Sequential(nn.Flatten(), nn.Linear(self.n_flatten, features_dim), nn.ReLU())

    def forward(self, observations: np.ndarray) -> th.Tensor:
        # Preprocess
        # t = time.time()
        observations = th.tensor(observations).to(self.device) # ndarray2tensor
        input_batch = self.preprocess(observations)
        if input_batch.dim() == 4:  # expand dim=0 when test mode
            input_batch = input_batch.unsqueeze(0)
        b, s, c, w, h = input_batch.shape
        x0 = input_batch.view(-1, c, w, h)

        x1 = self.resnet(x0)
        x1 = x1.view(b, s, -1)
        x2 = torch.flatten(x1, start_dim=1)
        x3 = self.linear(x2)
        # print("Time: ", time.time() - t, observations.shape)
        return x3