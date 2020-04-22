import memtorch
import torch
import torch.nn as nn
import torch.functional as F
import numpy as np
from sklearn import datasets, linear_model
from sklearn.metrics import r2_score


def naive_tune(module, input_shape):
    """Method to determine a linear relationship between a memristive crossbar and the output for a given memristive module.

        Parameters
        ----------
        module : torch.nn.Module
            Memristive layer to tune.
        input_shape : tuple
            Shape of the randomly generated input used to tune a crossbar.

        Returns
        -------
        function
            Function which transforms the output of the crossbar to the expected output.
    """
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    tmp = module.bias
    module.bias = None
    input = torch.rand(input_shape).uniform_(-1, 1).to(device)
    output = module.forward(input).detach().cpu().flatten()
    legacy_output = module.forward_legacy(input).detach().cpu().flatten()
    output = output.numpy().reshape(-1, 1)
    legacy_output = legacy_output.numpy()
    reg = linear_model.LinearRegression(fit_intercept=True).fit(output, legacy_output)
    transform_output = lambda x: x * reg.coef_[0] + reg.intercept_
    module.bias = tmp
    print('Tuned %s. Coefficient of determination: %f [%f, %f]' % (module, reg.score(output, legacy_output), reg.coef_[0], reg.intercept_))
    return transform_output
